"""
SentientMarket — Configuration & Client Initialization
Loads env vars and provides singleton access to OG SDK + MemSync.
No private key required — wallet connects from the browser.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration loaded from .env file."""

    # Optional — only needed if running server-side OG inference
    OG_PRIVATE_KEY: str = os.getenv("OG_PRIVATE_KEY", "")
    MEMSYNC_API_KEY: str = os.getenv("MEMSYNC_API_KEY", "")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # OpenGradient network (public info — safe for public repos)
    OG_RPC_URL: str = "https://rpc.opengradient.ai"
    OG_CHAIN_ID: int = 10744
    OG_EXPLORER_URL: str = "https://explorer.opengradient.ai"

    # MemSync
    MEMSYNC_BASE_URL: str = "https://api.memchat.io/v1"

    # x402 Gateway
    X402_BASE_URL: str = "https://llmogevm.opengradient.ai"

    @classmethod
    def validate(cls) -> list[str]:
        """Return list of config notes (non-blocking)."""
        notes = []
        if not cls.OG_PRIVATE_KEY:
            notes.append("OG_PRIVATE_KEY not set — using browser wallet or demo mode")
        if not cls.MEMSYNC_API_KEY or cls.MEMSYNC_API_KEY == "your_memsync_api_key_here":
            notes.append("MEMSYNC_API_KEY not set — using demo memory store")
        return notes


def get_og_client():
    """Create and return an OpenGradient SDK client (optional)."""
    if not Config.OG_PRIVATE_KEY:
        print("[INFO] No OG_PRIVATE_KEY — dashboard runs in demo mode. Users connect wallets in-browser.")
        return None
    try:
        import opengradient as og
        client = og.Client(private_key=Config.OG_PRIVATE_KEY)
        return client
    except ImportError:
        print("[WARN] opengradient not installed — running in demo mode")
        return None
    except Exception as e:
        print(f"[WARN] Failed to init OG client: {e} — running in demo mode")
        return None
