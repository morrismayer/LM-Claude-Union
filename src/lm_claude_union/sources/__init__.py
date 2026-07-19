"""All NotebookLM-compatible source types."""

from .base import LoadedSource, Source
from .google_docs import GoogleDocSource, GoogleDriveSource
from .pdf import PDFSource
from .text import RawTextSource, TextFileSource
from .web import WebSource
from .youtube import YouTubeSource

__all__ = [
    "Source",
    "LoadedSource",
    "GoogleDocSource",
    "GoogleDriveSource",
    "PDFSource",
    "WebSource",
    "YouTubeSource",
    "TextFileSource",
    "RawTextSource",
]
