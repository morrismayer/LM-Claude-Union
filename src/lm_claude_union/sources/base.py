"""Abstract base for all source types."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LoadedSource:
    title: str
    text: str
    source_type: str
    uri: str = ""


class Source(ABC):
    """All sources must implement load() and expose a title."""

    @abstractmethod
    def load(self) -> LoadedSource:
        """Fetch / parse the source and return its text."""

    @property
    @abstractmethod
    def title(self) -> str: ...
