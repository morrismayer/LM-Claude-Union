"""
NotebookLMClaude — connect any combination of sources to Claude and query them.

Supported sources (same set as Google NotebookLM):
  • Google Docs / Slides
  • Google Drive files
  • PDFs (local or URL)
  • Web pages (public URL)
  • YouTube videos (transcript)
  • Jupyter notebooks (.ipynb)
  • Plain text / Markdown files
  • Raw strings

Quick start
-----------
::

    from lm_claude_union import NotebookLMClaude

    conn = NotebookLMClaude()
    conn.add_google_doc("https://docs.google.com/document/d/...")
    conn.add_youtube("https://youtu.be/dQw4w9WgXcQ")
    conn.add_pdf("report.pdf")

    print(conn.query("What are the key themes?"))
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .claude_client import ClaudeClient
from .notebook_parser import parse_notebook
from .sources.base import LoadedSource, Source
from .sources.google_docs import GoogleDocSource, GoogleDriveSource
from .sources.pdf import PDFSource
from .sources.text import RawTextSource, TextFileSource
from .sources.web import WebSource
from .sources.youtube import YouTubeSource


class NotebookLMClaude:
    """
    A session that connects one or more sources to Claude.

    Sources are loaded lazily on the first :meth:`query` call (or explicitly
    via :meth:`load_sources`) so you can build the source list without
    incurring network / file IO costs immediately.

    Parameters
    ----------
    api_key:
        Anthropic API key.  Falls back to the ``ANTHROPIC_API_KEY`` env var.
    model:
        Claude model ID (default: ``claude-sonnet-4-6``).
    max_tokens:
        Max tokens for Claude's reply.
    system:
        Custom system prompt.
    google_credentials_file:
        Path to a Google OAuth client-secrets or service-account JSON.
        Required only when using Google Docs / Drive sources.
    google_token_file:
        Where to cache Google OAuth user tokens (default: ``token.json``).
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 8192,
        system: str | None = None,
        google_credentials_file: str | Path | None = None,
        google_token_file: str | Path = "token.json",
    ) -> None:
        self._client = ClaudeClient(api_key=api_key, model=model, max_tokens=max_tokens)
        self._system = system
        self._google_creds = google_credentials_file
        self._google_token = google_token_file
        self._sources: list[Source] = []
        self._loaded: list[LoadedSource] | None = None  # cache after first load

    # ------------------------------------------------------------------
    # Add sources
    # ------------------------------------------------------------------

    def add_source(self, source: Source) -> "NotebookLMClaude":
        """Add any :class:`~lm_claude_union.sources.Source` instance."""
        self._sources.append(source)
        self._loaded = None  # invalidate cache
        return self

    def add_google_doc(self, url_or_id: str) -> "NotebookLMClaude":
        """Add a Google Doc or Slides deck by URL or document ID."""
        return self.add_source(
            GoogleDocSource(
                url_or_id,
                credentials_file=self._google_creds,
                token_file=self._google_token,
            )
        )

    def add_google_drive_file(self, url_or_id: str) -> "NotebookLMClaude":
        """Add any Google Drive file (Docs, Sheets, PDF, text) by URL or file ID."""
        return self.add_source(
            GoogleDriveSource(
                url_or_id,
                credentials_file=self._google_creds,
                token_file=self._google_token,
            )
        )

    def add_pdf(self, path_or_url: str) -> "NotebookLMClaude":
        """Add a local PDF file or a public PDF URL."""
        return self.add_source(PDFSource(path_or_url))

    def add_url(self, url: str) -> "NotebookLMClaude":
        """Add a public web page."""
        return self.add_source(WebSource(url))

    def add_youtube(self, url_or_id: str, language: str = "en") -> "NotebookLMClaude":
        """Add a YouTube video (fetches its transcript)."""
        return self.add_source(YouTubeSource(url_or_id, language=language))

    def add_notebook(self, path: str | Path) -> "NotebookLMClaude":
        """Add a Jupyter notebook (.ipynb)."""
        nb = parse_notebook(path)
        return self.add_source(RawTextSource(nb.text, title=nb.title))

    def add_text_file(self, path: str | Path) -> "NotebookLMClaude":
        """Add a plain text or Markdown file."""
        return self.add_source(TextFileSource(path))

    def add_text(self, text: str, title: str = "Inline Text") -> "NotebookLMClaude":
        """Add a raw string as a source."""
        return self.add_source(RawTextSource(text, title=title))

    def remove_source(self, index: int) -> "NotebookLMClaude":
        """Remove a source by its index in :attr:`sources`."""
        self._sources.pop(index)
        self._loaded = None
        return self

    def clear(self) -> "NotebookLMClaude":
        """Remove all sources."""
        self._sources = []
        self._loaded = None
        return self

    # ------------------------------------------------------------------
    # Load & query
    # ------------------------------------------------------------------

    def load_sources(self) -> list[LoadedSource]:
        """
        Explicitly fetch/parse all sources and return the loaded list.

        Called automatically by :meth:`query` if not already done.
        Subsequent calls return the cached result.
        """
        if self._loaded is None:
            self._loaded = [s.load() for s in self._sources]
        return self._loaded

    def query(self, question: str, *, stream: bool = False) -> str | Iterator[str]:
        """
        Ask Claude a question across all connected sources.

        Parameters
        ----------
        question:
            The question to ask.
        stream:
            Return a token-by-token iterator when ``True``.

        Raises
        ------
        RuntimeError
            If no sources have been added.
        """
        if not self._sources:
            raise RuntimeError(
                "No sources connected.  Call add_google_doc(), add_pdf(), "
                "add_url(), add_youtube(), add_notebook(), or add_text() first."
            )
        context = self._build_context()
        return self._client.query(
            question, context, system=self._system, stream=stream
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def sources(self) -> list[Source]:
        return list(self._sources)

    @property
    def source_titles(self) -> list[str]:
        return [s.title for s in self._sources]

    def __len__(self) -> int:
        return len(self._sources)

    def __repr__(self) -> str:
        titles = ", ".join(repr(t) for t in self.source_titles)
        return f"NotebookLMClaude([{titles}])"

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "NotebookLMClaude":
        return self

    def __exit__(self, *_: object) -> None:
        self.clear()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_context(self) -> str:
        loaded = self.load_sources()
        sep = "\n\n" + "─" * 60 + "\n\n"
        intro = (
            f"The following {len(loaded)} source(s) are provided as your "
            "knowledge base:\n\n"
        )
        parts: list[str] = []
        for ls in loaded:
            header = f"=== {ls.title} [{ls.source_type}] ===\n"
            parts.append(header + ls.text)
        return intro + sep.join(parts)
