"""Plain text / Markdown / raw string source."""
from __future__ import annotations

from pathlib import Path

from .base import LoadedSource, Source


class TextFileSource(Source):
    """Load a local .txt or .md file."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    @property
    def title(self) -> str:
        return self._path.stem

    def load(self) -> LoadedSource:
        if not self._path.exists():
            raise FileNotFoundError(self._path)
        text = self._path.read_text(encoding="utf-8")
        return LoadedSource(
            title=self.title,
            text=text,
            source_type="text_file",
            uri=str(self._path.resolve()),
        )


class RawTextSource(Source):
    """Use a raw string directly as a source (e.g. from clipboard or API)."""

    def __init__(self, text: str, title: str = "Inline Text") -> None:
        self._text = text
        self._title = title

    @property
    def title(self) -> str:
        return self._title

    def load(self) -> LoadedSource:
        return LoadedSource(
            title=self._title,
            text=self._text,
            source_type="raw_text",
        )
