"""Mataroa MCP server — all 17 tool handlers."""

from __future__ import annotations

import os
import sys
from datetime import date
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .client import MataroaClient

# ── Initialisation ─────────────────────────────────────────────────────────────

_API_KEY_ENV = "MATAROA_API_KEY"


def _get_client() -> MataroaClient:
    api_key = os.environ.get(_API_KEY_ENV, "").strip()
    if not api_key:
        print(
            f"ERROR: {_API_KEY_ENV} environment variable is not set. "
            "Please set it to your Mataroa API key before starting the server.",
            file=sys.stderr,
        )
        sys.exit(1)
    return MataroaClient(api_key)


mcp = FastMCP("mataroa")


def _client() -> MataroaClient:
    return _get_client()


# ── Posts ──────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_posts() -> dict[str, Any]:
    """List all blog posts (both published and drafts)."""
    return await _client().list_posts()


@mcp.tool()
async def list_drafts() -> dict[str, Any]:
    """List only unpublished draft posts (where published_at is null)."""
    result = await _client().list_posts()
    if not result.get("ok", True):
        return result
    posts = result.get("post_list", [])
    drafts = [p for p in posts if not p.get("published_at")]
    return {"ok": True, "post_list": drafts}


@mcp.tool()
async def get_post(slug: str) -> dict[str, Any]:
    """Get a single blog post by its slug."""
    return await _client().get_post(slug)


@mcp.tool()
async def create_post(
    title: str,
    body: Optional[str] = None,
    published_at: Optional[str] = None,
) -> dict[str, Any]:
    """
    Create a new blog post.

    - title: required, the post headline
    - body: optional markdown content
    - published_at: optional ISO date string (YYYY-MM-DD); omit to save as draft
    """
    if not title or not title.strip():
        return {"ok": False, "error": "title is required and cannot be empty."}
    payload: dict[str, Any] = {"title": title.strip()}
    if body is not None:
        payload["body"] = body
    if published_at is not None:
        payload["published_at"] = published_at
    return await _client().create_post(payload)


@mcp.tool()
async def update_post(
    slug: str,
    title: Optional[str] = None,
    new_slug: Optional[str] = None,
    body: Optional[str] = None,
    published_at: Optional[str] = None,
) -> dict[str, Any]:
    """
    Update an existing blog post.

    - slug: the current slug of the post to update
    - title, new_slug, body, published_at: fields to change (all optional)
    """
    payload: dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if new_slug is not None:
        payload["slug"] = new_slug
    if body is not None:
        payload["body"] = body
    if published_at is not None:
        payload["published_at"] = published_at
    if not payload:
        return {"ok": False, "error": "No fields provided to update."}
    return await _client().update_post(slug, payload)


@mcp.tool()
async def delete_post(slug: str) -> dict[str, Any]:
    """Permanently delete a blog post by its slug."""
    return await _client().delete_post(slug)


@mcp.tool()
async def publish_post(slug: str, publish_date: Optional[str] = None) -> dict[str, Any]:
    """
    Publish a draft post.

    - slug: the post slug
    - publish_date: ISO date string (YYYY-MM-DD); defaults to today
    """
    target_date = publish_date or date.today().isoformat()
    return await _client().update_post(slug, {"published_at": target_date})


@mcp.tool()
async def unpublish_post(slug: str) -> dict[str, Any]:
    """Revert a published post back to draft status."""
    return await _client().update_post(slug, {"published_at": ""})


# ── Comments ───────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_comments(post_slug: Optional[str] = None) -> dict[str, Any]:
    """
    List comments. If post_slug is provided, returns only comments for that post.
    Otherwise returns all comments across the blog.
    """
    if post_slug:
        return await _client().list_comments_for_post(post_slug)
    return await _client().list_comments()


@mcp.tool()
async def list_pending_comments() -> dict[str, Any]:
    """List comments awaiting approval."""
    return await _client().list_pending_comments()


@mcp.tool()
async def approve_comment(comment_id: int) -> dict[str, Any]:
    """Approve a pending comment by its ID."""
    return await _client().approve_comment(comment_id)


@mcp.tool()
async def delete_comment(comment_id: int) -> dict[str, Any]:
    """Permanently delete a comment by its ID."""
    return await _client().delete_comment(comment_id)


# ── Pages ──────────────────────────────────────────────────────────────────────


@mcp.tool()
async def list_pages() -> dict[str, Any]:
    """List all pages on the blog."""
    return await _client().list_pages()


@mcp.tool()
async def get_page(slug: str) -> dict[str, Any]:
    """Get a single page by its slug."""
    return await _client().get_page(slug)


@mcp.tool()
async def create_page(
    title: str,
    slug: str,
    body: Optional[str] = None,
    is_hidden: bool = False,
) -> dict[str, Any]:
    """
    Create a new page.

    - title: required
    - slug: required, URL-safe identifier (e.g. "about")
    - body: optional markdown content
    - is_hidden: if true, the page link won't appear in the blog header
    """
    if not title or not title.strip():
        return {"ok": False, "error": "title is required and cannot be empty."}
    if not slug or not slug.strip():
        return {"ok": False, "error": "slug is required and cannot be empty."}
    payload: dict[str, Any] = {
        "title": title.strip(),
        "slug": slug.strip(),
        "is_hidden": is_hidden,
    }
    if body is not None:
        payload["body"] = body
    return await _client().create_page(payload)


@mcp.tool()
async def update_page(
    slug: str,
    title: Optional[str] = None,
    new_slug: Optional[str] = None,
    body: Optional[str] = None,
    is_hidden: Optional[bool] = None,
) -> dict[str, Any]:
    """
    Update an existing page.

    - slug: current slug of the page
    - title, new_slug, body, is_hidden: fields to update (all optional)
    """
    payload: dict[str, Any] = {}
    if title is not None:
        payload["title"] = title
    if new_slug is not None:
        payload["slug"] = new_slug
    if body is not None:
        payload["body"] = body
    if is_hidden is not None:
        payload["is_hidden"] = is_hidden
    if not payload:
        return {"ok": False, "error": "No fields provided to update."}
    return await _client().update_page(slug, payload)


@mcp.tool()
async def delete_page(slug: str) -> dict[str, Any]:
    """Permanently delete a page by its slug."""
    return await _client().delete_page(slug)


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    _get_client()
    mcp.run()  # Use default stdio transport


if __name__ == "__main__":
    main()
