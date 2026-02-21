"""
SentientMarket — Reputation Engine
Combines MemSync memories + OG forecasts + accuracy data to produce
TEE-verified reputation scores for each digital twin.
"""

from __future__ import annotations
import json
import time
from typing import Optional

from og_client import OGClient
from memsync_client import MemSyncClient
from twin_collector import TwinCollector


class AccuracyTracker:
    """Tracks prediction accuracy for twins with rolling windows."""

    @staticmethod
    def calculate_accuracy(predictions: list[dict]) -> dict:
        """
        Calculate accuracy metrics from resolved predictions.
        Returns { accuracy_pct, total, hits, misses, by_asset, by_direction }
        """
        resolved = [p for p in predictions if p.get("outcome") in ("hit", "miss")]
        if not resolved:
            return {"accuracy_pct": 0, "total": 0, "hits": 0, "misses": 0, "by_asset": {}, "by_direction": {}}

        hits = sum(1 for p in resolved if p["outcome"] == "hit")
        misses = len(resolved) - hits
        accuracy = round((hits / len(resolved)) * 100, 1)

        # Breakdown by asset
        by_asset = {}
        for p in resolved:
            asset = p["asset"]
            if asset not in by_asset:
                by_asset[asset] = {"hits": 0, "misses": 0, "total": 0}
            by_asset[asset]["total"] += 1
            by_asset[asset]["hits" if p["outcome"] == "hit" else "misses"] += 1

        for asset in by_asset:
            a = by_asset[asset]
            a["accuracy_pct"] = round((a["hits"] / a["total"]) * 100, 1) if a["total"] > 0 else 0

        # Breakdown by direction
        by_direction = {"long": {"hits": 0, "misses": 0, "total": 0}, "short": {"hits": 0, "misses": 0, "total": 0}}
        for p in resolved:
            d = p.get("direction", "long")
            by_direction[d]["total"] += 1
            by_direction[d]["hits" if p["outcome"] == "hit" else "misses"] += 1

        for d in by_direction:
            bd = by_direction[d]
            bd["accuracy_pct"] = round((bd["hits"] / bd["total"]) * 100, 1) if bd["total"] > 0 else 0

        return {
            "accuracy_pct": accuracy,
            "total": len(resolved),
            "hits": hits,
            "misses": misses,
            "by_asset": by_asset,
            "by_direction": by_direction,
        }


class MemoryPipeline:
    """Processes twin data into MemSync memories."""

    def __init__(self, memsync: MemSyncClient):
        self.memsync = memsync

    def ingest_twin(self, twin: dict) -> int:
        """
        Ingest a twin's predictions into MemSync as memories.
        Returns count of memories stored.
        """
        name = twin["name"]
        count = 0

        # Store bio as a semantic memory
        self.memsync.store_memory(
            twin_name=name,
            action_text=f"Twin profile: {name}",
            twin_response=f"Bio: {twin.get('bio', 'No bio')}. Avatar: {twin.get('avatar', '')}",
            source="document",
        )
        count += 1

        # Store each prediction as an episodic memory
        for pred in twin.get("predictions", []):
            direction = pred.get("direction", "unknown")
            asset = pred.get("asset", "?")
            price = pred.get("price_at_call", 0)
            target = pred.get("target", 0)
            outcome = pred.get("outcome", "pending")
            actual = pred.get("actual_price")

            action = f"Called {asset} {direction} at ${price:,.2f}, target ${target:,.2f}"
            if outcome == "pending":
                response = "Prediction pending — awaiting outcome."
            elif outcome == "hit":
                response = f"✅ HIT — {asset} reached ${actual:,.2f} (target was ${target:,.2f})"
            else:
                response = f"❌ MISS — {asset} went to ${actual:,.2f} instead of target ${target:,.2f}"

            self.memsync.store_memory(
                twin_name=name,
                action_text=action,
                twin_response=response,
            )
            count += 1

        return count

    def get_memory_context(self, twin_name: str, limit: int = 10) -> str:
        """Build a text context from a twin's memories for LLM analysis."""
        memories = self.memsync.search_memories(
            query=f"{twin_name} predictions accuracy trades",
            twin_name=twin_name,
            limit=limit,
        )

        if not memories:
            return f"No memories found for {twin_name}."

        lines = []
        for m in memories:
            action = m.get("action", m.get("content", ""))
            response = m.get("response", "")
            lines.append(f"- {action}: {response}")

        return "\n".join(lines)


