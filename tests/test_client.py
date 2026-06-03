"""Unit tests for MataroaClient — all HTTP calls are mocked via respx."""

import pytest
import respx
import httpx

from mataroa_mcp.client import MataroaClient, BASE_URL
from tests.conftest import (
    PUBLISHED_POST, DRAFT_POST, SECOND_PUBLISHED_POST,
    SAMPLE_COMMENT, SPAM_COMMENT, SAMPLE_PAGE, HIDDEN_PAGE,
)

BASE = BASE_URL


@pytest.fixture
def client():
    return MataroaClient(api_key="test-key")


# ── Posts ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_posts_returns_all(client):
    posts = [PUBLISHED_POST, SECOND_PUBLISHED_POST, DRAFT_POST]
    with respx.mock(base_url=BASE) as mock:
        mock.get("/posts/").mock(return_value=httpx.Response(200, json={"post_list": posts}))
        result = await client.list_posts()
    assert result["ok"] is True
    assert len(result["post_list"]) == 3


@pytest.mark.asyncio
async def test_get_post_valid_slug(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/posts/hello-world/").mock(return_value=httpx.Response(200, json=PUBLISHED_POST))
        result = await client.get_post("hello-world")
    assert result["slug"] == "hello-world"
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_get_post_not_found(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/posts/no-such/").mock(
            return_value=httpx.Response(404, json={"detail": "Not found."})
        )
        result = await client.get_post("no-such")
    assert result["ok"] is False
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_create_post_title_only(client):
    created = {"ok": True, "slug": "new-post", "url": "https://user.mataroa.blog/blog/new-post/"}
    with respx.mock(base_url=BASE) as mock:
        mock.post("/posts/").mock(return_value=httpx.Response(200, json=created))
        result = await client.create_post({"title": "New Post"})
    assert result["slug"] == "new-post"
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_create_post_with_all_fields(client):
    payload = {"title": "Full Post", "body": "Content", "published_at": "2026-06-03"}
    created = {"ok": True, "slug": "full-post", "url": "https://u.mataroa.blog/blog/full-post/"}
    with respx.mock(base_url=BASE) as mock:
        route = mock.post("/posts/").mock(return_value=httpx.Response(200, json=created))
        result = await client.create_post(payload)
    sent = route.calls[0].request
    import json
    body = json.loads(sent.content)
    assert body["published_at"] == "2026-06-03"
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_update_post_body_only(client):
    # PATCH returns only {ok, slug, url} — not the full post object
    updated = {"ok": True, "slug": "hello-world", "url": "https://user.mataroa.blog/blog/hello-world/"}
    with respx.mock(base_url=BASE) as mock:
        mock.patch("/posts/hello-world/").mock(return_value=httpx.Response(200, json=updated))
        result = await client.update_post("hello-world", {"body": "Updated body."})
    assert result["ok"] is True
    assert result["slug"] == "hello-world"


@pytest.mark.asyncio
async def test_update_post_slug_change(client):
    updated = {"ok": True, "slug": "hello-world-v2", "url": "https://user.mataroa.blog/blog/hello-world-v2/"}
    with respx.mock(base_url=BASE) as mock:
        mock.patch("/posts/hello-world/").mock(return_value=httpx.Response(200, json=updated))
        result = await client.update_post("hello-world", {"slug": "hello-world-v2"})
    assert result["slug"] == "hello-world-v2"


@pytest.mark.asyncio
async def test_delete_post(client):
    with respx.mock(base_url=BASE) as mock:
        mock.delete("/posts/hello-world/").mock(return_value=httpx.Response(200, json={"ok": True}))
        result = await client.delete_post("hello-world")
    assert result["ok"] is True


# ── Comments ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_comments_all(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/comments/").mock(
            return_value=httpx.Response(200, json={"comment_list": [SAMPLE_COMMENT, SPAM_COMMENT]})
        )
        result = await client.list_comments()
    assert len(result["comment_list"]) == 2


