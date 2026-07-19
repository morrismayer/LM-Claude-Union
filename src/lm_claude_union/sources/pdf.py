"""PDF source — local file or remote URL."""
from __future__ import annotations

from pathlib import Path

from .base import LoadedSource, Source


class PDFSource(Source):
    """
    Extract text from a PDF file.

    Parameters
    ----------
    path_or_url:
        A local filesystem path **or** an ``http(s)://`` URL to a PDF.
    """

    def __init__(self, path_or_url: str) -> None:
        self._path_or_url = path_or_url

    @property
    def title(self) -> str:
        if self._path_or_url.startswith("http"):
            return self._path_or_url.split("/")[-1].split("?")[0] or "Remote PDF"
        return Path(self._path_or_url).stem

    def load(self) -> LoadedSource:
        try:
            import pypdf
        except ImportError as exc:
            raise ImportError(
                "pypdf is required for PDF sources.\n"
                "Install with: pip install pypdf"
            ) from exc

        if self._path_or_url.startswith("http"):
            import io
            import urllib.request

            with urllib.request.urlopen(self._path_or_url) as resp:  # noqa: S310
                data = resp.read()
            reader = pypdf.PdfReader(io.BytesIO(data))
        else:
            reader = pypdf.PdfReader(self._path_or_url)

        pages: list[str] = []
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"[Page {i}]\n{text.strip()}")

        return LoadedSource(
            title=self.title,
            text="\n\n".join(pages),
            source_type="pdf",
            uri=self._path_or_url,
        )
