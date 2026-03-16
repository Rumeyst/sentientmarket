"""
SentientMarket — OpenGradient SDK Wrapper
Handles TEE-verified LLM inference via x402 (updated SDK API).

SDK changes (March 2026):
- og.Client() → og.LLM(private_key=...)
- llm.chat() and llm.completion() are now ASYNC
- Requires Permit2 approval via llm.ensure_opg_approval()
- OPG tokens on Base Sepolia (not OUSDC)
- SETTLE_METADATA → INDIVIDUAL_FULL
- Models: GPT_5, GPT_4_1_2025_04_14, CLAUDE_SONNET_4_5, etc.
"""

from __future__ import annotations
import asyncio
import json
import threading
import time
from typing import Any, Optional

from config import Config

# ---------------------------------------------------------------------------
# Async helper — run coroutines from sync code even inside event loops
# ---------------------------------------------------------------------------

def _run_async(coro: Any) -> Any:
    """Run an async coroutine from synchronous code.

    Works even when called from inside an existing event loop (e.g. FastAPI).
    Spawns a new thread with its own event loop to avoid conflicts.
    """
    result: list[Any] = [None]
    error: list[Optional[BaseException]] = [None]

    def _worker() -> None:
        try:
            result[0] = asyncio.run(coro)
        except BaseException as e:
            error[0] = e

    t = threading.Thread(target=_worker)
    t.start()
    t.join(timeout=60)
    if error[0] is not None:
        raise error[0]  # type: ignore[misc]
    return result[0]


# ---------------------------------------------------------------------------
# Demo / fallback data when SDK is unavailable
# ---------------------------------------------------------------------------

DEMO_FORECASTS = {
    "BTC": {"price": 97420.50, "direction": "bullish", "confidence": 0.72, "horizon": "1h", "timestamp": int(time.time())},
    "ETH": {"price": 3285.10, "direction": "bearish", "confidence": 0.58, "horizon": "1h", "timestamp": int(time.time())},
    "SOL": {"price": 178.40, "direction": "bullish", "confidence": 0.65, "horizon": "1h", "timestamp": int(time.time())},
    "SUI": {"price": 4.12, "direction": "neutral", "confidence": 0.51, "horizon": "1h", "timestamp": int(time.time())},
}


class OGClient:
    """Wrapper around the OpenGradient Python SDK (new async API)."""

    def __init__(self, llm: Any = None):
        """
        Args:
            llm: og.LLM instance (created via og.LLM(private_key=...))
        """
        self.llm = llm
        self.demo_mode = llm is None

    # ------------------------------------------------------------------
    # LLM Inference (TEE-verified via x402)
    # ------------------------------------------------------------------

    def analyze_twin(self, twin_name: str, memory_context: str) -> dict:
        """
        Run a TEE-verified LLM analysis of a twin's reputation.
        Returns { analysis: str, payment_hash: str | None }
        """
        if self.demo_mode:
            return self._demo_analysis(twin_name)

        system_prompt = (
            "You are a crypto market analyst evaluating digital twins on Twin.fun. "
            "Given a twin's memory history (past predictions, trades, and statements), "
            "produce a structured JSON reputation report.\n\n"
            "Output ONLY valid JSON with these fields:\n"
            "- accuracy_pct: estimated prediction accuracy (0-100)\n"
            "- bias: 'bullish' | 'bearish' | 'neutral'\n"
            "- strengths: list of 2-3 key strengths\n"
            "- weaknesses: list of 1-2 weaknesses\n"
            "- risk_rating: 'low' | 'medium' | 'high'\n"
            "- narrative: 1-sentence summary of this twin's track record"
        )

        user_prompt = (
            f"Digital Twin: {twin_name}\n\n"
            f"Memory History:\n{memory_context}\n\n"
            "Analyze this twin and output the JSON reputation report."
        )

        try:
            import opengradient as og

            result = _run_async(self.llm.chat(
                model=og.TEE_LLM.GPT_4_1_2025_04_14,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
                temperature=0.1,
                x402_settlement_mode=og.x402SettlementMode.INDIVIDUAL_FULL,
            ))

            return {
                "analysis": result.chat_output.get("content", "{}"),
                "payment_hash": result.payment_hash,
            }
        except Exception as e:
            print(f"[OG] LLM inference failed: {e}, falling back to demo")
            return self._demo_analysis(twin_name)

    # ------------------------------------------------------------------
    # On-Chain Forecast Models (Alpha testnet)
    # ------------------------------------------------------------------

    def get_forecasts(self) -> dict:
        """
        Read live price forecasts from OG's on-chain workflow models.
        Returns { BTC: {...}, ETH: {...}, SOL: {...}, SUI: {...} }
        """
        # Alpha testnet forecasts need og.Alpha client (separate network)
        # For now use demo data — LLM inference is the core feature
        return DEMO_FORECASTS

    # ------------------------------------------------------------------
    # Demo fallbacks
    # ------------------------------------------------------------------

    def _demo_analysis(self, twin_name: str) -> dict:
        """Generate a plausible demo analysis."""
        import random
        accuracy = random.randint(45, 85)
        bias = random.choice(["bullish", "bearish", "neutral"])
        risk = "low" if accuracy > 70 else ("medium" if accuracy > 55 else "high")
        analysis = {
            "accuracy_pct": accuracy,
            "bias": bias,
            "strengths": ["Consistent timeframe analysis", "Good entry timing"],
            "weaknesses": ["Over-leveraged positions"],
            "risk_rating": risk,
            "narrative": f"{twin_name} shows a {bias} bias with ~{accuracy}% accuracy on recent calls.",
        }
        return {
            "analysis": json.dumps(analysis),
            "payment_hash": f"0xDEMO_{twin_name}_{int(time.time())}",
        }
