"""YouTube transcript source."""
from __future__ import annotations

import re

from .base import LoadedSource, Source

_YT_ID_RE = re.compile(
    r"(?:youtu\.be/|youtube\.com/(?:watch\?.*v=|embed/|shorts/))([A-Za-z0-9_-]{11})"
)


def _extract_video_id(url_or_id: str) -> str:
    m = _YT_ID_RE.search(url_or_id)
    if m:
        return m.group(1)
    # Assume bare 11-char ID
    if re.match(r"^[A-Za-z0-9_-]{11}$", url_or_id):
        return url_or_id
    raise ValueError(f"Cannot extract YouTube video ID from: {url_or_id!r}")


class YouTubeSource(Source):
    """
    Fetch the auto-generated or manual transcript of a YouTube video.

    Parameters
    ----------
    url_or_id:
        A YouTube URL (``https://youtu.be/…``, ``https://www.youtube.com/watch?v=…``)
        or a bare 11-character video ID.
    language:
        Preferred transcript language code (e.g. ``"en"``).  Falls back to
        any available language.
    """

    def __init__(self, url_or_id: str, language: str = "en") -> None:
        self._url_or_id = url_or_id
        self._video_id = _extract_video_id(url_or_id)
        self._language = language

    @property
    def title(self) -> str:
        return f"YouTube video ({self._video_id})"

    def load(self) -> LoadedSource:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
        except ImportError as exc:
            raise ImportError(
                "youtube-transcript-api is required for YouTube sources.\n"
                "Install with: pip install youtube-transcript-api"
            ) from exc

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(self._video_id)
            try:
                transcript = transcript_list.find_transcript([self._language])
            except NoTranscriptFound:
                transcript = next(iter(transcript_list))
            entries = transcript.fetch()
        except Exception as exc:
            raise RuntimeError(
                f"Could not fetch transcript for {self._video_id}: {exc}"
            ) from exc

        # Build readable transcript with timestamps
        lines: list[str] = []
        for entry in entries:
            start = int(entry["start"])
            mins, secs = divmod(start, 60)
            text = entry["text"].replace("\n", " ")
            lines.append(f"[{mins:02d}:{secs:02d}] {text}")

        return LoadedSource(
            title=self.title,
            text="\n".join(lines),
            source_type="youtube",
            uri=f"https://www.youtube.com/watch?v={self._video_id}",
        )
