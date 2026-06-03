"""Shared fixtures for the Mataroa MCP test suite."""

import pytest
from mataroa_mcp.client import MataroaClient


@pytest.fixture
def client():
    return MataroaClient(api_key="test-key")


# ── Sample API payloads ────────────────────────────────────────────────────────

PUBLISHED_POST = {
    "title": "Hello World",
    "slug": "hello-world",
    "body": "My first post.",
    "published_at": "2026-01-01",
    "url": "https://user.mataroa.blog/blog/hello-world/",
}

DRAFT_POST = {
    "title": "Draft Post",
    "slug": "draft-post",
    "body": "Work in progress.",
    "published_at": None,
    "url": "https://user.mataroa.blog/blog/draft-post/",
}

SECOND_PUBLISHED_POST = {
    "title": "Second Post",
    "slug": "second-post",
    "body": "Another post.",
    "published_at": "2026-02-01",
    "url": "https://user.mataroa.blog/blog/second-post/",
}

SAMPLE_COMMENT = {
    "id": 42,
    "post_slug": "hello-world",
    "post_title": "Hello World",
    "post_url": "https://user.mataroa.blog/blog/hello-world/",
    "url": "https://user.mataroa.blog/blog/hello-world/#comment-42",
    "created_at": "2026-03-01T10:00:00Z",
    "name": "Alice",
    "email": "alice@example.com",
    "body": "Great post!",
    "is_approved": False,
    "is_author": False,
}

SPAM_COMMENT = {
    "id": 43,
    "post_slug": "hello-world",
    "post_title": "Hello World",
    "post_url": "https://user.mataroa.blog/blog/hello-world/",
    "url": "https://user.mataroa.blog/blog/hello-world/#comment-43",
    "created_at": "2026-03-02T11:00:00Z",
    "name": "Spammer",
    "email": None,
    "body": "Buy cheap watches!!!",
    "is_approved": False,
    "is_author": False,
}

SAMPLE_PAGE = {
    "title": "About",
    "slug": "about",
    "body": "This is the about page.",
    "is_hidden": False,
    "url": "https://user.mataroa.blog/pages/about/",
}

HIDDEN_PAGE = {
    "title": "Secret",
    "slug": "secret",
    "body": "Hidden page.",
    "is_hidden": True,
    "url": "https://user.mataroa.blog/pages/secret/",
}


def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests against the live Mataroa API",
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-integration"):
        skip = pytest.mark.skip(reason="Pass --run-integration to run")
        for item in items:
            if "integration" in item.nodeid:
                item.add_marker(skip)
