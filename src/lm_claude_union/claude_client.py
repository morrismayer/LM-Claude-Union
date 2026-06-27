"""
Thin wrapper around the Anthropic SDK.

Uses prompt caching so that large notebook contexts are cached server-side
and don't count against your token budget on repeated queries.
"""
from __future__ import annotations

from typing import Generator, Iterator

import anthropic

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192

# Anthropic's minimum cacheable block size (tokens).  The SDK will silently
# ignore the cache_control hint on blocks that are too small, so this is just
# a soft guard to avoid pointless attempts.
MIN_CACHE_TOKENS = 1024


class ClaudeClient:
    """
    Sends queries to Claude, optionally with notebook content pinned to the
    prompt cache so repeated queries against the same notebooks are cheap.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = MAX_TOKENS,
    ) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def query(
        self,
        question: str,
        context: str,
        *,
        system: str | None = None,
        stream: bool = False,
    ) -> str | Iterator[str]:
        """
        Ask Claude a question with the notebook content as cached context.

        Parameters
        ----------
        question:
            The user's question.
        context:
            Full notebook text to use as grounding context.
        system:
            Optional system prompt override.
        stream:
            If True, returns a token iterator instead of the full string.
        """
        if stream:
            return self._stream(question, context, system=system)
        return self._complete(question, context, system=system)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_messages(self, question: str, context: str) -> list[dict]:
        """
        Build the messages array.  The large context block carries a
        ``cache_control`` hint so Anthropic can cache it server-side.
        """
        # Anthropic expects cache_control on individual *content blocks*.
        # We split the user turn into two blocks:
        #   1. The (potentially huge) notebook context  →  cached
        #   2. The short question                       →  not cached
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": context,
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": question,
                    },
                ],
            }
        ]

    def _default_system(self) -> str:
        return (
            "You are a helpful assistant with deep knowledge of the notebooks "
            "provided as context. Answer questions accurately using only the "
            "information in those notebooks. If the answer is not in the "
            "notebooks, say so clearly. Cite the notebook name and relevant "
            "section when helpful."
        )

    def _complete(self, question: str, context: str, *, system: str | None) -> str:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system or self._default_system(),
            messages=self._build_messages(question, context),
            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
        )
        return response.content[0].text

    def _stream(
        self, question: str, context: str, *, system: str | None
    ) -> Iterator[str]:
        with self._client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system or self._default_system(),
            messages=self._build_messages(question, context),
            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
        ) as stream:
            yield from stream.text_stream
