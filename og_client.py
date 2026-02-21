"""
SentientMarket — OpenGradient SDK Wrapper
Handles TEE-verified LLM inference and on-chain forecast model reads.
"""

from __future__ import annotations
import json
import time
from typing import Optional

from config import Config

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
    """Wrapper around the OpenGradient Python SDK."""

    def __init__(self, client=None):
        self.client = client
        self.demo_mode = client is None

    # ------------------------------------------------------------------
    # LLM Inference (TEE-verified via x402)
    # ------------------------------------------------------------------

    def analyze_twin(self, twin_name: str, memory_context: str) -> dict:
        """
        Run a TEE-verified LLM analysis of a twin's reputation.
        Returns { analysis: str, payment_hash: str | None }
        """
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

        if self.demo_mode:
            return self._demo_analysis(twin_name)

        try:
            import opengradient as og
            result = self.client.llm.chat(
                model=og.TEE_LLM.GPT_4O,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
                temperature=0.1,
                x402_settlement_mode=og.x402SettlementMode.SETTLE_METADATA,
            )
            return {
                "analysis": result.chat_output.get("content", "{}"),
                "payment_hash": result.payment_hash,
            }
        except Exception as e:
            print(f"[OG] LLM inference failed: {e}, falling back to demo")
            return self._demo_analysis(twin_name)

    # ------------------------------------------------------------------
    # On-Chain Forecast Models
    # ------------------------------------------------------------------

    def get_forecasts(self) -> dict:
        """
        Read live price forecasts from OG's on-chain workflow models.
        Returns { BTC: {...}, ETH: {...}, SOL: {...}, SUI: {...} }
        """
        if self.demo_mode:
            return DEMO_FORECASTS

        forecasts = {}
        try:
            import opengradient as og
            from opengradient.workflow_models.workflow_models import (
                read_btc_1_hour_price_forecast,
                read_eth_1_hour_price_forecast,
                read_sol_1_hour_price_forecast,
                read_sui_1_hour_price_forecast,
            )

            model_readers = {
                "BTC": read_btc_1_hour_price_forecast,
                "ETH": read_eth_1_hour_price_forecast,
                "SOL": read_sol_1_hour_price_forecast,
                "SUI": read_sui_1_hour_price_forecast,
            }

            for symbol, reader in model_readers.items():
                try:
                    raw = reader(self.client.alpha)
                    forecasts[symbol] = {
                        "raw": str(raw),
                        "timestamp": int(time.time()),
                        "source": "opengradient_onchain",
                    }
                except Exception as e:
                    print(f"[OG] Failed to read {symbol} forecast: {e}")
                    forecasts[symbol] = DEMO_FORECASTS.get(symbol, {})

        except ImportError:
            return DEMO_FORECASTS

        return forecasts if forecasts else DEMO_FORECASTS

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
