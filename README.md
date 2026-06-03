# mataroa-mcp

An MCP server that lets you manage your [Mataroa](https://mataroa.blog) blog through natural language in Claude Desktop, Claude Code, or any MCP-compatible AI client.

---

## What you can do

Tell Claude things like:

- *"Show me all my blog posts"*
- *"Write a post about my weekend hike and save it as a draft"*
- *"Publish my sourdough post"*
- *"Are there any comments waiting for approval?"*
- *"Delete the draft called testing-123"*
- *"Create an About page for my blog"*

Claude will call the right tool automatically.

---

## Setup (5 minutes)

### 1. Get your Mataroa API key

1. Go to [mataroa.blog](https://mataroa.blog) and log in (or create a free account).
2. Open **Dashboard → API** and copy your API key.

### 2. Install the server

You need Python 3.10 or later. If you have [`uv`](https://github.com/astral-sh/uv) installed (recommended):

```bash
uvx mataroa-mcp
```

Or install with pip:

```bash
pip install mataroa-mcp
```

### 3. Add to Claude Desktop

Open your Claude Desktop config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the `mataroa` entry inside `"mcpServers"`:

```json
{
  "mcpServers": {
    "mataroa": {
      "command": "uvx",
      "args": ["mataroa-mcp"],
      "env": {
        "MATAROA_API_KEY": "paste-your-key-here"
      }
    }
  }
}
```

If you used `pip install` instead of `uvx`, replace `"command": "uvx"` and `"args": ["mataroa-mcp"]` with:

```json
"command": "mataroa-mcp",
"args": []
```

### 4. Restart Claude Desktop

Quit and reopen Claude Desktop. You should see a small plug icon in the chat bar indicating MCP tools are active.

### 5. Test it

Type: *"Show me my blog posts"* — Claude should list them.

---

## Add to Claude Code

Create or edit `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "mataroa": {
      "command": "uvx",
      "args": ["mataroa-mcp"],
      "env": {
        "MATAROA_API_KEY": "paste-your-key-here"
      }
    }
  }
}
```

---

## Available tools

| Tool | What it does |
|------|-------------|
| `list_posts` | List all posts (published + drafts) |
| `list_drafts` | List only unpublished drafts |
| `get_post` | Get a single post by slug |
| `create_post` | Create a new post |
| `update_post` | Edit an existing post |
| `delete_post` | Permanently delete a post |
| `publish_post` | Publish a draft (sets today's date, or a date you choose) |
| `unpublish_post` | Revert a published post back to draft |
| `list_comments` | List all comments (or just for one post) |
| `list_pending_comments` | List comments awaiting moderation |
| `approve_comment` | Approve a pending comment |
| `delete_comment` | Delete a comment |
| `list_pages` | List all pages |
| `get_page` | Get a single page by slug |
| `create_page` | Create a new page |
| `update_page` | Edit an existing page |
| `delete_page` | Permanently delete a page |

---

## Notes

- **API key is never stored in code** — it's always read from the `MATAROA_API_KEY` environment variable.
- **Mataroa has no rate limiting**, so you can make requests freely.
- **Blog-level settings** (title, custom domain, etc.) are not accessible via the Mataroa API and therefore not exposed here.
- Draft posts have `published_at: null`. Publishing sets it to a date; unpublishing clears it.

---

## Running tests

```bash
# Unit tests (no API key needed)
pip install -e ".[dev]"
pytest tests/test_client.py tests/test_server.py -v

# Integration tests (requires a real Mataroa API key)
MATAROA_API_KEY=your-key pytest tests/test_integration.py --run-integration -v
```

---

## License

MIT
