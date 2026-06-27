"""All NotebookLM-compatible source types."""

from .airtable import AirtableTableSource, fetch_records
from .base import LoadedSource, Source
from .google_docs import GoogleDocSource, GoogleDriveSource
from .pdf import PDFSource
from .text import RawTextSource, TextFileSource
from .web import WebSource
from .youtube import YouTubeSource

__all__ = [
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
]