@pytest.mark.asyncio
async def test_list_comments_for_post(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/posts/hello-world/comments/").mock(
            return_value=httpx.Response(200, json={"comment_list": [SAMPLE_COMMENT]})
        )
        result = await client.list_comments_for_post("hello-world")
    assert result["comment_list"][0]["id"] == 42


@pytest.mark.asyncio
async def test_list_pending_comments(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/comments/pending/").mock(
            return_value=httpx.Response(200, json={"comment_list": [SAMPLE_COMMENT, SPAM_COMMENT]})
        )
        result = await client.list_pending_comments()
    assert len(result["comment_list"]) == 2


@pytest.mark.asyncio
async def test_approve_comment(client):
    # approve response nests the updated comment under a "comment" key
    approved = {"ok": True, "comment": {**SAMPLE_COMMENT, "is_approved": True}}
    with respx.mock(base_url=BASE) as mock:
        mock.post("/comments/42/approve/").mock(return_value=httpx.Response(200, json=approved))
        result = await client.approve_comment(42)
    assert result["ok"] is True
    assert result["comment"]["is_approved"] is True


@pytest.mark.asyncio
async def test_delete_comment(client):
    with respx.mock(base_url=BASE) as mock:
        mock.delete("/comments/43/").mock(return_value=httpx.Response(200, json={"ok": True}))
        result = await client.delete_comment(43)
    assert result["ok"] is True


# ── Pages ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_pages(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/pages/").mock(
            return_value=httpx.Response(200, json={"page_list": [SAMPLE_PAGE, HIDDEN_PAGE]})
        )
        result = await client.list_pages()
    assert len(result["page_list"]) == 2


@pytest.mark.asyncio
async def test_get_page(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/pages/about/").mock(return_value=httpx.Response(200, json=SAMPLE_PAGE))
        result = await client.get_page("about")
    assert result["slug"] == "about"


@pytest.mark.asyncio
async def test_create_page(client):
    created = {"ok": True, "slug": "about", "url": "https://user.mataroa.blog/about/"}
    with respx.mock(base_url=BASE) as mock:
        mock.post("/pages/").mock(return_value=httpx.Response(200, json=created))
        result = await client.create_page({"title": "About", "slug": "about"})
    assert result["slug"] == "about"
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_update_page(client):
    # PATCH returns only {ok, slug, url} — not the full page object
    updated = {"ok": True, "slug": "about", "url": "https://user.mataroa.blog/about/"}
    with respx.mock(base_url=BASE) as mock:
        mock.patch("/pages/about/").mock(return_value=httpx.Response(200, json=updated))
        result = await client.update_page("about", {"body": "New bio.", "is_hidden": True})
    assert result["ok"] is True
    assert result["slug"] == "about"


@pytest.mark.asyncio
async def test_delete_page(client):
    with respx.mock(base_url=BASE) as mock:
        mock.delete("/pages/about/").mock(return_value=httpx.Response(200, json={"ok": True}))
        result = await client.delete_page("about")
    assert result["ok"] is True


# ── Error handling ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_401_returns_auth_error(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/posts/").mock(return_value=httpx.Response(401, json={"detail": "Unauthorized"}))
        result = await client.list_posts()
    assert result["ok"] is False
    assert "MATAROA_API_KEY" in result["error"]


@pytest.mark.asyncio
async def test_500_returns_server_error(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/posts/").mock(return_value=httpx.Response(500, json={"detail": "oops"}))
        result = await client.list_posts()
    assert result["ok"] is False
    assert "500" in result["error"]


@pytest.mark.asyncio
async def test_malformed_json_returns_graceful_error(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/posts/").mock(return_value=httpx.Response(200, content=b"not json"))
        result = await client.list_posts()
    assert result["ok"] is False
    assert "non-JSON" in result["error"]


@pytest.mark.asyncio
async def test_network_timeout_returns_error(client):
    with respx.mock(base_url=BASE) as mock:
        mock.get("/posts/").mock(side_effect=httpx.TimeoutException("timed out"))
        try:
            result = await client.list_posts()
            assert result["ok"] is False
        except httpx.TimeoutException:
            # Acceptable — caller (server.py tools) will catch this
            pass
