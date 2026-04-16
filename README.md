# LM-Claude-Union

A direct connection between Jupyter notebooks and Claude.  
Connect one notebook or many at a time, then query across all of them.

---

## How it works

```
your .ipynb files
       │
       ▼
 NotebookLMClaude          ← Python session object
       │   connects / parses notebooks (markdown + code + outputs)
       │
       ▼
  Claude API               ← Anthropic claude-sonnet-4-6
  (prompt-cached context)  ← notebook text is cached server-side
       │
       ▼
   your answer
```

Notebook content is sent as a **prompt-cached** context block, so repeated
queries against the same notebook(s) hit the cache instead of re-tokenising
the full content on every request.

---

## Installation

```bash
pip install -e .
# or just install the dependencies directly
pip install anthropic nbformat
```

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## Quick start

### Single notebook

```python
from lm_claude_union import NotebookLMClaude

with NotebookLMClaude("my_analysis.ipynb") as conn:
    print(conn.query("What is the main conclusion?"))
```

### Multiple notebooks

```python
from lm_claude_union import NotebookLMClaude

conn = NotebookLMClaude("intro.ipynb", "results.ipynb", "discussion.ipynb")

print(conn.query("Summarise the key findings across all notebooks."))
print(conn.query("Which notebook discusses statistical significance?"))

conn.clear()
```

### Streaming

```python
with NotebookLMClaude("analysis.ipynb") as conn:
    for token in conn.query("Explain the methodology.", stream=True):
        print(token, end="", flush=True)
```

### Dynamic connection management

```python
conn = NotebookLMClaude()               # start empty

conn.connect("chapter1.ipynb")          # add one notebook
conn.connect_many(["ch2.ipynb", "ch3.ipynb"])  # add several

print(conn.notebook_titles)             # ['Chapter 1', 'Chapter 2', 'Chapter 3']

conn.disconnect("chapter1.ipynb")       # remove one
conn.clear()                            # remove all
```

---

## API reference

### `NotebookLMClaude(*notebooks, api_key=None, model=..., max_tokens=8192, system=None)`

| Parameter | Description |
|-----------|-------------|
| `*notebooks` | Zero or more `.ipynb` paths to connect immediately |
| `api_key` | Anthropic API key (falls back to `ANTHROPIC_API_KEY` env var) |
| `model` | Claude model ID (default: `claude-sonnet-4-6`) |
| `max_tokens` | Max tokens for Claude's reply (default: 8192) |
| `system` | Custom system prompt |

#### Methods

| Method | Description |
|--------|-------------|
| `.connect(path)` | Connect a single notebook; returns `self` |
| `.connect_many(paths)` | Connect multiple notebooks; returns `self` |
| `.disconnect(path)` | Remove a specific notebook by path; returns `self` |
| `.clear()` | Remove all notebooks; returns `self` |
| `.query(question, *, stream=False)` | Ask Claude a question; returns `str` or `Iterator[str]` |
| `.notebooks` | List of `ParsedNotebook` objects |
| `.notebook_titles` | List of notebook titles |

---

## Examples

```bash
python examples/single_notebook.py
python examples/multi_notebook.py
```

---

## Project structure

```
src/lm_claude_union/
├── __init__.py          # Public API
├── connector.py         # NotebookLMClaude session class
├── notebook_parser.py   # .ipynb → clean text converter
└── claude_client.py     # Anthropic SDK wrapper with prompt caching

examples/
├── single_notebook.py
├── multi_notebook.py
├── sample_notebook.ipynb
└── sample_notebook_2.ipynb
```
