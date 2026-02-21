"""
SentientMarket — MemSync Client
REST API wrapper for OpenGradient's long-term memory layer.
Handles storing twin activity, searching memories, and retrieving profiles.
"""

from __future__ import annotations
import time
import json
from typing import Optional

import requests

from config import Config


class MemSyncClient:
    """Wrapper around the MemSync REST API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.MEMSYNC_API_KEY
        self.base_url = Config.MEMSYNC_BASE_URL
        self.demo_mode = not self.api_key or self.api_key == "your_memsync_api_key_here"
        self._demo_memories: list[dict] = []

    @property
    def _headers(self) -> dict:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------
    # Store a memory (twin action / prediction / statement)
    # ------------------------------------------------------------------

    def store_memory(
        self,
        twin_name: str,
        action_text: str,
        twin_response: str,
        source: str = "chat",
        thread_id: Optional[str] = None,
    ) -> dict:
        """
        Store a memory about a twin's activity.
        
        Args:
            twin_name:      Name of the digital twin
            action_text:    Description of the twin's action (e.g. "Called BTC long at $95k")
            twin_response:  The outcome or further context
            source:         Memory source type (chat, document, etc.)
            thread_id:      Optional thread grouping
        """
        agent_id = f"sentientmarket-{twin_name.lower().replace(' ', '-')}"
        thread = thread_id or f"twin-{twin_name.lower().replace(' ', '-')}-activity"

        payload = {
            "messages": [
                {"role": "user", "content": f"[Twin: {twin_name}] {action_text}"},
                {"role": "assistant", "content": twin_response},
            ],
            "agent_id": agent_id,
            "thread_id": thread,
            "source": source,
        }

        if self.demo_mode:
            return self._demo_store(twin_name, action_text, twin_response)

        try:
            resp = requests.post(
                f"{self.base_url}/memories",
                headers=self._headers,
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"[MemSync] Store failed: {e}, using demo")
            return self._demo_store(twin_name, action_text, twin_response)

    # ------------------------------------------------------------------
    # Search memories (semantic search)
    # ------------------------------------------------------------------

    def search_memories(
        self,
        query: str,
        twin_name: Optional[str] = None,
        limit: int = 10,
        rerank: bool = True,
    ) -> list[dict]:
        """
        Search stored memories using semantic search.
        
        Args:
            query:      Natural language search query
            twin_name:  Optional filter to a specific twin's memories
            limit:      Max results to return
            rerank:     Whether to re-rank results for relevance
        """
        payload = {
            "query": query,
            "limit": limit,
            "rerank": rerank,
        }

        if twin_name:
            payload["agent_id"] = f"sentientmarket-{twin_name.lower().replace(' ', '-')}"

        if self.demo_mode:
            return self._demo_search(query, twin_name)

        try:
            resp = requests.post(
                f"{self.base_url}/memories/search",
                headers=self._headers,
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception as e:
            print(f"[MemSync] Search failed: {e}, using demo")
            return self._demo_search(query, twin_name)

    # ------------------------------------------------------------------
    # Get user/twin profile
    # ------------------------------------------------------------------

    def get_twin_profile(self, twin_name: str) -> dict:
        """
        Retrieve the auto-generated profile for a twin.
        MemSync builds these from accumulated memories.
        """
        agent_id = f"sentientmarket-{twin_name.lower().replace(' ', '-')}"

        if self.demo_mode:
            return self._demo_profile(twin_name)

        try:
            resp = requests.get(
                f"{self.base_url}/users/{agent_id}/profile",
                headers=self._headers,
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"[MemSync] Profile fetch failed: {e}, using demo")
            return self._demo_profile(twin_name)

    # ------------------------------------------------------------------
    # Demo fallbacks
    # ------------------------------------------------------------------

    def _demo_store(self, twin_name: str, action: str, response: str) -> dict:
        memory = {
            "id": f"demo_{len(self._demo_memories)}",
            "twin_name": twin_name,
            "action": action,
            "response": response,
            "timestamp": int(time.time()),
            "type": "semantic",
        }
        self._demo_memories.append(memory)
        return {"status": "ok", "memory_id": memory["id"]}

    def _demo_search(self, query: str, twin_name: Optional[str] = None) -> list[dict]:
        results = self._demo_memories
        if twin_name:
            results = [m for m in results if m.get("twin_name") == twin_name]
        # Simple keyword matching for demo
        query_lower = query.lower()
        scored = []
        for m in results:
            text = f"{m.get('action', '')} {m.get('response', '')}".lower()
            score = sum(1 for word in query_lower.split() if word in text)
            if score > 0:
                scored.append({**m, "relevance_score": score})
        scored.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return scored[:10]

    def _demo_profile(self, twin_name: str) -> dict:
        twin_memories = [m for m in self._demo_memories if m.get("twin_name") == twin_name]
        return {
            "twin_name": twin_name,
            "total_memories": len(twin_memories),
            "profile_summary": f"Digital twin with {len(twin_memories)} tracked activities.",
            "source": "demo",
        }
