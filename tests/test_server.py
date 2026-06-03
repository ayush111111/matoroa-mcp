"""Unit tests for MCP tool handlers in server.py — mock the MataroaClient."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import (
    PUBLISHED_POST, DRAFT_POST, SECOND_PUBLISHED_POST,
    SAMPLE_COMMENT, SPAM_COMMENT, SAMPLE_PAGE,
)


def _patch_client(return_value: dict):
    """Context manager that patches _get_client() to return a pre-configured mock."""
    mock_client = AsyncMock()
    for method in [
        "list_posts", "get_post", "create_post", "update_post", "delete_post",
        "list_comments", "list_comments_for_post", "list_pending_comments",
        "approve_comment", "delete_comment",
        "list_pages", "get_page", "create_page", "update_page", "delete_page",
    ]:
        getattr(mock_client, method).return_value = return_value
    return patch("mataroa_mcp.server._get_client", return_value=mock_client), mock_client


# ── Posts ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_tool_list_posts():
    from mataroa_mcp import server
    posts = [PUBLISHED_POST, SECOND_PUBLISHED_POST, DRAFT_POST]
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.list_posts.return_value = {"ok": True, "post_list": posts}
        mock_factory.return_value = mock_client
        result = await server.list_posts()
    assert len(result["post_list"]) == 3


@pytest.mark.asyncio
async def test_tool_list_drafts_filters_correctly():
    from mataroa_mcp import server
    posts = [PUBLISHED_POST, SECOND_PUBLISHED_POST, DRAFT_POST]
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.list_posts.return_value = {"ok": True, "post_list": posts}
        mock_factory.return_value = mock_client
        result = await server.list_drafts()
    assert len(result["post_list"]) == 1
    assert result["post_list"][0]["slug"] == "draft-post"


@pytest.mark.asyncio
async def test_tool_get_post():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.get_post.return_value = {**PUBLISHED_POST, "ok": True}
        mock_factory.return_value = mock_client
        result = await server.get_post("hello-world")
    mock_client.get_post.assert_called_once_with("hello-world")
    assert result["slug"] == "hello-world"


@pytest.mark.asyncio
async def test_tool_get_post_not_found():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.get_post.return_value = {"ok": False, "error": "Resource not found."}
        mock_factory.return_value = mock_client
        result = await server.get_post("no-such")
    assert result["ok"] is False


@pytest.mark.asyncio
async def test_tool_create_post_title_only():
    from mataroa_mcp import server
    created = {"ok": True, "slug": "draft-post", "url": "https://user.mataroa.blog/blog/draft-post/"}
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.create_post.return_value = created
        mock_factory.return_value = mock_client
        result = await server.create_post(title="Draft Post")
    mock_client.create_post.assert_called_once_with({"title": "Draft Post"})
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_tool_create_post_with_all_fields():
    from mataroa_mcp import server
    created = {**PUBLISHED_POST, "ok": True}
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.create_post.return_value = created
        mock_factory.return_value = mock_client
        result = await server.create_post(
            title="Hello World", body="Content", published_at="2026-01-01"
        )
    call_payload = mock_client.create_post.call_args[0][0]
    assert call_payload["published_at"] == "2026-01-01"
    assert call_payload["body"] == "Content"


@pytest.mark.asyncio
async def test_tool_create_post_missing_title():
    from mataroa_mcp import server
    result = await server.create_post(title="")
    assert result["ok"] is False
    assert "title" in result["error"].lower()


@pytest.mark.asyncio
async def test_tool_update_post_body_only():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.update_post.return_value = {"ok": True, "slug": "hello-world", "url": "https://user.mataroa.blog/blog/hello-world/"}
        mock_factory.return_value = mock_client
        result = await server.update_post("hello-world", body="New")
    mock_client.update_post.assert_called_once_with("hello-world", {"body": "New"})


@pytest.mark.asyncio
async def test_tool_update_post_slug_change():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.update_post.return_value = {"ok": True, "slug": "new-slug"}
        mock_factory.return_value = mock_client
        await server.update_post("hello-world", new_slug="new-slug")
    call_payload = mock_client.update_post.call_args[0][1]
    assert call_payload["slug"] == "new-slug"


@pytest.mark.asyncio
async def test_tool_delete_post():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.delete_post.return_value = {"ok": True}
        mock_factory.return_value = mock_client
        result = await server.delete_post("hello-world")
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_tool_publish_post_no_date(monkeypatch):
    from mataroa_mcp import server
    import mataroa_mcp.server as srv_module
    from datetime import date

    monkeypatch.setattr("mataroa_mcp.server.date", type("date", (), {"today": staticmethod(lambda: date(2026, 6, 3))})())

    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.update_post.return_value = {"ok": True}
        mock_factory.return_value = mock_client
        result = await server.publish_post("draft-post")
    call_payload = mock_client.update_post.call_args[0][1]
    assert call_payload["published_at"] == "2026-06-03"


@pytest.mark.asyncio
async def test_tool_publish_post_explicit_date():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.update_post.return_value = {"ok": True}
        mock_factory.return_value = mock_client
        await server.publish_post("draft-post", publish_date="2026-12-25")
    call_payload = mock_client.update_post.call_args[0][1]
    assert call_payload["published_at"] == "2026-12-25"


@pytest.mark.asyncio
async def test_tool_unpublish_post():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.update_post.return_value = {"ok": True}
        mock_factory.return_value = mock_client
        await server.unpublish_post("hello-world")
    call_payload = mock_client.update_post.call_args[0][1]
    assert call_payload["published_at"] == ""


# ── Comments ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_tool_list_comments_no_args():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.list_comments.return_value = {"ok": True, "comment_list": [SAMPLE_COMMENT]}
        mock_factory.return_value = mock_client
        result = await server.list_comments()
    mock_client.list_comments.assert_called_once()
    mock_client.list_comments_for_post.assert_not_called()


@pytest.mark.asyncio
async def test_tool_list_comments_with_post_slug():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.list_comments_for_post.return_value = {"ok": True, "comment_list": [SAMPLE_COMMENT]}
        mock_factory.return_value = mock_client
        result = await server.list_comments(post_slug="hello-world")
    mock_client.list_comments_for_post.assert_called_once_with("hello-world")


@pytest.mark.asyncio
async def test_tool_list_pending_comments():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.list_pending_comments.return_value = {
            "ok": True, "comment_list": [SAMPLE_COMMENT, SPAM_COMMENT]
        }
        mock_factory.return_value = mock_client
        result = await server.list_pending_comments()
    assert len(result["comment_list"]) == 2


@pytest.mark.asyncio
async def test_tool_approve_comment():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.approve_comment.return_value = {"ok": True, "comment": {**SAMPLE_COMMENT, "is_approved": True}}
        mock_factory.return_value = mock_client
        result = await server.approve_comment(42)
    mock_client.approve_comment.assert_called_once_with(42)
    assert result["comment"]["is_approved"] is True


@pytest.mark.asyncio
async def test_tool_delete_comment():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.delete_comment.return_value = {"ok": True}
        mock_factory.return_value = mock_client
        result = await server.delete_comment(43)
    assert result["ok"] is True


# ── Pages ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_tool_list_pages():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.list_pages.return_value = {"ok": True, "page_list": [SAMPLE_PAGE]}
        mock_factory.return_value = mock_client
        result = await server.list_pages()
    assert len(result["page_list"]) == 1


@pytest.mark.asyncio
async def test_tool_get_page():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.get_page.return_value = {**SAMPLE_PAGE, "ok": True}
        mock_factory.return_value = mock_client
        result = await server.get_page("about")
    mock_client.get_page.assert_called_once_with("about")


@pytest.mark.asyncio
async def test_tool_create_page_title_and_slug():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.create_page.return_value = {**SAMPLE_PAGE, "ok": True}
        mock_factory.return_value = mock_client
        result = await server.create_page(title="About", slug="about")
    call_payload = mock_client.create_page.call_args[0][0]
    assert call_payload["title"] == "About"
    assert call_payload["slug"] == "about"


@pytest.mark.asyncio
async def test_tool_create_page_missing_slug():
    from mataroa_mcp import server
    result = await server.create_page(title="About", slug="")
    assert result["ok"] is False
    assert "slug" in result["error"].lower()


@pytest.mark.asyncio
async def test_tool_update_page_body_and_hidden():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.update_page.return_value = {"ok": True}
        mock_factory.return_value = mock_client
        await server.update_page("about", body="New bio.", is_hidden=True)
    call_payload = mock_client.update_page.call_args[0][1]
    assert call_payload["body"] == "New bio."
    assert call_payload["is_hidden"] is True


@pytest.mark.asyncio
async def test_tool_delete_page():
    from mataroa_mcp import server
    with patch.object(server, "_get_client") as mock_factory:
        mock_client = AsyncMock()
        mock_client.delete_page.return_value = {"ok": True}
        mock_factory.return_value = mock_client
        result = await server.delete_page("about")
    assert result["ok"] is True
