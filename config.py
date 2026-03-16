"""
SentientMarket — Configuration
Loads env vars. No SDK dependency — uses direct HTTP x402 calls.
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

    # OPG token on Base Sepolia (for x402 payments)
    OPG_TOKEN_ADDRESS: str = "0x240b09731D96979f50B2C649C9CE10FcF9C7987F"

    # MemSync
    MEMSYNC_BASE_URL: str = "https://api.memchat.io/v1"

    @classmethod
    def validate(cls) -> list[str]:
        """Return list of config notes (non-blocking)."""
        notes = []
        if not cls.OG_PRIVATE_KEY:
            notes.append("OG_PRIVATE_KEY not set — using demo mode")
        if not cls.MEMSYNC_API_KEY or cls.MEMSYNC_API_KEY == "your_memsync_api_key_here":
            notes.append("MEMSYNC_API_KEY not set — using demo memory store")
        return notes
