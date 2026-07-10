"""
Airtable source — pulls records from a base/table as both free-text
context (for Claude Q&A) and structured records (for deterministic logic
like mismatch detection).
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any

from .base import LoadedSource, Source

_API_ROOT = "https://api.airtable.com/v0"


def fetch_records(
    base_id: str,
    table: str,
    *,
    api_key: str | None = None,
    fields: list[str] | None = None,
    filter_by_formula: str | None = None,
    view: str | None = None,
    max_records: int | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch records from an Airtable table via the REST API, following
    pagination automatically.

    Returns a flat list of dicts: ``{"id": <record id>, **fields}``.

    Parameters
    ----------
    base_id:
        Airtable base ID (e.g. ``appXXXXXXXXXXXXXX``).
    table:
        Table name or table ID.
    api_key:
        Personal access token. Falls back to the ``AIRTABLE_API_KEY`` env var.
    fields:
        Restrict the response to these field names.
    filter_by_formula:
        Airtable formula string (server-side filtering).
    view:
        Restrict to a saved view.
    max_records:
        Stop after this many records.
    """
    api_key = api_key or os.environ.get("AIRTABLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No Airtable API key. Pass api_key= or set AIRTABLE_API_KEY."
        )

    records: list[dict[str, Any]] = []
    offset: str | None = None

    while True:
        params: dict[str, Any] = {}
        if fields:
            params["fields[]"] = fields
        if filter_by_formula:
            params["filterByFormula"] = filter_by_formula
        if view:
            params["view"] = view
        if max_records:
            params["maxRecords"] = max_records
        if offset:
            params["offset"] = offset

        url = f"{_API_ROOT}/{base_id}/{urllib.parse.quote(table)}"
        query = urllib.parse.urlencode(params, doseq=True)
        if query:
            url += f"?{query}"

        req = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {api_key}"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            payload = json.loads(resp.read().decode("utf-8"))

        for rec in payload.get("records", []):
            records.append({"id": rec["id"], **rec.get("fields", {})})

        offset = payload.get("offset")
        if not offset or (max_records and len(records) >= max_records):
            break

    return records[:max_records] if max_records else records


class AirtableTableSource(Source):
    """
    Load an Airtable table as a flattened text block, suitable for use as
    Claude context alongside other sources (PDFs, Docs, web pages, etc.).

    For deterministic lookups/aggregation (e.g. "find unpaid invoices"),
    call :func:`fetch_records` directly instead — flattened text is lossy
    for that kind of logic. See :class:`~lm_claude_union.ops_assistant.OpsAssistant`.
    """

    def __init__(
        self,
        base_id: str,
        table: str,
        *,
        api_key: str | None = None,
        fields: list[str] | None = None,
        filter_by_formula: str | None = None,
        view: str | None = None,
        max_records: int | None = None,
    ) -> None:
        self._base_id = base_id
        self._table = table
        self._api_key = api_key
        self._fields = fields
        self._filter_by_formula = filter_by_formula
        self._view = view
        self._max_records = max_records

    @property
    def title(self) -> str:
        return f"Airtable: {self._table}"

    def load(self) -> LoadedSource:
        records = fetch_records(
            self._base_id,
            self._table,
            api_key=self._api_key,
            fields=self._fields,
            filter_by_formula=self._filter_by_formula,
            view=self._view,
            max_records=self._max_records,
        )

        lines = [f"{len(records)} record(s) from '{self._table}':\n"]
        for rec in records:
            row = ", ".join(f"{k}: {v}" for k, v in rec.items() if k != "id")
            lines.append(f"- {row}")

        return LoadedSource(
            title=self.title,
            text="\n".join(lines),
            source_type="airtable",
            uri=f"https://airtable.com/{self._base_id}",
        )
