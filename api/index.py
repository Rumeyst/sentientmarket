"""
SentientMarket — Vercel Serverless Entry Point
Wraps the FastAPI app for Vercel's Python runtime.
"""

import sys
import os

# Add project root to Python path so imports resolve
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Set the static dir env var so server.py knows where to find files
os.environ.setdefault("STATIC_DIR", os.path.join(ROOT, "static"))

from server import app  # noqa: E402

# Vercel expects 'app' at module level
# FastAPI is ASGI-compatible, Vercel handles it automatically
