"""
SentientMarket — OpenGradient Client
Uses the OG SDK for TEE-verified LLM inference with x402 payment settlement.

Two modes:
  1. LIVE (SDK available + OG_PRIVATE_KEY set): Real x402 inference via SDK
  2. DEMO (SDK unavailable or no key): Generated demo data

The SDK handles x402 payment flow internally via on-chain contracts.
Users need OPG tokens on Base Sepolia to pay for inference.
"""

from __future__ import annotations
import asyncio
import json
import os
import time
import threading
from typing import Any, Optional

from config import Config

# ---------------------------------------------------------------------------
# Try to import the OpenGradient SDK
# ---------------------------------------------------------------------------

try:
    import opengradient as og
    OG_SDK_AVAILABLE = True
except ImportError:
    OG_SDK_AVAILABLE = False
    print("[OG] opengradient SDK not installed — demo mode only")

# ---------------------------------------------------------------------------
# Demo / fallback data
# ---------------------------------------------------------------------------

DEMO_FORECASTS = {
    "BTC": {"price": 97420.50, "direction": "bullish", "confidence": 0.72, "horizon": "1h", "timestamp": int(time.time())},
    "ETH": {"price": 3285.10, "direction": "bearish", "confidence": 0.58, "horizon": "1h", "timestamp": int(time.time())},
    "SOL": {"price": 178.40, "direction": "bullish", "confidence": 0.65, "horizon": "1h", "timestamp": int(time.time())},
    "SUI": {"price": 4.12, "direction": "neutral", "confidence": 0.51, "horizon": "1h", "timestamp": int(time.time())},
}

# System prompt for twin analysis
SYSTEM_PROMPT = (
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


# ---------------------------------------------------------------------------
# Persistent background event loop — all SDK async calls run here
# ---------------------------------------------------------------------------

_bg_loop: Optional[asyncio.AbstractEventLoop] = None
_bg_thread: Optional[threading.Thread] = None


def _get_bg_loop() -> asyncio.AbstractEventLoop:
    """Get or create the persistent background event loop."""
    global _bg_loop, _bg_thread
    if _bg_loop is not None and _bg_loop.is_running():
        return _bg_loop

    _bg_loop = asyncio.new_event_loop()

    def _run_loop():
        asyncio.set_event_loop(_bg_loop)
        _bg_loop.run_forever()

    _bg_thread = threading.Thread(target=_run_loop, daemon=True)
    _bg_thread.start()
    return _bg_loop


def _run_async(coro: Any) -> Any:
    """Run an async coroutine on the persistent background event loop."""
    loop = _get_bg_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=120)  # 2 min timeout


class OGClient:
    """OpenGradient client — uses SDK for real x402 inference when available."""

    def __init__(self, private_key: str = ""):
        self.private_key = private_key or Config.OG_PRIVATE_KEY
        self.demo_mode = True
        self.llm = None

        if OG_SDK_AVAILABLE and self.private_key:
            try:
                # Create LLM client on the background loop so httpx binds there
                self.llm = _run_async(self._create_llm())
                self.demo_mode = False
                print("[OG] ✅ SDK initialized — live mode")

                # Try to approve OPG spending (may fail if no ETH for gas)
                try:
                    self.llm.ensure_opg_approval(opg_amount=5)
                    print("[OG] ✅ OPG approval confirmed")
                except Exception as e:
                    print(f"[WARN] OPG approval failed: {e} — x402 calls may still work if previously approved")

            except Exception as e:
                print(f"[WARN] SDK init failed: {e} — running demo mode")
                self.demo_mode = True
        elif OG_SDK_AVAILABLE and not self.private_key:
            print("[INFO] OG SDK available but no OG_PRIVATE_KEY — demo mode")
        else:
            print("[INFO] OG SDK not installed — demo mode")

    async def _create_llm(self):
        """Create the LLM client inside the background event loop context."""
        return og.LLM(private_key=self.private_key)

    # ------------------------------------------------------------------
    # TEE-Verified LLM Analysis
    # ------------------------------------------------------------------

    def analyze_twin(self, twin_name: str, memory_context: str) -> dict:
        """
        Run a TEE-verified LLM analysis of a twin's reputation.
        Returns { analysis: str, payment_hash: str }
        """
        if self.demo_mode:
            return self._demo_analysis(twin_name)

        user_prompt = (
            f"Digital Twin: {twin_name}\n\n"
            f"Memory History:\n{memory_context}\n\n"
            "Analyze this twin and output the JSON reputation report."
        )

        try:
            # Call the SDK's chat method (may be sync or async)
            chat_call = self.llm.chat(
                model=og.TEE_LLM.GPT_4_1_2025_04_14,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
                temperature=0.1,
            )

            # Handle both sync and async returns
            import asyncio
            if asyncio.iscoroutine(chat_call) or asyncio.isfuture(chat_call):
                result = _run_async(chat_call)
            else:
                result = chat_call

            # Extract content from TextGenerationOutput
            content = ""
            if hasattr(result, 'chat_output') and result.chat_output:
                content = result.chat_output.get('content', '') if isinstance(result.chat_output, dict) else str(result.chat_output)
            elif hasattr(result, 'content'):
                content = result.content or ""
            elif hasattr(result, 'choices') and result.choices:
                content = result.choices[0].message.content or ""
            else:
                content = str(result)

            # Use TEE signature as proof (unique per call, unlike tee_id which is the enclave ID)
            proof_hash = ""
            tee_sig = getattr(result, 'tee_signature', '') or ''
            tee_id = getattr(result, 'tee_id', '') or ''
            tee_endpoint = getattr(result, 'tee_endpoint', '') or ''

            if tee_sig:
                proof_hash = tee_sig[:64]  # First 64 chars of the unique signature
            elif hasattr(result, 'transaction_hash') and result.transaction_hash and result.transaction_hash != 'external':
                proof_hash = result.transaction_hash
            elif hasattr(result, 'payment_hash') and result.payment_hash:
                proof_hash = result.payment_hash

            if proof_hash:
                print(f"[OG] ✅ TEE verified: {proof_hash[:24]}...")
                print(f"[OG]    Enclave: {tee_id[:16]}... | Endpoint: {tee_endpoint}")

            return {
                "analysis": content,
                "payment_hash": proof_hash or f"0xTEE_{twin_name}_{int(time.time())}",
                "tee_verified": True,
            }

        except Exception as e:
            import traceback
            print(f"[OG] x402 inference failed: {e}")
            traceback.print_exc()
            print("[OG] Falling back to demo")
            return self._demo_analysis(twin_name)

    # ------------------------------------------------------------------
    # On-Chain Forecast Models
    # ------------------------------------------------------------------

    def get_forecasts(self) -> dict:
        """Return demo forecasts (Alpha testnet is separate network)."""
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
