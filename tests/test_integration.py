"""
Integration tests against the live Mataroa API.

Run with:  MATAROA_API_KEY=your-key pytest tests/test_integration.py --run-integration -v
"""

import os
import pytest
from mataroa_mcp.client import MataroaClient


@pytest.fixture
def live_client():
    key = os.environ.get("MATAROA_API_KEY", "")
    if not key:
        pytest.skip("MATAROA_API_KEY not set")
    return MataroaClient(api_key=key)


@pytest.mark.asyncio
async def test_i01_post_create_read_delete(live_client):
    created = await live_client.create_post({"title": "Integration Test Post - Delete Me"})
    assert created["ok"] is True
    slug = created["slug"]

    fetched = await live_client.get_post(slug)
    assert fetched["title"] == "Integration Test Post - Delete Me"

    deleted = await live_client.delete_post(slug)
    assert deleted["ok"] is True

    gone = await live_client.get_post(slug)
    assert gone["ok"] is False


@pytest.mark.asyncio
async def test_i02_publish_unpublish_cycle(live_client):
    created = await live_client.create_post({"title": "Publish Test - Delete Me"})
    slug = created["slug"]

    published = await live_client.update_post(slug, {"published_at": "2026-06-03"})
    assert published["published_at"] == "2026-06-03"

    unpublished = await live_client.update_post(slug, {"published_at": ""})
    assert not unpublished.get("published_at")

    await live_client.delete_post(slug)


@pytest.mark.asyncio
async def test_i03_post_update(live_client):
    created = await live_client.create_post({"title": "Update Test", "body": "Original body."})
    slug = created["slug"]

    updated = await live_client.update_post(slug, {"title": "Updated Title", "body": "New body."})
    assert updated["title"] == "Updated Title"

    fetched = await live_client.get_post(slug)
    assert fetched["body"] == "New body."

    await live_client.delete_post(slug)


@pytest.mark.asyncio
async def test_i04_page_crud(live_client):
    created = await live_client.create_page({"title": "Test Page", "slug": "test-page-integ"})
    assert created["ok"] is True

    fetched = await live_client.get_page("test-page-integ")
    assert fetched["title"] == "Test Page"

    updated = await live_client.update_page("test-page-integ", {"body": "Updated body."})
    assert updated["ok"] is True

    pages = await live_client.list_pages()
    slugs = [p["slug"] for p in pages.get("page_list", [])]
    assert "test-page-integ" in slugs

    await live_client.delete_page("test-page-integ")


@pytest.mark.asyncio
async def test_i05_list_drafts_filtering(live_client):
    draft = await live_client.create_post({"title": "Draft Integration Test"})
    published = await live_client.create_post({
        "title": "Published Integration Test",
        "published_at": "2026-06-03",
    })
    draft_slug = draft["slug"]
    published_slug = published["slug"]

    all_posts = await live_client.list_posts()
    all_slugs = [p["slug"] for p in all_posts.get("post_list", [])]
    assert draft_slug in all_slugs
    assert published_slug in all_slugs

    # Verify draft has no published_at
    draft_fetched = await live_client.get_post(draft_slug)
    assert not draft_fetched.get("published_at")

    await live_client.delete_post(draft_slug)
    await live_client.delete_post(published_slug)
