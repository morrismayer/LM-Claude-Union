# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`lm-claude-union` is a small Python library that grounds Claude API queries in
external content. It has two independent use cases living in one package:

1. **Multi-source Q&A** (`NotebookLMClaude`, `NotebookLMBridge`) — pull text
   from Google Docs/Drive, PDFs, web pages, YouTube transcripts, Jupyter
   notebooks, or raw strings into one context blob, then ask Claude questions
   grounded in all of it. `NotebookLMBridge` additionally discovers a user's
   real Google NotebookLM notebooks (stored as folders in Drive) via the Drive
   API and wires their contents into a `NotebookLMClaude` session automatically.
2. **`OpsAssistant`** — a purpose-built assistant over an Airtable job tracker
   (fabrication/workroom use case), doing deterministic aggregation (grouping,
   filtering) in Python before handing results to Claude for drafting/Q&A.

These two halves share only `ClaudeClient` (the Anthropic SDK wrapper).
`OpsAssistant` does not use the `Source`/`sources/` abstraction — it fetches
Airtable records directly via `fetch_records()` for exact, auditable logic.

## Development commands

```bash
# Install for local dev (editable install)
pip install -e ".[all]"   # includes google + youtube extras
pip install -e ".[dev]"   # pytest/pytest-asyncio, if writing tests

# Run an example script (each is a runnable smoke test for one code path)
python examples/single_notebook.py          # Jupyter notebooks only, no external creds
python examples/multi_notebook.py           # multiple notebooks in one session
python examples/google_notebooklm_bridge.py # requires client_secret.json (Google OAuth)
python examples/ops_assistant_demo.py       # requires AIRTABLE_API_KEY + ANTHROPIC_API_KEY
```

There is currently no test suite in the repo (no `tests/` directory) even
though `pytest`/`pytest-asyncio` are declared under the `dev` extra, and no
lint/format config (ruff cache is gitignored but no `ruff.toml`/config
section exists). Verify changes by running the relevant `examples/*.py`
script and/or by exercising the modified class directly in a REPL.

Required env vars depend on what you're touching:
- `ANTHROPIC_API_KEY` — always, for any `ClaudeClient`/`.query()` call.
- `AIRTABLE_API_KEY` — `AirtableTableSource`, `fetch_records()`, `OpsAssistant`.
- Google OAuth: a `client_secret.json` (or `GOOGLE_APPLICATION_CREDENTIALS`
  service-account key) is required for `GoogleDocSource`, `GoogleDriveSource`,
  and `NotebookLMBridge`; a `token.json` is written after the first
  interactive consent and reused silently after that.

## Architecture

### Source loading pipeline

Every content type implements the `Source` ABC (`sources/base.py`):
`title` (property) and `load() -> LoadedSource`, where `LoadedSource` is a
plain dataclass (`title`, `text`, `source_type`, `uri`). `NotebookLMClaude`
holds a list of `Source` instances added via `add_*` methods, loads them
lazily (on first `.query()` or explicit `.load_sources()`), caches the
loaded result until a source is added/removed, and concatenates them into
one context string in `_build_context()` (each source wrapped in
`=== title [type] ===` header, sources separated by a rule).

Adding a new source type means: create `sources/<name>.py` implementing
`Source`, export it from `sources/__init__.py` and the top-level
`lm_claude_union/__init__.py`, and add a corresponding `add_*` convenience
method on `NotebookLMClaude` (see `connector.py`).

### Claude query path

`ClaudeClient` (`claude_client.py`) is the only place that talks to the
Anthropic SDK. It splits the user turn into two content blocks — the (large)
context gets `cache_control: {"type": "ephemeral"}`, the (short) question does
not — so repeated queries against the same sources reuse Anthropic's prompt
cache instead of re-billing the full context. Both `_complete` and `_stream`
must stay in sync on this message-building logic (`_build_messages`) and the
`anthropic-beta: prompt-caching-2024-07-31` header. Default model is
`claude-sonnet-4-6`.

### `NotebookLMBridge` vs `NotebookLMClaude`

`NotebookLMBridge` is a Drive-API discovery layer, not a separate query
engine: it finds the "NotebookLM" root folder in Drive, resolves a notebook
name/ID to its Drive folder ID, filters files down to
`_SUPPORTED_MIMES` (Docs, Slides, PDF, plain text/markdown — audio/images
are skipped since NotebookLM doesn't expose their content directly), wraps
each as a `GoogleDocSource`, and returns a plain `NotebookLMClaude` with
those sources pre-added. `connect_notebooks()` (plural) is how cross-notebook
questions work — it's just multiple notebooks' files loaded into one session.

### `OpsAssistant` conventions

The Airtable base this was built for stores **one row per line item**, with
several `Item #` rows sharing a `Job #`. This shapes every method:
- `_group_by_job()` groups raw records by job number before any status
  check — filtering a checkbox field across raw line-item rows produces
  inflated/unreliable counts (a job with 5 items looks like 5 hits).
- `find_payment_mismatches()` is deliberately conservative: it only flags a
  job when **none** of its invoiced line items are marked paid, and returns
  a `caveat` string alongside results — treat its output as a worklist to
  confirm with billing, not a final answer. Don't "simplify" this to a
  per-row filter; that was tried and produces wrong results.
- Field names are overridable per-base via `field_map` merged onto
  `DEFAULT_FIELDS` (`Job #`, `Item #`, `Client/Project Name`, `Due Date`,
  `Furniture Received`, `Invoice Completed`, `Paid In Full`, `Invoice Link`) —
  when adding a new aggregate method, look up field names through `self._f(key)`
  rather than hardcoding the Airtable column name.
- `query()` and `draft_client_update()` flatten records to text via
  `_records_to_context()` and hand that to `ClaudeClient` for free-form/
  drafting tasks; the deterministic lookups (`lookup_job`,
  `find_ready_to_invoice`, `find_payment_mismatches`) never go through Claude.

### Google auth

`sources/google_auth.get_credentials()` is the single shared entry point for
both `GoogleDocSource`/`GoogleDriveSource` and `NotebookLMBridge`. It tries,
in order: a service-account key (`credentials_file` or
`GOOGLE_APPLICATION_CREDENTIALS`), a cached OAuth user token (`token_file`),
then an interactive OAuth flow that writes the token back for next time.
Don't duplicate this logic in new Google-backed sources — call it.

## Package layout

- `src/lm_claude_union/__init__.py` — public API surface; anything meant to
  be user-facing must be re-exported here (and from `sources/__init__.py` if
  it's a source type).
- `connector.py` — `NotebookLMClaude`, the multi-source session.
- `notebooklm_bridge.py` — `NotebookLMBridge`, Drive-based notebook discovery.
- `ops_assistant.py` — `OpsAssistant`, Airtable job-tracker assistant.
- `notebook_parser.py` — standalone `.ipynb` → text parser, used by both
  `NotebookLMClaude.add_notebook()` and directly from user code.
- `claude_client.py` — Anthropic SDK wrapper with prompt caching.
- `sources/` — one file per source type, all implementing `Source`.
