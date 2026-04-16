"""
Google Docs and Google Drive file sources.

Supports any URL or ID that Google NotebookLM accepts as a Google source:
  • https://docs.google.com/document/d/{ID}/...   → Google Doc (text)
  • https://docs.google.com/presentation/d/{ID}/... → Google Slides (text)
  • https://drive.google.com/file/d/{ID}/...       → Drive file (PDF/text)
  • A bare document / file ID
"""
from __future__ import annotations

import re
from pathlib import Path

from .base import LoadedSource, Source

_DOC_URL_RE = re.compile(
    r"https?://docs\.google\.com/(?:document|spreadsheets|presentation)/d/([^/?#]+)"
)
_DRIVE_FILE_RE = re.compile(
    r"https?://drive\.google\.com/(?:file/d/|open\?id=)([^/?#&]+)"
)


def _extract_id(url_or_id: str) -> tuple[str, str]:
    """Return (resource_id, kind) where kind is 'doc', 'slides', or 'drive'."""
    m = _DOC_URL_RE.match(url_or_id)
    if m:
        kind = "slides" if "/presentation/" in url_or_id else "doc"
        return m.group(1), kind
    m = _DRIVE_FILE_RE.match(url_or_id)
    if m:
        return m.group(1), "drive"
    # Assume bare ID → try as Doc first
    return url_or_id.strip(), "doc"


class GoogleDocSource(Source):
    """
    Load a Google Doc (or Slide deck) into plain text via the Docs API.

    Parameters
    ----------
    url_or_id:
        A full Google Docs / Slides URL **or** just the document ID.
    credentials_file:
        Path to a service-account key or OAuth client-secrets JSON.
        Falls back to ``GOOGLE_APPLICATION_CREDENTIALS`` env var.
    token_file:
        Where to cache OAuth user tokens (default: ``token.json``).
    """

    def __init__(
        self,
        url_or_id: str,
        credentials_file: str | Path | None = None,
        token_file: str | Path = "token.json",
    ) -> None:
        self._url_or_id = url_or_id
        self._credentials_file = credentials_file
        self._token_file = token_file
        self._doc_id, self._kind = _extract_id(url_or_id)

    @property
    def title(self) -> str:
        return f"Google Doc ({self._doc_id[:12]}…)"

    def load(self) -> LoadedSource:
        from .google_auth import get_credentials

        try:
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise ImportError(
                "google-api-python-client is required.\n"
                "Install with: pip install google-api-python-client "
                "google-auth-httplib2 google-auth-oauthlib"
            ) from exc

        creds = get_credentials(
            credentials_file=self._credentials_file,
            token_file=self._token_file,
        )

        if self._kind in ("doc",):
            text, doc_title = self._load_doc(creds)
        elif self._kind == "slides":
            text, doc_title = self._load_slides(creds)
        else:
            text, doc_title = self._load_drive_file(creds)

        return LoadedSource(
            title=doc_title,
            text=text,
            source_type="google_doc",
            uri=self._url_or_id,
        )

    # ------------------------------------------------------------------
    # Loaders
    # ------------------------------------------------------------------

    def _load_doc(self, creds) -> tuple[str, str]:
        from googleapiclient.discovery import build

        service = build("docs", "v1", credentials=creds)
        doc = service.documents().get(documentId=self._doc_id).execute()
        title = doc.get("title", "Untitled Doc")

        parts: list[str] = []
        for elem in doc.get("body", {}).get("content", []):
            para = elem.get("paragraph")
            if not para:
                continue
            line = "".join(
                r.get("textRun", {}).get("content", "")
                for r in para.get("elements", [])
            )
            if line.strip():
                parts.append(line.rstrip("\n"))

        return "\n".join(parts), title

    def _load_slides(self, creds) -> tuple[str, str]:
        from googleapiclient.discovery import build

        service = build("slides", "v1", credentials=creds)
        presentation = (
            service.presentations().get(presentationId=self._doc_id).execute()
        )
        title = presentation.get("title", "Untitled Presentation")

        parts: list[str] = []
        for i, slide in enumerate(presentation.get("slides", []), 1):
            parts.append(f"\n--- Slide {i} ---")
            for elem in slide.get("pageElements", []):
                shape = elem.get("shape", {})
                text_content = shape.get("text", {})
                for te in text_content.get("textElements", []):
                    run = te.get("textRun", {})
                    content = run.get("content", "").strip()
                    if content:
                        parts.append(content)

        return "\n".join(parts), title

    def _load_drive_file(self, creds) -> tuple[str, str]:
        """Export a Drive file as plain text (works for Docs, Sheets, etc.)."""
        from googleapiclient.discovery import build
        import io

        service = build("drive", "v3", credentials=creds)
        meta = service.files().get(fileId=self._doc_id, fields="name,mimeType").execute()
        file_title = meta.get("name", "Drive File")
        mime = meta.get("mimeType", "")

        # Google Workspace types can be exported as text
        export_mime = "text/plain"
        if "spreadsheet" in mime:
            export_mime = "text/csv"

        try:
            response = (
                service.files()
                .export(fileId=self._doc_id, mimeType=export_mime)
                .execute()
            )
            if isinstance(response, bytes):
                text = response.decode("utf-8", errors="replace")
            else:
                text = str(response)
        except Exception:
            # Fall back to downloading raw content
            request = service.files().get_media(fileId=self._doc_id)
            buf = io.BytesIO()
            from googleapiclient.http import MediaIoBaseDownload

            downloader = MediaIoBaseDownload(buf, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            text = buf.getvalue().decode("utf-8", errors="replace")

        return text, file_title


class GoogleDriveSource(Source):
    """
    Load any file from Google Drive by its file ID or shareable URL.
    Thin wrapper around :class:`GoogleDocSource` with ``kind='drive'``.
    """

    def __init__(
        self,
        url_or_id: str,
        credentials_file: str | Path | None = None,
        token_file: str | Path = "token.json",
    ) -> None:
        self._inner = GoogleDocSource(
            url_or_id, credentials_file=credentials_file, token_file=token_file
        )
        self._inner._kind = "drive"

    @property
    def title(self) -> str:
        return self._inner.title

    def load(self) -> LoadedSource:
        return self._inner.load()
