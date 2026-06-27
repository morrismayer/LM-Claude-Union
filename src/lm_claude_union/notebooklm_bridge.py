"""
NotebookLMBridge — discover and connect to real Google NotebookLM notebooks.

Google NotebookLM stores notebooks as folders in the user's Google Drive
(under "NotebookLM" in My Drive).  This bridge uses the Drive API to:

  1. List all of a user's NotebookLM notebooks.
  2. Load the source documents from a given notebook.
  3. Feed those sources to Claude, enabling "communication" with the same
     knowledge that NotebookLM has.

Usage
-----
::

    from lm_claude_union import NotebookLMBridge

    bridge = NotebookLMBridge(credentials_file="client_secret.json")

    # List available notebooks
    for nb in bridge.list_notebooks():
        print(nb["name"], nb["id"])

    # Connect one notebook by name or Drive folder ID
    conn = bridge.connect_notebook("My Research")
    print(conn.query("What are the main themes across my sources?"))

    # Connect multiple notebooks
    conn = bridge.connect_notebooks(["Research", "Meeting Notes"])
    print(conn.query("Summarise everything."))
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .connector import NotebookLMClaude
from .sources.google_auth import get_credentials
from .sources.google_docs import GoogleDocSource


# MIME types Google NotebookLM source documents can be
_SUPPORTED_MIMES = {
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.presentation",
    "application/pdf",
    "text/plain",
    "text/markdown",
}

# The root folder name NotebookLM uses in Google Drive
_NOTEBOOKLM_ROOT = "NotebookLM"


class NotebookLMBridge:
    """
    Discover Google NotebookLM notebooks via the Drive API and feed their
    sources to Claude.

    Parameters
    ----------
    credentials_file:
        Path to a Google OAuth client-secrets JSON or service-account key.
        Falls back to ``GOOGLE_APPLICATION_CREDENTIALS`` env var.
    token_file:
        Where to cache the OAuth user token between runs.
    anthropic_api_key:
        Anthropic API key.  Falls back to ``ANTHROPIC_API_KEY`` env var.
    model:
        Claude model ID.
    """

    def __init__(
        self,
        credentials_file: str | Path | None = None,
        token_file: str | Path = "token.json",
        anthropic_api_key: str | None = None,
        model: str = "claude-sonnet-4-6",
    ) -> None:
        self._credentials_file = credentials_file
        self._token_file = token_file
        self._anthropic_api_key = anthropic_api_key
        self._model = model
        self._drive = None  # lazy

    # ------------------------------------------------------------------
    # Drive helpers
    # ------------------------------------------------------------------

    def _get_drive(self):
        if self._drive is not None:
            return self._drive
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
        self._drive = build("drive", "v3", credentials=creds)
        return self._drive

    def _find_notebooklm_root(self) -> str | None:
        """Return the Drive folder ID of the 'NotebookLM' root folder."""
        drive = self._get_drive()
        query = (
            f"name = '{_NOTEBOOKLM_ROOT}' "
            "and mimeType = 'application/vnd.google-apps.folder' "
            "and trashed = false"
        )
        results = drive.files().list(q=query, fields="files(id,name)").execute()
        files = results.get("files", [])
        return files[0]["id"] if files else None

    def _list_folders_in(self, parent_id: str) -> list[dict[str, str]]:
        drive = self._get_drive()
        query = (
            f"'{parent_id}' in parents "
            "and mimeType = 'application/vnd.google-apps.folder' "
            "and trashed = false"
        )
        results = (
            drive.files()
            .list(q=query, fields="files(id,name,createdTime,modifiedTime)")
            .execute()
        )
        return results.get("files", [])

    def _list_files_in(self, folder_id: str) -> list[dict[str, Any]]:
        drive = self._get_drive()
        query = (
            f"'{folder_id}' in parents "
            "and trashed = false"
        )
        results = (
            drive.files()
            .list(
                q=query,
                fields="files(id,name,mimeType,webViewLink)",
            )
            .execute()
        )
        return results.get("files", [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_notebooks(self) -> list[dict[str, str]]:
        """
        Return all NotebookLM notebooks found in the user's Google Drive.

        Each entry contains ``id``, ``name``, ``createdTime``, and
        ``modifiedTime`` (Drive folder metadata).

        Returns an empty list if no NotebookLM root folder is found.
        """
        root_id = self._find_notebooklm_root()
        if not root_id:
            return []
        return self._list_folders_in(root_id)

    def list_sources(self, notebook_name_or_id: str) -> list[dict[str, Any]]:
        """
        List the source files inside a NotebookLM notebook folder.

        Parameters
        ----------
        notebook_name_or_id:
            The notebook's Display name **or** its Drive folder ID.
        """
        folder_id = self._resolve_notebook_id(notebook_name_or_id)
        return self._list_files_in(folder_id)

    def connect_notebook(
        self,
        notebook_name_or_id: str,
        *,
        system: str | None = None,
    ) -> NotebookLMClaude:
        """
        Load all sources from a single NotebookLM notebook and return a
        ready-to-query :class:`~lm_claude_union.NotebookLMClaude` session.
        """
        return self._build_session(
            [notebook_name_or_id],
            system=system,
        )

    def connect_notebooks(
        self,
        notebook_names_or_ids: list[str],
        *,
        system: str | None = None,
    ) -> NotebookLMClaude:
        """
        Load sources from *multiple* NotebookLM notebooks into one Claude session.

        Claude will have the combined context of all notebooks, allowing
        cross-notebook questions.
        """
        return self._build_session(notebook_names_or_ids, system=system)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _resolve_notebook_id(self, name_or_id: str) -> str:
        """Resolve a notebook name to its Drive folder ID."""
        # If it looks like a Drive ID (no spaces, ~28-33 chars), use directly
        if len(name_or_id) > 20 and " " not in name_or_id:
            return name_or_id

        notebooks = self.list_notebooks()
        matches = [nb for nb in notebooks if nb["name"] == name_or_id]
        if not matches:
            available = [nb["name"] for nb in notebooks]
            raise ValueError(
                f"Notebook {name_or_id!r} not found in Google Drive.\n"
                f"Available notebooks: {available}"
            )
        return matches[0]["id"]

    def _build_session(
        self,
        notebook_names_or_ids: list[str],
        *,
        system: str | None,
    ) -> NotebookLMClaude:
        conn = NotebookLMClaude(
            api_key=self._anthropic_api_key,
            model=self._model,
            system=system,
        )

        for name_or_id in notebook_names_or_ids:
            folder_id = self._resolve_notebook_id(name_or_id)
            files = self._list_files_in(folder_id)

            for f in files:
                mime = f.get("mimeType", "")
                file_id = f["id"]
                url = f.get("webViewLink", file_id)

                if mime not in _SUPPORTED_MIMES:
                    continue  # skip audio, images, etc.

                source = GoogleDocSource(
                    url,
                    credentials_file=self._credentials_file,
                    token_file=self._token_file,
                )
                conn.add_source(source)

        return conn
