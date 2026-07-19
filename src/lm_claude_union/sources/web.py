"""Web URL source — fetches and strips HTML to plain text."""
from __future__ import annotations

import re
import urllib.request
from urllib.parse import urlparse

from .base import LoadedSource, Source


def _strip_html(html: str) -> str:
    """Very lightweight HTML → plain text (no BS4 dependency required)."""
    # Remove scripts and styles
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    # Replace block elements with newlines
    html = re.sub(
        r"<(br|p|div|h[1-6]|li|tr|blockquote)[^>]*>",
        "\n",
        html,
        flags=re.I,
    )
    # Strip remaining tags
    html = re.sub(r"<[^>]+>", "", html)
    # Decode common HTML entities
    for entity, char in [
        ("&amp;", "&"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&quot;", '"'),
        ("&#39;", "'"),
        ("&nbsp;", " "),
    ]:
        html = html.replace(entity, char)
    # Collapse whitespace
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


class WebSource(Source):
    """
    Fetch a public web page and extract its text content.

    Parameters
    ----------
    url:
        A public ``http(s)://`` URL — the same kind NotebookLM accepts.
    use_beautifulsoup:
        If True and ``beautifulsoup4`` is installed, use it for better
        HTML parsing.  Falls back to the built-in stripper otherwise.
    """

    def __init__(self, url: str, *, use_beautifulsoup: bool = True) -> None:
        self._url = url
        self._use_bs4 = use_beautifulsoup

    @property
    def title(self) -> str:
        parsed = urlparse(self._url)
        return parsed.netloc + parsed.path.rstrip("/")

    def load(self) -> LoadedSource:
        req = urllib.request.Request(
            self._url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LMClaudeUnion/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            raw = resp.read()
            charset = resp.headers.get_content_charset("utf-8")
            html = raw.decode(charset, errors="replace")

        page_title = self.title
        # Try to extract <title>
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
        if m:
            page_title = re.sub(r"\s+", " ", m.group(1)).strip()

        if self._use_bs4:
            try:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                text = soup.get_text(separator="\n")
                text = re.sub(r"\n{3,}", "\n\n", text).strip()
            except ImportError:
                text = _strip_html(html)
        else:
            text = _strip_html(html)

        return LoadedSource(
            title=page_title,
            text=text,
            source_type="web",
            uri=self._url,
        )
