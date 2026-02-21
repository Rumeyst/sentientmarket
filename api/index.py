"""
SentientMarket — Vercel Serverless Entry Point
Wraps the FastAPI app for Vercel's Python runtime.
"""

import sys
import os

# Add project root to Python path so imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

# Vercel expects 'app' or 'handler' at module level
# FastAPI is ASGI-compatible, Vercel handles it automatically
