"""
NotebookLMClaude — connect one or many Jupyter notebooks to Claude.

Quick start
-----------
::

    from lm_claude_union import NotebookLMClaude

    # Single notebook
    with NotebookLMClaude("analysis.ipynb") as nb:
        print(nb.query("What datasets were used?"))

    # Multiple notebooks
    conn = NotebookLMClaude()
    conn.connect_many(["intro.ipynb", "results.ipynb", "discussion.ipynb"])
    print(conn.query("Summarise the key findings across all notebooks."))
    conn.clear()
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .claude_client import ClaudeClient
from .notebook_parser import ParsedNotebook, parse_notebook, parse_notebooks


class NotebookLMClaude:
    """
    A session that connects one or more Jupyter notebooks to Claude.

    Notebooks are parsed once on connection; their full text is sent to
    Claude as a prompt-cached context block, so repeated queries against
    the same set of notebooks are efficient.

    Parameters
    ----------
    *notebooks:
        Zero or more notebook paths to connect immediately.
    api_key:
        Anthropic API key.  Falls back to the ``ANTHROPIC_API_KEY``
        environment variable when omitted.
    model:
        Claude model ID to use.
    max_tokens:
        Maximum tokens for Claude's response.
    system:
        Custom system prompt.  When ``None`` the default assistant prompt
        is used (see :class:`ClaudeClient`).
    """

    def __init__(
        self,
        *notebooks: str | Path,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 8192,
        system: str | None = None,
    ) -> None:
        self._client = ClaudeClient(api_key=api_key, model=model, max_tokens=max_tokens)
        self._system = system
        self._notebooks: list[ParsedNotebook] = []

        if notebooks:
            self.connect_many(list(notebooks))

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self, path: str | Path) -> "NotebookLMClaude":
        """
        Connect a single notebook.

        Raises :exc:`FileNotFoundError` if the path does not exist.
        Returns *self* so calls can be chained.
        """
        nb = parse_notebook(path)
        self._notebooks.append(nb)
        return self

    def connect_many(self, paths: list[str | Path]) -> "NotebookLMClaude":
        """
        Connect multiple notebooks at once.

        Returns *self* so calls can be chained.
        """
        self._notebooks.extend(parse_notebooks(paths))
        return self

    def disconnect(self, path: str | Path) -> "NotebookLMClaude":
        """Remove a specific notebook from the session by path."""
        resolved = str(Path(path).resolve())
        self._notebooks = [nb for nb in self._notebooks if nb.path != resolved]
        return self

    def clear(self) -> "NotebookLMClaude":
        """Disconnect all notebooks."""
        self._notebooks = []
        return self

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(self, question: str, *, stream: bool = False) -> str | Iterator[str]:
        """
        Ask Claude a question about the connected notebooks.

        Parameters
        ----------
        question:
            The question to ask.
        stream:
            When ``True``, return a token-by-token :class:`~typing.Iterator`
            instead of the complete answer string.

        Raises
        ------
        RuntimeError
            If no notebooks are connected.
        """
        if not self._notebooks:
            raise RuntimeError(
                "No notebooks connected. Call connect() or connect_many() first."
            )

        context = self._build_context()
        return self._client.query(
            question, context, system=self._system, stream=stream
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def notebooks(self) -> list[ParsedNotebook]:
        """List of currently connected notebooks (read-only copy)."""
        return list(self._notebooks)

    @property
    def notebook_titles(self) -> list[str]:
        """Titles of all connected notebooks."""
        return [nb.title for nb in self._notebooks]

    def __len__(self) -> int:
        return len(self._notebooks)

    def __repr__(self) -> str:
        titles = ", ".join(repr(t) for t in self.notebook_titles)
        return f"NotebookLMClaude([{titles}])"

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "NotebookLMClaude":
        return self

    def __exit__(self, *_: object) -> None:
        self.clear()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_context(self) -> str:
        """Concatenate all notebook texts into a single context string."""
        sep = "\n\n" + "─" * 60 + "\n\n"
        intro = (
            f"The following {len(self._notebooks)} notebook(s) are provided as "
            "your knowledge base:\n\n"
        )
        body = sep.join(nb.text for nb in self._notebooks)
        return intro + body