class ReputationEngine:
    """
    Core intelligence engine.
    Combines accuracy tracking, memory context, and TEE-verified LLM analysis
    to produce verifiable reputation scores.
    """

    def __init__(
        self,
        og: OGClient,
        memsync: MemSyncClient,
        collector: TwinCollector,
    ):
        self.og = og
        self.memsync = memsync
        self.collector = collector
        self.pipeline = MemoryPipeline(memsync)
        self.tracker = AccuracyTracker()
        self._cache: dict[str, dict] = {}

    def initialize(self):
        """Ingest all twins into MemSync on startup."""
        twins = self.collector.get_all_twins()
        for twin in twins:
            count = self.pipeline.ingest_twin(twin)
            print(f"[Engine] Ingested {count} memories for {twin['name']}")

    def score_twin(self, twin_id: str, force_refresh: bool = False) -> Optional[dict]:
        """
        Produce a full reputation score for a twin.
        Returns {
            twin, accuracy, forecasts, ai_analysis, payment_hash, 
            explorer_url, scored_at
        }
        """
        if twin_id in self._cache and not force_refresh:
            return self._cache[twin_id]

        twin = self.collector.get_twin(twin_id)
        if not twin:
            return None

        # 1. Calculate accuracy from predictions
        resolved = self.collector.get_resolved_predictions(twin_id)
        accuracy = self.tracker.calculate_accuracy(resolved)

        # 2. Get OG on-chain forecasts for comparison
        forecasts = self.og.get_forecasts()

        # 3. Build memory context
        memory_context = self.pipeline.get_memory_context(twin["name"])

        # 4. Enrich context with accuracy + forecasts
        enriched_context = (
            f"{memory_context}\n\n"
            f"Accuracy stats: {accuracy['accuracy_pct']}% ({accuracy['hits']}/{accuracy['total']})\n"
            f"By asset: {json.dumps(accuracy['by_asset'])}\n"
            f"Current OG model forecasts: {json.dumps({k: v.get('direction', v.get('raw', 'N/A')) for k, v in forecasts.items()})}"
        )

        # 5. TEE-verified LLM analysis
        result = self.og.analyze_twin(twin["name"], enriched_context)

        # Parse the analysis JSON
        try:
            analysis = json.loads(result["analysis"])
        except (json.JSONDecodeError, TypeError):
            analysis = {"narrative": result.get("analysis", "Analysis unavailable"), "accuracy_pct": accuracy["accuracy_pct"]}

        # Build explorer URL for the proof
        payment_hash = result.get("payment_hash", "")
        explorer_url = f"https://explorer.opengradient.ai/tx/{payment_hash}" if payment_hash else None

        score = {
            "twin": twin,
            "accuracy": accuracy,
            "forecasts": forecasts,
            "ai_analysis": analysis,
            "payment_hash": payment_hash,
            "explorer_url": explorer_url,
            "scored_at": int(time.time()),
        }

        self._cache[twin_id] = score
        return score

    def get_leaderboard(self) -> list[dict]:
        """
        Score all twins and return sorted by accuracy.
        Each entry: { twin_id, name, avatar, accuracy_pct, bias, risk_rating, payment_hash }
        """
        twins = self.collector.get_all_twins()
        entries = []

        for twin in twins:
            score = self.score_twin(twin["id"])
            if not score:
                continue

            entries.append({
                "twin_id": twin["id"],
                "name": twin["name"],
                "avatar": twin.get("avatar", ""),
                "bio": twin.get("bio", ""),
                "accuracy_pct": score["accuracy"]["accuracy_pct"],
                "total_calls": score["accuracy"]["total"],
                "hits": score["accuracy"]["hits"],
                "misses": score["accuracy"]["misses"],
                "bias": score["ai_analysis"].get("bias", "unknown"),
                "risk_rating": score["ai_analysis"].get("risk_rating", "unknown"),
                "narrative": score["ai_analysis"].get("narrative", ""),
                "payment_hash": score.get("payment_hash", ""),
                "explorer_url": score.get("explorer_url", ""),
                "scored_at": score.get("scored_at", 0),
            })

        # Sort by accuracy descending
        entries.sort(key=lambda x: x["accuracy_pct"], reverse=True)
        return entries
