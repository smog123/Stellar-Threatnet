"""Async-capable Python client for the Stellar ThreatNet API.

Example:
    from stellar_threatnet_sdk import ThreatNetClient

    client = ThreatNetClient(api_key="tn_...")
    result = await client.lookup_wallet("GABC...")
"""
from typing import Any, Dict, List, Optional

import httpx

DEFAULT_BASE_URL = "https://api.stellar-threatnet.org/api/v1"


class ThreatNetClient:
    """Thin, typed client over the ThreatNet REST API."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        headers: Dict[str, str] = {}
        if api_key:
            headers["X-API-Key"] = api_key
        elif token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(base_url=base_url.rstrip("/"), headers=headers, timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "ThreatNetClient":
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    # ------------------------------------------------------------------ #
    # Lookups
    # ------------------------------------------------------------------ #
    async def lookup_wallet(self, address: str) -> Dict[str, Any]:
        resp = await self._client.get(f"/lookup/wallet/{address}")
        resp.raise_for_status()
        return resp.json()

    async def lookup_domain(self, domain: str) -> Dict[str, Any]:
        resp = await self._client.get(f"/lookup/domain/{domain}")
        resp.raise_for_status()
        return resp.json()

    async def lookup_token(self, asset_code: str, issuer: str) -> Dict[str, Any]:
        resp = await self._client.get(f"/lookup/token/{asset_code}/{issuer}")
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------ #
    # Incidents
    # ------------------------------------------------------------------ #
    async def incidents(
        self, status: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> Dict[str, Any]:
        resp = await self._client.get(
            "/incidents", params={"status": status, "limit": limit, "offset": offset}
        )
        resp.raise_for_status()
        return resp.json()

    async def incident(self, incident_id: str) -> Dict[str, Any]:
        resp = await self._client.get(f"/incidents/{incident_id}")
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------ #
    # Feed, stats, search, latest threats
    # ------------------------------------------------------------------ #
    async def latest_threats(self, limit: int = 10) -> List[Dict[str, Any]]:
        resp = await self._client.get("/threats/latest", params={"limit": limit})
        resp.raise_for_status()
        return resp.json()

    async def stats(self) -> Dict[str, Any]:
        resp = await self._client.get("/stats")
        resp.raise_for_status()
        return resp.json()

    async def search(
        self, query: str, entity_type: Optional[str] = None, limit: int = 20
    ) -> Dict[str, Any]:
        resp = await self._client.get(
            "/search", params={"q": query, "type": entity_type, "limit": limit}
        )
        resp.raise_for_status()
        return resp.json()

    async def download_feed(self, output_path: str) -> int:
        """Download the CSV threat feed to a local file. Returns bytes written."""
        resp = await self._client.get("/feed")
        resp.raise_for_status()
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(resp.text)
        return len(resp.text)

    # ------------------------------------------------------------------ #
    # Community reports & AI
    # ------------------------------------------------------------------ #
    async def submit_report(
        self,
        target_type: str,
        target_value: str,
        description: str,
        category: Optional[str] = None,
        evidence_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        resp = await self._client.post(
            "/reports",
            json={
                "target_type": target_type,
                "target_value": target_value,
                "category": category,
                "description": description,
                "evidence_url": evidence_url,
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def ai_query(self, query: str, context_type: str = "general") -> Dict[str, Any]:
        resp = await self._client.post("/ai/query", json={"query": query, "context_type": context_type})
        resp.raise_for_status()
        return resp.json()
