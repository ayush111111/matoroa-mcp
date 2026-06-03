"""Thin async wrapper around the Mataroa REST API using httpx."""

from __future__ import annotations

from typing import Any

import httpx

BASE_URL = "https://mataroa.blog/api"
TIMEOUT = 30.0


class MataroaClient:
    def __init__(self, api_key: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=BASE_URL,
            headers=self._headers,
            timeout=TIMEOUT,
        )

    # ── Posts ──────────────────────────────────────────────────────────────

    async def list_posts(self) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.get("/posts/")
            return _parse(r)

    async def get_post(self, slug: str) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.get(f"/posts/{slug}/")
            return _parse(r)

    async def create_post(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.post("/posts/", json=payload)
            return _parse(r)

    async def update_post(self, slug: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.patch(f"/posts/{slug}/", json=payload)
            return _parse(r)

    async def delete_post(self, slug: str) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.delete(f"/posts/{slug}/")
            return _parse(r)

    # ── Comments ───────────────────────────────────────────────────────────

    async def list_comments(self) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.get("/comments/")
            return _parse(r)

    async def list_comments_for_post(self, slug: str) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.get(f"/posts/{slug}/comments/")
            return _parse(r)

    async def list_pending_comments(self) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.get("/comments/pending/")
            return _parse(r)

    async def get_comment(self, comment_id: int) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.get(f"/comments/{comment_id}/")
            return _parse(r)

    async def approve_comment(self, comment_id: int) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.post(f"/comments/{comment_id}/approve/")
            return _parse(r)

    async def delete_comment(self, comment_id: int) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.delete(f"/comments/{comment_id}/")
            return _parse(r)

    # ── Pages ──────────────────────────────────────────────────────────────

    async def list_pages(self) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.get("/pages/")
            return _parse(r)

    async def get_page(self, slug: str) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.get(f"/pages/{slug}/")
            return _parse(r)

    async def create_page(self, payload: dict[str, Any]) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.post("/pages/", json=payload)
            return _parse(r)

    async def update_page(self, slug: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.patch(f"/pages/{slug}/", json=payload)
            return _parse(r)

    async def delete_page(self, slug: str) -> dict[str, Any]:
        async with self._client() as c:
            r = await c.delete(f"/pages/{slug}/")
            return _parse(r)


def _parse(response: httpx.Response) -> dict[str, Any]:
    """Normalise every API response into a plain dict."""
    status = response.status_code

    if status == 204 or response.content == b"":
        return {"ok": True}

    try:
        data = response.json()
    except Exception:
        return {
            "ok": False,
            "error": f"Mataroa API returned non-JSON response (HTTP {status})",
        }

    if status == 401:
        return {"ok": False, "error": "Authentication failed. Check your MATAROA_API_KEY."}
    if status == 404:
        return {"ok": False, "error": data.get("detail", "Resource not found.")}
    if status >= 500:
        return {"ok": False, "error": f"Mataroa API server error (HTTP {status})."}
    if status >= 400:
        return {"ok": False, "error": data.get("detail", f"API error (HTTP {status}): {data}")}

    # Successful responses don't always include an "ok" key — normalise.
    if isinstance(data, dict) and "ok" not in data:
        data["ok"] = True
    return data
