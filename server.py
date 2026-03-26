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

from config import Config
from og_client import OGClient
from memsync_client import MemSyncClient
from twin_collector import TwinCollector
from reputation_engine import ReputationEngine

# ---------------------------------------------------------------------------
# App init
# ---------------------------------------------------------------------------

app = FastAPI(title="SentientMarket", version="0.1.0")

STATIC_DIR = Path(os.environ.get("STATIC_DIR", str(Path(__file__).parent / "static")))
ASSETS_DIR = STATIC_DIR / "assets"

# Mount /assets for JS/CSS bundles from the React build
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


# Initialize engine (SDK handles x402 internally when available)
og = OGClient()
memsync = MemSyncClient()
collector = TwinCollector(demo_mode=True)
engine = ReputationEngine(og=og, memsync=memsync, collector=collector)


@app.on_event("startup")
async def startup():
    """Ingest demo data on startup."""
    issues = Config.validate()
    if issues:
        print(f"[Server] Config notes: {issues}")
    engine.initialize()
    print(f"[Server] SentientMarket ready! (demo_mode={og.demo_mode})")


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
    """Health check with detailed SDK status."""
    status = og.get_status()
    return JSONResponse(content={
        "status": "ok",
        "og_sdk": status,
        "memsync_demo": memsync.demo_mode,
        "twins_loaded": len(collector.get_all_twins()),
    })


# ---------------------------------------------------------------------------
# SPA catch-all  (must come AFTER all /api routes)
# ---------------------------------------------------------------------------

@app.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_catch_all(full_path: str):
    """Serve index.html for all non-API routes so React Router handles them."""
    html_path = STATIC_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Build the frontend first</h1>", status_code=404)


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
