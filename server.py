"""
SentientMarket — API Server
FastAPI backend serving the dashboard and API endpoints.
"""

from __future__ import annotations
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import Config, get_og_client
from og_client import OGClient
from memsync_client import MemSyncClient
from twin_collector import TwinCollector
from reputation_engine import ReputationEngine

# ---------------------------------------------------------------------------
# App init
# ---------------------------------------------------------------------------

app = FastAPI(title="SentientMarket", version="0.1.0")

STATIC_DIR = Path(os.environ.get("STATIC_DIR", str(Path(__file__).parent / "static")))
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Initialize engine
og_sdk = get_og_client()
og = OGClient(og_sdk)
memsync = MemSyncClient()
collector = TwinCollector(demo_mode=True)
engine = ReputationEngine(og=og, memsync=memsync, collector=collector)


@app.on_event("startup")
async def startup():
    """Ingest demo data on startup."""
    issues = Config.validate()
    if issues:
        print(f"[Server] Config issues (running in demo mode): {issues}")
    engine.initialize()
    print("[Server] SentientMarket ready!")


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main dashboard."""
    html_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/twin/{twin_id}", response_class=HTMLResponse)
async def twin_page(twin_id: str):
    """Serve the twin detail page."""
    html_path = STATIC_DIR / "twin.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.get("/api/leaderboard")
async def api_leaderboard():
    """Get the ranked leaderboard."""
    return JSONResponse(content=engine.get_leaderboard())


@app.get("/api/twin/{twin_id}")
async def api_twin_detail(twin_id: str):
    """Get detailed reputation score for a twin."""
    score = engine.score_twin(twin_id)
    if not score:
        return JSONResponse(content={"error": "Twin not found"}, status_code=404)
    # Serialize for JSON (twin data may have non-serializable values)
    return JSONResponse(content={
        "twin": score["twin"],
        "accuracy": score["accuracy"],
        "ai_analysis": score["ai_analysis"],
        "payment_hash": score.get("payment_hash", ""),
        "explorer_url": score.get("explorer_url", ""),
        "scored_at": score.get("scored_at", 0),
    })


@app.get("/api/forecasts")
async def api_forecasts():
    """Get current OG on-chain forecasts."""
    return JSONResponse(content=og.get_forecasts())


@app.get("/api/network")
async def api_network():
    """Return OG network config for wallet connection."""
    return JSONResponse(content={
        "chainId": hex(Config.OG_CHAIN_ID),
        "chainIdDecimal": Config.OG_CHAIN_ID,
        "chainName": "OpenGradient",
        "rpcUrls": [Config.OG_RPC_URL],
        "blockExplorerUrls": [Config.OG_EXPLORER_URL],
        "nativeCurrency": {
            "name": "ETH",
            "symbol": "ETH",
            "decimals": 18,
        },
    })


@app.get("/api/health")
async def api_health():
    """Health check."""
    return JSONResponse(content={
        "status": "ok",
        "demo_mode": og.demo_mode,
        "memsync_demo": memsync.demo_mode,
        "twins_loaded": len(collector.get_all_twins()),
    })


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
    )
