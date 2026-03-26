"""
SentientMarket — Twin Data Collector
Fetches and normalizes digital twin data from Twin.fun.
Uses demo data when live API is unavailable.
"""

from __future__ import annotations
import time
from typing import Optional


# ---------------------------------------------------------------------------
# Demo twin data (representative examples for the pitch)
# ---------------------------------------------------------------------------

DEMO_TWINS: list[dict] = [
    {
        "id": "twin_alpha_whale",
        "name": "AlphaWhale",
        "bio": "On-chain whale tracker. Follows smart money flows across DeFi protocols.",
        "avatar": "🐋",
        "created_at": int(time.time()) - 86400 * 30,
        "predictions": [
            {"asset": "BTC", "direction": "long", "price_at_call": 94200, "target": 98000, "timestamp": int(time.time()) - 86400 * 7, "outcome": "hit", "actual_price": 98450},
            {"asset": "ETH", "direction": "long", "price_at_call": 3180, "target": 3400, "timestamp": int(time.time()) - 86400 * 5, "outcome": "miss", "actual_price": 3150},
            {"asset": "SOL", "direction": "long", "price_at_call": 165, "target": 180, "timestamp": int(time.time()) - 86400 * 3, "outcome": "hit", "actual_price": 182},
            {"asset": "BTC", "direction": "short", "price_at_call": 99100, "target": 96000, "timestamp": int(time.time()) - 86400 * 2, "outcome": "hit", "actual_price": 95800},
            {"asset": "ETH", "direction": "long", "price_at_call": 3250, "target": 3500, "timestamp": int(time.time()) - 86400, "outcome": "pending", "actual_price": None},
        ],
    },
    {
        "id": "twin_degen_sage",
        "name": "DegenSage",
        "bio": "High-conviction altcoin calls. Lives for the 10x or bust.",
        "avatar": "🔮",
        "created_at": int(time.time()) - 86400 * 45,
        "predictions": [
            {"asset": "SOL", "direction": "long", "price_at_call": 140, "target": 200, "timestamp": int(time.time()) - 86400 * 10, "outcome": "hit", "actual_price": 205},
            {"asset": "SUI", "direction": "long", "price_at_call": 3.50, "target": 5.00, "timestamp": int(time.time()) - 86400 * 8, "outcome": "miss", "actual_price": 3.20},
            {"asset": "ETH", "direction": "short", "price_at_call": 3400, "target": 3100, "timestamp": int(time.time()) - 86400 * 6, "outcome": "hit", "actual_price": 3050},
            {"asset": "BTC", "direction": "long", "price_at_call": 91000, "target": 100000, "timestamp": int(time.time()) - 86400 * 4, "outcome": "miss", "actual_price": 89500},
            {"asset": "SOL", "direction": "long", "price_at_call": 170, "target": 190, "timestamp": int(time.time()) - 86400, "outcome": "hit", "actual_price": 192},
            {"asset": "SUI", "direction": "long", "price_at_call": 3.80, "target": 4.50, "timestamp": int(time.time()) - 3600, "outcome": "pending", "actual_price": None},
        ],
    },
    {
        "id": "twin_macro_mind",
        "name": "MacroMind",
        "bio": "Macro-first approach. Reads the Fed tea leaves before touching a chart.",
        "avatar": "📊",
        "created_at": int(time.time()) - 86400 * 60,
        "predictions": [
            {"asset": "BTC", "direction": "long", "price_at_call": 88000, "target": 95000, "timestamp": int(time.time()) - 86400 * 14, "outcome": "hit", "actual_price": 96200},
            {"asset": "ETH", "direction": "long", "price_at_call": 3000, "target": 3300, "timestamp": int(time.time()) - 86400 * 12, "outcome": "hit", "actual_price": 3350},
            {"asset": "BTC", "direction": "long", "price_at_call": 95000, "target": 100000, "timestamp": int(time.time()) - 86400 * 9, "outcome": "hit", "actual_price": 101200},
            {"asset": "SOL", "direction": "short", "price_at_call": 190, "target": 170, "timestamp": int(time.time()) - 86400 * 5, "outcome": "miss", "actual_price": 195},
            {"asset": "BTC", "direction": "short", "price_at_call": 99500, "target": 95000, "timestamp": int(time.time()) - 86400 * 2, "outcome": "hit", "actual_price": 94800},
        ],
    },
    {
        "id": "twin_snipe_bot",
        "name": "SnipeBot",
        "bio": "Scalper mentality. Quick entries, tight stops, volume-driven.",
        "avatar": "🎯",
        "created_at": int(time.time()) - 86400 * 20,
        "predictions": [
            {"asset": "SOL", "direction": "long", "price_at_call": 172, "target": 178, "timestamp": int(time.time()) - 86400 * 6, "outcome": "hit", "actual_price": 179},
            {"asset": "ETH", "direction": "short", "price_at_call": 3300, "target": 3200, "timestamp": int(time.time()) - 86400 * 4, "outcome": "hit", "actual_price": 3190},
            {"asset": "BTC", "direction": "long", "price_at_call": 96000, "target": 97500, "timestamp": int(time.time()) - 86400 * 3, "outcome": "miss", "actual_price": 95200},
            {"asset": "SUI", "direction": "long", "price_at_call": 3.90, "target": 4.20, "timestamp": int(time.time()) - 86400 * 2, "outcome": "hit", "actual_price": 4.25},
            {"asset": "ETH", "direction": "long", "price_at_call": 3220, "target": 3350, "timestamp": int(time.time()) - 86400, "outcome": "miss", "actual_price": 3180},
            {"asset": "SOL", "direction": "short", "price_at_call": 180, "target": 172, "timestamp": int(time.time()) - 7200, "outcome": "pending", "actual_price": None},
        ],
    },
    {
        "id": "twin_yield_farmer",
        "name": "YieldFarmer",
        "bio": "Doesn't trade — farms. Watches TVL flows and protocol emissions.",
        "avatar": "🌾",
        "created_at": int(time.time()) - 86400 * 55,
        "predictions": [
            {"asset": "ETH", "direction": "long", "price_at_call": 3100, "target": 3400, "timestamp": int(time.time()) - 86400 * 11, "outcome": "hit", "actual_price": 3420},
            {"asset": "SOL", "direction": "long", "price_at_call": 155, "target": 175, "timestamp": int(time.time()) - 86400 * 8, "outcome": "hit", "actual_price": 178},
            {"asset": "SUI", "direction": "long", "price_at_call": 3.20, "target": 4.00, "timestamp": int(time.time()) - 86400 * 5, "outcome": "miss", "actual_price": 3.10},
            {"asset": "BTC", "direction": "long", "price_at_call": 93000, "target": 97000, "timestamp": int(time.time()) - 86400 * 3, "outcome": "hit", "actual_price": 97500},
            {"asset": "ETH", "direction": "short", "price_at_call": 3350, "target": 3150, "timestamp": int(time.time()) - 86400, "outcome": "pending", "actual_price": None},
        ],
    },
    {
        "id": "twin_onchain_oracle",
        "name": "OnChainOracle",
        "bio": "Pure data. Reads wallets, monitors flows, ignores narratives.",
        "avatar": "🔗",
        "created_at": int(time.time()) - 86400 * 40,
        "predictions": [
            {"asset": "BTC", "direction": "long", "price_at_call": 90000, "target": 96000, "timestamp": int(time.time()) - 86400 * 12, "outcome": "hit", "actual_price": 96800},
            {"asset": "ETH", "direction": "long", "price_at_call": 3050, "target": 3300, "timestamp": int(time.time()) - 86400 * 10, "outcome": "hit", "actual_price": 3380},
            {"asset": "SOL", "direction": "long", "price_at_call": 150, "target": 170, "timestamp": int(time.time()) - 86400 * 8, "outcome": "hit", "actual_price": 174},
            {"asset": "BTC", "direction": "short", "price_at_call": 98000, "target": 94000, "timestamp": int(time.time()) - 86400 * 5, "outcome": "hit", "actual_price": 93500},
            {"asset": "ETH", "direction": "long", "price_at_call": 3200, "target": 3450, "timestamp": int(time.time()) - 86400 * 3, "outcome": "hit", "actual_price": 3470},
            {"asset": "SOL", "direction": "long", "price_at_call": 175, "target": 195, "timestamp": int(time.time()) - 86400, "outcome": "miss", "actual_price": 171},
        ],
    },
    {
        "id": "twin_contrarian_king",
        "name": "ContrarianKing",
        "bio": "Fades every consensus trade. If CT is bullish, this one's short.",
        "avatar": "👑",
        "created_at": int(time.time()) - 86400 * 35,
        "predictions": [
            {"asset": "BTC", "direction": "short", "price_at_call": 97000, "target": 92000, "timestamp": int(time.time()) - 86400 * 9, "outcome": "miss", "actual_price": 98500},
            {"asset": "SOL", "direction": "short", "price_at_call": 185, "target": 165, "timestamp": int(time.time()) - 86400 * 7, "outcome": "hit", "actual_price": 162},
            {"asset": "ETH", "direction": "short", "price_at_call": 3350, "target": 3100, "timestamp": int(time.time()) - 86400 * 5, "outcome": "hit", "actual_price": 3080},
            {"asset": "BTC", "direction": "short", "price_at_call": 95000, "target": 90000, "timestamp": int(time.time()) - 86400 * 3, "outcome": "miss", "actual_price": 96200},
            {"asset": "SUI", "direction": "short", "price_at_call": 4.20, "target": 3.50, "timestamp": int(time.time()) - 86400 * 2, "outcome": "miss", "actual_price": 4.35},
            {"asset": "SOL", "direction": "short", "price_at_call": 178, "target": 160, "timestamp": int(time.time()) - 3600, "outcome": "pending", "actual_price": None},
        ],
    },
    {
        "id": "twin_momentum_max",
        "name": "MomentumMax",
        "bio": "Rides the trend until it breaks. Never catches tops or bottoms.",
        "avatar": "⚡",
        "created_at": int(time.time()) - 86400 * 25,
        "predictions": [
            {"asset": "SOL", "direction": "long", "price_at_call": 160, "target": 185, "timestamp": int(time.time()) - 86400 * 8, "outcome": "hit", "actual_price": 188},
            {"asset": "BTC", "direction": "long", "price_at_call": 93000, "target": 98000, "timestamp": int(time.time()) - 86400 * 6, "outcome": "hit", "actual_price": 98200},
            {"asset": "ETH", "direction": "long", "price_at_call": 3200, "target": 3500, "timestamp": int(time.time()) - 86400 * 4, "outcome": "miss", "actual_price": 3150},
            {"asset": "SOL", "direction": "long", "price_at_call": 180, "target": 200, "timestamp": int(time.time()) - 86400 * 2, "outcome": "hit", "actual_price": 203},
            {"asset": "BTC", "direction": "long", "price_at_call": 99000, "target": 105000, "timestamp": int(time.time()) - 86400, "outcome": "miss", "actual_price": 97500},
            {"asset": "ETH", "direction": "long", "price_at_call": 3280, "target": 3400, "timestamp": int(time.time()) - 7200, "outcome": "pending", "actual_price": None},
        ],
    },
    {
        "id": "twin_liquidity_lens",
        "name": "LiquidityLens",
        "bio": "Watches the order book like a hawk. Trades the liquidity, not the chart.",
        "avatar": "🔍",
        "created_at": int(time.time()) - 86400 * 50,
        "predictions": [
            {"asset": "BTC", "direction": "long", "price_at_call": 91000, "target": 95000, "timestamp": int(time.time()) - 86400 * 11, "outcome": "hit", "actual_price": 95400},
            {"asset": "ETH", "direction": "short", "price_at_call": 3400, "target": 3200, "timestamp": int(time.time()) - 86400 * 9, "outcome": "hit", "actual_price": 3180},
            {"asset": "SOL", "direction": "long", "price_at_call": 168, "target": 180, "timestamp": int(time.time()) - 86400 * 7, "outcome": "hit", "actual_price": 183},
            {"asset": "SUI", "direction": "long", "price_at_call": 3.60, "target": 4.20, "timestamp": int(time.time()) - 86400 * 5, "outcome": "miss", "actual_price": 3.45},
            {"asset": "BTC", "direction": "short", "price_at_call": 98000, "target": 94000, "timestamp": int(time.time()) - 86400 * 3, "outcome": "hit", "actual_price": 93800},
            {"asset": "ETH", "direction": "long", "price_at_call": 3150, "target": 3350, "timestamp": int(time.time()) - 86400 * 2, "outcome": "hit", "actual_price": 3370},
            {"asset": "SOL", "direction": "long", "price_at_call": 176, "target": 190, "timestamp": int(time.time()) - 86400, "outcome": "miss", "actual_price": 172},
        ],
    },
]


class TwinCollector:
    """Fetches digital twin data — live from Twin.fun or demo data."""

    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self._twins: dict[str, dict] = {t["id"]: t for t in DEMO_TWINS}

    def get_all_twins(self) -> list[dict]:
        """Return all tracked digital twins."""
        if self.demo_mode:
            return DEMO_TWINS
        # TODO: Hit Twin.fun subgraph/API when available
        return DEMO_TWINS

    def get_twin(self, twin_id: str) -> Optional[dict]:
        """Get a specific twin by ID."""
        return self._twins.get(twin_id)

    def get_twin_by_name(self, name: str) -> Optional[dict]:
        """Get a specific twin by name."""
        for t in self._twins.values():
            twin_name: str = t["name"]
            if twin_name.lower() == name.lower():
                return t
        return None

    def get_resolved_predictions(self, twin_id: str) -> list[dict]:
        """Get only predictions with known outcomes (not pending)."""
        twin = self.get_twin(twin_id)
        if not twin:
            return []
        return [p for p in twin.get("predictions", []) if p.get("outcome") != "pending"]
