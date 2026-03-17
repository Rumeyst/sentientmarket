"""
SentientMarket — Twin Data Collector
Fetches and normalizes digital twin data from Twin.fun.
Uses demo data when live API is unavailable.
"""

from __future__ import annotations
import time
import random
from typing import Optional


# ---------------------------------------------------------------------------
# Realistic demo twin data (used when Twin.fun API isn't available)
# ---------------------------------------------------------------------------

DEMO_TWINS = [
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
        "id": "twin_chain_oracle",
        "name": "ChainOracle",
        "bio": "On-chain data purist. Only trades when wallets move, not when Twitter talks.",
        "avatar": "⛓️",
        "created_at": int(time.time()) - 86400 * 40,
        "predictions": [
            {"asset": "BTC", "direction": "long", "price_at_call": 92000, "target": 98000, "timestamp": int(time.time()) - 86400 * 13, "outcome": "hit", "actual_price": 99100},
            {"asset": "ETH", "direction": "long", "price_at_call": 3050, "target": 3250, "timestamp": int(time.time()) - 86400 * 10, "outcome": "hit", "actual_price": 3310},
            {"asset": "SOL", "direction": "short", "price_at_call": 185, "target": 165, "timestamp": int(time.time()) - 86400 * 7, "outcome": "miss", "actual_price": 190},
            {"asset": "BTC", "direction": "long", "price_at_call": 96500, "target": 102000, "timestamp": int(time.time()) - 86400 * 4, "outcome": "hit", "actual_price": 103200},
            {"asset": "SUI", "direction": "long", "price_at_call": 3.60, "target": 4.20, "timestamp": int(time.time()) - 86400 * 2, "outcome": "hit", "actual_price": 4.35},
            {"asset": "ETH", "direction": "short", "price_at_call": 3400, "target": 3200, "timestamp": int(time.time()) - 86400, "outcome": "hit", "actual_price": 3180},
        ],
    },
    {
        "id": "twin_momentum_mike",
        "name": "MomentumMike",
        "bio": "Rides trends until they break. RSI + volume divergence is the whole playbook.",
        "avatar": "📈",
        "created_at": int(time.time()) - 86400 * 35,
        "predictions": [
            {"asset": "SOL", "direction": "long", "price_at_call": 148, "target": 170, "timestamp": int(time.time()) - 86400 * 12, "outcome": "hit", "actual_price": 175},
            {"asset": "BTC", "direction": "long", "price_at_call": 89000, "target": 94000, "timestamp": int(time.time()) - 86400 * 9, "outcome": "hit", "actual_price": 95200},
            {"asset": "ETH", "direction": "long", "price_at_call": 3100, "target": 3350, "timestamp": int(time.time()) - 86400 * 6, "outcome": "hit", "actual_price": 3370},
            {"asset": "SOL", "direction": "long", "price_at_call": 175, "target": 195, "timestamp": int(time.time()) - 86400 * 3, "outcome": "miss", "actual_price": 168},
            {"asset": "BTC", "direction": "long", "price_at_call": 97000, "target": 103000, "timestamp": int(time.time()) - 86400, "outcome": "pending", "actual_price": None},
        ],
    },
    {
        "id": "twin_bear_hunter",
        "name": "BearHunter",
        "bio": "Contrarian short seller. Profits when everyone else panics.",
        "avatar": "🐻",
        "created_at": int(time.time()) - 86400 * 50,
        "predictions": [
            {"asset": "BTC", "direction": "short", "price_at_call": 101000, "target": 95000, "timestamp": int(time.time()) - 86400 * 15, "outcome": "hit", "actual_price": 94200},
            {"asset": "ETH", "direction": "short", "price_at_call": 3450, "target": 3100, "timestamp": int(time.time()) - 86400 * 11, "outcome": "hit", "actual_price": 3080},
            {"asset": "SOL", "direction": "short", "price_at_call": 195, "target": 170, "timestamp": int(time.time()) - 86400 * 8, "outcome": "miss", "actual_price": 198},
            {"asset": "BTC", "direction": "short", "price_at_call": 98000, "target": 92000, "timestamp": int(time.time()) - 86400 * 4, "outcome": "hit", "actual_price": 91500},
            {"asset": "SUI", "direction": "short", "price_at_call": 4.50, "target": 3.80, "timestamp": int(time.time()) - 86400 * 2, "outcome": "miss", "actual_price": 4.60},
            {"asset": "ETH", "direction": "short", "price_at_call": 3300, "target": 3050, "timestamp": int(time.time()) - 86400, "outcome": "hit", "actual_price": 3020},
        ],
    },
    {
        "id": "twin_sui_maxi",
        "name": "SuiMaxi",
        "bio": "All-in on Sui ecosystem. Tracks Move devs, TVL, and validator counts.",
        "avatar": "💧",
        "created_at": int(time.time()) - 86400 * 25,
        "predictions": [
            {"asset": "SUI", "direction": "long", "price_at_call": 2.80, "target": 3.50, "timestamp": int(time.time()) - 86400 * 14, "outcome": "hit", "actual_price": 3.65},
            {"asset": "SUI", "direction": "long", "price_at_call": 3.40, "target": 4.00, "timestamp": int(time.time()) - 86400 * 10, "outcome": "hit", "actual_price": 4.10},
            {"asset": "SUI", "direction": "long", "price_at_call": 4.20, "target": 5.00, "timestamp": int(time.time()) - 86400 * 6, "outcome": "miss", "actual_price": 3.90},
            {"asset": "BTC", "direction": "long", "price_at_call": 93000, "target": 96000, "timestamp": int(time.time()) - 86400 * 3, "outcome": "hit", "actual_price": 96800},
            {"asset": "SUI", "direction": "long", "price_at_call": 3.90, "target": 4.50, "timestamp": int(time.time()) - 86400, "outcome": "pending", "actual_price": None},
        ],
    },
    {
        "id": "twin_gas_fee_gary",
        "name": "GasFeeGary",
        "bio": "Trades based on gas fee spikes and mempool congestion patterns.",
        "avatar": "⛽",
        "created_at": int(time.time()) - 86400 * 18,
        "predictions": [
            {"asset": "ETH", "direction": "long", "price_at_call": 2900, "target": 3200, "timestamp": int(time.time()) - 86400 * 11, "outcome": "hit", "actual_price": 3250},
            {"asset": "ETH", "direction": "short", "price_at_call": 3350, "target": 3100, "timestamp": int(time.time()) - 86400 * 7, "outcome": "hit", "actual_price": 3070},
            {"asset": "BTC", "direction": "long", "price_at_call": 95000, "target": 99000, "timestamp": int(time.time()) - 86400 * 4, "outcome": "miss", "actual_price": 94200},
            {"asset": "ETH", "direction": "long", "price_at_call": 3000, "target": 3300, "timestamp": int(time.time()) - 86400 * 2, "outcome": "miss", "actual_price": 2980},
            {"asset": "SOL", "direction": "long", "price_at_call": 160, "target": 175, "timestamp": int(time.time()) - 86400, "outcome": "hit", "actual_price": 178},
        ],
    },
    {
        "id": "twin_liquidation_larry",
        "name": "LiquidationLarry",
        "bio": "Watches liquidation heatmaps. Trades the squeeze, not the trend.",
        "avatar": "💀",
        "created_at": int(time.time()) - 86400 * 42,
        "predictions": [
            {"asset": "BTC", "direction": "long", "price_at_call": 87000, "target": 93000, "timestamp": int(time.time()) - 86400 * 16, "outcome": "hit", "actual_price": 94500},
            {"asset": "ETH", "direction": "short", "price_at_call": 3500, "target": 3200, "timestamp": int(time.time()) - 86400 * 12, "outcome": "hit", "actual_price": 3150},
            {"asset": "BTC", "direction": "short", "price_at_call": 100000, "target": 95000, "timestamp": int(time.time()) - 86400 * 8, "outcome": "hit", "actual_price": 94800},
            {"asset": "SOL", "direction": "long", "price_at_call": 155, "target": 175, "timestamp": int(time.time()) - 86400 * 5, "outcome": "hit", "actual_price": 180},
            {"asset": "ETH", "direction": "long", "price_at_call": 3100, "target": 3400, "timestamp": int(time.time()) - 86400 * 2, "outcome": "miss", "actual_price": 3050},
            {"asset": "BTC", "direction": "long", "price_at_call": 96000, "target": 100000, "timestamp": int(time.time()) - 86400, "outcome": "hit", "actual_price": 101500},
        ],
    },
    {
        "id": "twin_funding_rate_fred",
        "name": "FundingRateFred",
        "bio": "Funding rate arbitrage. Goes long when shorts pay, short when longs pay.",
        "avatar": "📊",
        "created_at": int(time.time()) - 86400 * 38,
        "predictions": [
            {"asset": "BTC", "direction": "short", "price_at_call": 99000, "target": 96000, "timestamp": int(time.time()) - 86400 * 13, "outcome": "hit", "actual_price": 95500},
            {"asset": "ETH", "direction": "long", "price_at_call": 3050, "target": 3250, "timestamp": int(time.time()) - 86400 * 9, "outcome": "hit", "actual_price": 3280},
            {"asset": "SOL", "direction": "short", "price_at_call": 188, "target": 175, "timestamp": int(time.time()) - 86400 * 6, "outcome": "miss", "actual_price": 192},
            {"asset": "BTC", "direction": "long", "price_at_call": 94000, "target": 98000, "timestamp": int(time.time()) - 86400 * 3, "outcome": "hit", "actual_price": 98500},
            {"asset": "ETH", "direction": "short", "price_at_call": 3380, "target": 3200, "timestamp": int(time.time()) - 86400, "outcome": "miss", "actual_price": 3400},
        ],
    },
    {
        "id": "twin_onchain_olivia",
        "name": "OnchainOlivia",
        "bio": "Tracks wallet age, token distribution, and holder concentration metrics.",
        "avatar": "🔍",
        "created_at": int(time.time()) - 86400 * 28,
        "predictions": [
            {"asset": "SOL", "direction": "long", "price_at_call": 142, "target": 160, "timestamp": int(time.time()) - 86400 * 15, "outcome": "hit", "actual_price": 165},
            {"asset": "ETH", "direction": "long", "price_at_call": 2950, "target": 3200, "timestamp": int(time.time()) - 86400 * 11, "outcome": "hit", "actual_price": 3220},
            {"asset": "SUI", "direction": "long", "price_at_call": 2.90, "target": 3.50, "timestamp": int(time.time()) - 86400 * 7, "outcome": "hit", "actual_price": 3.60},
            {"asset": "BTC", "direction": "long", "price_at_call": 91000, "target": 96000, "timestamp": int(time.time()) - 86400 * 4, "outcome": "hit", "actual_price": 96500},
            {"asset": "SOL", "direction": "long", "price_at_call": 175, "target": 195, "timestamp": int(time.time()) - 86400 * 2, "outcome": "miss", "actual_price": 170},
            {"asset": "ETH", "direction": "long", "price_at_call": 3200, "target": 3450, "timestamp": int(time.time()) - 86400, "outcome": "hit", "actual_price": 3470},
        ],
    },
    {
        "id": "twin_narratives_nick",
        "name": "NarrativesNick",
        "bio": "Trades narratives, not charts. AI, RWA, DePIN — whatever CT is hyping.",
        "avatar": "📰",
        "created_at": int(time.time()) - 86400 * 22,
        "predictions": [
            {"asset": "SOL", "direction": "long", "price_at_call": 135, "target": 160, "timestamp": int(time.time()) - 86400 * 14, "outcome": "hit", "actual_price": 165},
            {"asset": "SUI", "direction": "long", "price_at_call": 2.50, "target": 3.20, "timestamp": int(time.time()) - 86400 * 10, "outcome": "hit", "actual_price": 3.30},
            {"asset": "ETH", "direction": "long", "price_at_call": 3200, "target": 3500, "timestamp": int(time.time()) - 86400 * 6, "outcome": "miss", "actual_price": 3150},
            {"asset": "BTC", "direction": "long", "price_at_call": 95000, "target": 100000, "timestamp": int(time.time()) - 86400 * 3, "outcome": "miss", "actual_price": 93000},
            {"asset": "SOL", "direction": "long", "price_at_call": 170, "target": 190, "timestamp": int(time.time()) - 86400, "outcome": "pending", "actual_price": None},
        ],
    },
    {
        "id": "twin_whale_watcher",
        "name": "WhaleWatcher",
        "bio": "Follows top 100 wallets. When they accumulate, so does this twin.",
        "avatar": "🐳",
        "created_at": int(time.time()) - 86400 * 32,
        "predictions": [
            {"asset": "BTC", "direction": "long", "price_at_call": 86000, "target": 92000, "timestamp": int(time.time()) - 86400 * 16, "outcome": "hit", "actual_price": 93500},
            {"asset": "ETH", "direction": "long", "price_at_call": 2800, "target": 3100, "timestamp": int(time.time()) - 86400 * 12, "outcome": "hit", "actual_price": 3150},
            {"asset": "SOL", "direction": "long", "price_at_call": 138, "target": 155, "timestamp": int(time.time()) - 86400 * 8, "outcome": "hit", "actual_price": 158},
            {"asset": "BTC", "direction": "long", "price_at_call": 97000, "target": 103000, "timestamp": int(time.time()) - 86400 * 4, "outcome": "miss", "actual_price": 95500},
            {"asset": "SUI", "direction": "long", "price_at_call": 3.30, "target": 4.00, "timestamp": int(time.time()) - 86400 * 2, "outcome": "hit", "actual_price": 4.15},
            {"asset": "ETH", "direction": "short", "price_at_call": 3400, "target": 3200, "timestamp": int(time.time()) - 86400, "outcome": "hit", "actual_price": 3170},
        ],
    },
]


class TwinCollector:
    """Fetches digital twin data — live from Twin.fun or demo data."""

    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode
        self._twins = {t["id"]: t for t in DEMO_TWINS}

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
            if t["name"].lower() == name.lower():
                return t
        return None

    def get_resolved_predictions(self, twin_id: str) -> list[dict]:
        """Get only predictions with known outcomes (not pending)."""
        twin = self.get_twin(twin_id)
        if not twin:
            return []
        return [p for p in twin.get("predictions", []) if p.get("outcome") != "pending"]
