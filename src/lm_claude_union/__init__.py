"""
lm-claude-union
===============

Direct connection between Google NotebookLM (and other sources) and Claude.

Connect any combination of sources — Google Docs, PDFs, web pages, YouTube
videos, Jupyter notebooks — then ask questions across all of them at once.

Bridges directly into real Google NotebookLM notebooks via the Drive API.

Usage::

    # --- Manual source connection ---
    from lm_claude_union import NotebookLMClaude

    conn = NotebookLMClaude(google_credentials_file="client_secret.json")
    conn.add_google_doc("https://docs.google.com/document/d/...")
    conn.add_youtube("https://youtu.be/...")
    conn.add_pdf("report.pdf")

    print(conn.query("What are the key themes across all sources?"))

    # --- Direct Google NotebookLM bridge ---
    from lm_claude_union import NotebookLMBridge

    bridge = NotebookLMBridge(credentials_file="client_secret.json")
    print(bridge.list_notebooks())

    conn = bridge.connect_notebook("My Research")
    print(conn.query("Summarise my research."))
"""

from .connector import NotebookLMClaude
from .notebooklm_bridge import NotebookLMBridge
from .notebook_parser import ParsedNotebook, parse_notebook, parse_notebooks
from .ops_assistant import OpsAssistant
from .sources import (
    AirtableTableSource,
    GoogleDocSource,
    GoogleDriveSource,
    LoadedSource,
    PDFSource,
    RawTextSource,
    Source,
    TextFileSource,
    WebSource,
    YouTubeSource,
    fetch_records,
)

__all__ = [
    # Main classes
    "NotebookLMClaude",
    "NotebookLMBridge",
    "OpsAssistant",
    # Source types
    "Source",
    "LoadedSource",
    "AirtableTableSource",
    "fetch_records",
    "GoogleDocSource",
    "GoogleDriveSource",
    "PDFSource",
    "WebSource",
    "YouTubeSource",
    "TextFileSource",
    "RawTextSource",
    # Jupyter helpers
    "ParsedNotebook",
    "parse_notebook",
    "parse_notebooks",
]
