# LM-Claude-Union

Direct connection between **Google NotebookLM** and **Claude**.  
Connect one notebook or many at a time, then query across all of them.

Supports every source type that Google NotebookLM accepts, plus a bridge
that reads directly from your real NotebookLM notebooks in Google Drive.

---

## How it works

```
Google NotebookLM notebooks (Drive)
  └── Google Docs / PDFs / Slides / text files
        │
        │  also accepts:
        ├── public web pages
        ├── YouTube videos (transcript)
        ├── local PDFs / text files
        └── Jupyter notebooks

        ▼
  NotebookLMClaude session
  (sources loaded + cached)

        ▼
  Claude API  (prompt-cached context)

        ▼
  your answer
```

---

## Installation

```bash
# Core (PDF, web, Jupyter sources)
pip install -e .

# + Google Docs / Drive / NotebookLM bridge
pip install -e ".[google]"

# + YouTube transcripts
pip install -e ".[youtube]"

# Everything
pip install -e ".[all]"
```

Set API keys:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Google NotebookLM setup (one-time)

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project → enable **Google Drive API** and **Google Docs API**.
3. Create credentials → **OAuth 2.0 Client ID** (Desktop app) → download JSON
   as `client_secret.json`.
4. The first run opens a browser for consent; a `token.json` is saved for
   subsequent silent runs.

---

## Quick start

### Bridge directly into Google NotebookLM

```python
from lm_claude_union import NotebookLMBridge

bridge = NotebookLMBridge(credentials_file="client_secret.json")

# See all your NotebookLM notebooks
for nb in bridge.list_notebooks():
    print(nb["name"], nb["id"])

# Connect one notebook → Claude answers from its sources
conn = bridge.connect_notebook("My Research")
print(conn.query("What are the main themes?"))

# Connect multiple notebooks at once
conn = bridge.connect_notebooks(["Research", "Meeting Notes", "Papers"])
print(conn.query("What topics appear across all my notebooks?"))
```

### Manual multi-source session

```python
from lm_claude_union import NotebookLMClaude

conn = NotebookLMClaude(google_credentials_file="client_secret.json")

conn.add_google_doc("https://docs.google.com/document/d/...")
conn.add_youtube("https://youtu.be/dQw4w9WgXcQ")
conn.add_pdf("report.pdf")
conn.add_url("https://example.com/article")
conn.add_notebook("analysis.ipynb")
conn.add_text("Any raw text goes here.", title="My Note")

print(conn.query("Summarise all sources."))
```

### Streaming

```python
for token in conn.query("Explain the methodology.", stream=True):
    print(token, end="", flush=True)
```

---

## API reference

### `NotebookLMBridge`

Discovers and connects to real Google NotebookLM notebooks via the Drive API.

```python
bridge = NotebookLMBridge(
    credentials_file="client_secret.json",  # Google OAuth / service-account
    token_file="token.json",                # cached OAuth token
    anthropic_api_key=None,                 # falls back to ANTHROPIC_API_KEY
    model="claude-sonnet-4-6",
)
```

| Method | Description |
|--------|-------------|
| `.list_notebooks()` | List all NotebookLM notebooks in Google Drive |
| `.list_sources(name_or_id)` | List source files inside a notebook |
| `.connect_notebook(name_or_id)` | Load one notebook → returns `NotebookLMClaude` |
| `.connect_notebooks([...])` | Load multiple notebooks → returns `NotebookLMClaude` |

---

### `NotebookLMClaude`

The query session.  Returned by `NotebookLMBridge` or built manually.

```python
conn = NotebookLMClaude(
    api_key=None,                      # ANTHROPIC_API_KEY
    model="claude-sonnet-4-6",
    max_tokens=8192,
    system=None,                       # custom system prompt
    google_credentials_file=None,
    google_token_file="token.json",
)
```

| Method | Description |
|--------|-------------|
| `.add_google_doc(url_or_id)` | Google Doc or Slides |
| `.add_google_drive_file(url_or_id)` | Any Google Drive file |
| `.add_pdf(path_or_url)` | Local PDF or public PDF URL |
| `.add_url(url)` | Public web page |
| `.add_youtube(url_or_id)` | YouTube video transcript |
| `.add_notebook(path)` | Jupyter notebook (`.ipynb`) |
| `.add_text_file(path)` | Plain text / Markdown file |
| `.add_text(text, title)` | Raw string |
| `.add_source(source)` | Any custom `Source` instance |
| `.remove_source(index)` | Remove by index |
| `.clear()` | Remove all sources |
| `.load_sources()` | Pre-fetch all sources |
| `.query(question, *, stream=False)` | Ask Claude |
| `.source_titles` | List of source titles |

---

## Examples

```bash
# Jupyter notebooks only
python examples/single_notebook.py
python examples/multi_notebook.py

# Google NotebookLM bridge (requires Google credentials)
python examples/google_notebooklm_bridge.py
```

---

## Project structure

```
src/lm_claude_union/
├── __init__.py               # Public API
├── connector.py              # NotebookLMClaude session
├── notebooklm_bridge.py      # Google NotebookLM → Claude bridge
├── notebook_parser.py        # .ipynb parser
├── claude_client.py          # Anthropic SDK + prompt caching
└── sources/
    ├── base.py               # Abstract Source
    ├── google_auth.py        # Google OAuth2 helper
    ├── google_docs.py        # Google Docs / Drive / Slides
    ├── pdf.py                # PDF (local or URL)
    ├── web.py                # Web page
    ├── youtube.py            # YouTube transcript
    └── text.py               # Plain text / Markdown / raw string

examples/
├── google_notebooklm_bridge.py
├── single_notebook.py
├── multi_notebook.py
├── sample_notebook.ipynb
└── sample_notebook_2.ipynb
```
