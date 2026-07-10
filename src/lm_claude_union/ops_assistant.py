"""
OpsAssistant — a Claude-powered operations assistant grounded in an
Airtable job tracker.

Built for workrooms / fabrication shops that track jobs as one row per
line item (e.g. several "Item #" rows sharing the same "Job #"). Every
aggregate check below groups by job number first — filtering a status
checkbox across raw line-item rows over-counts jobs with many items and
under-counts partially-updated ones.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from .claude_client import ClaudeClient
from .sources.airtable import fetch_records

DEFAULT_FIELDS = {
    "job_number": "Job #",
    "item_number": "Item #",
    "client": "Client/Project Name",
    "due_date": "Due Date",
    "furniture_received": "Furniture Received",
    "invoice_completed": "Invoice Completed",
    "paid_in_full": "Paid In Full",
    "invoice_link": "Invoice Link",
}


class OpsAssistant:
    """
    Operational assistant over a one-row-per-line-item Airtable job tracker.

    Parameters
    ----------
    base_id:
        Airtable base ID (e.g. ``appXXXXXXXXXXXXXX``).
    table:
        Table name or ID holding job/line-item records.
    api_key:
        Airtable personal access token. Falls back to ``AIRTABLE_API_KEY``.
    field_map:
        Override default field-name mapping (see ``DEFAULT_FIELDS``) if
        your base uses different column names.
    anthropic_api_key, model:
        Passed through to :class:`ClaudeClient` for :meth:`query` and
        :meth:`draft_client_update`.
    """

    def __init__(
        self,
        base_id: str,
        table: str,
        *,
        api_key: str | None = None,
        field_map: dict[str, str] | None = None,
        anthropic_api_key: str | None = None,
        model: str = "claude-sonnet-4-6",
    ) -> None:
        self._base_id = base_id
        self._table = table
        self._api_key = api_key
        self._fields = {**DEFAULT_FIELDS, **(field_map or {})}
        self._client = ClaudeClient(api_key=anthropic_api_key, model=model)
        self._records: list[dict[str, Any]] | None = None

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def refresh(self) -> list[dict[str, Any]]:
        """Re-fetch all records from Airtable and replace the local cache."""
        self._records = fetch_records(
            self._base_id, self._table, api_key=self._api_key
        )
        return self._records

    def _records_cached(self) -> list[dict[str, Any]]:
        if self._records is None:
            self.refresh()
        return self._records  # type: ignore[return-value]

    def _f(self, key: str) -> str:
        return self._fields[key]

    def _group_by_job(self) -> dict[str, list[dict[str, Any]]]:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        job_field = self._f("job_number")
        for rec in self._records_cached():
            job_no = rec.get(job_field)
            if job_no is not None:
                groups[str(job_no)].append(rec)
        return groups

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    def lookup_job(self, job_number: str | int) -> list[dict[str, Any]]:
        """Return all line-item rows for a given Job #."""
        job_field = self._f("job_number")
        return [
            rec
            for rec in self._records_cached()
            if str(rec.get(job_field)) == str(job_number)
        ]

    def find_ready_to_invoice(self) -> list[dict[str, Any]]:
        """
        Jobs with at least one line item where furniture has been received
        but the item isn't yet marked invoiced.

        Returns one summary dict per **job** (not per line item):
        ``{"job_number", "client", "item_count", "line_items"}``.
        """
        received_field = self._f("furniture_received")
        invoiced_field = self._f("invoice_completed")
        client_field = self._f("client")
        job_field = self._f("job_number")

        ready_items = [
            rec
            for rec in self._records_cached()
            if rec.get(received_field) and not rec.get(invoiced_field)
        ]

        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for rec in ready_items:
            groups[str(rec.get(job_field))].append(rec)

        return [
            {
                "job_number": job_no,
                "client": items[0].get(client_field),
                "item_count": len(items),
                "line_items": items,
            }
            for job_no, items in groups.items()
        ]

    def find_payment_mismatches(self) -> dict[str, Any]:
        """
        Flag jobs whose invoiced line items show no "Paid In Full" on any
        of them.

        "Paid In Full" is tracked per line item in this base, not per job,
        so a job is only flagged here if **every** invoiced line item lacks
        it — far more conservative than filtering the raw checkbox row by
        row, which produces an implausibly large, unreliable result set.
        Partially-paid jobs are intentionally not flagged; treat this as a
        worklist to confirm with billing, not a final answer.
        """
        invoiced_field = self._f("invoice_completed")
        paid_field = self._f("paid_in_full")
        client_field = self._f("client")

        unpaid_jobs = []
        for job_no, items in self._group_by_job().items():
            invoiced_items = [i for i in items if i.get(invoiced_field)]
            if not invoiced_items:
                continue
            if all(not i.get(paid_field) for i in invoiced_items):
                unpaid_jobs.append(
                    {
                        "job_number": job_no,
                        "client": items[0].get(client_field),
                        "invoiced_item_count": len(invoiced_items),
                    }
                )

        return {
            "unpaid_jobs": unpaid_jobs,
            "caveat": (
                "'Paid In Full' is tracked per line item, not per job. A job "
                "appears here only if NONE of its invoiced line items are "
                "marked paid — partially-paid jobs are not flagged. Confirm "
                "with billing before contacting clients."
            ),
        }

    # ------------------------------------------------------------------
    # Claude-backed actions
    # ------------------------------------------------------------------

    def draft_client_update(self, job_number: str | int) -> str:
        """Ask Claude to draft a status-update email for one job."""
        items = self.lookup_job(job_number)
        if not items:
            raise ValueError(f"No records found for Job # {job_number}")

        context = self._records_to_context(items, title=f"Job # {job_number}")
        question = (
            f"Draft a brief, friendly status-update email to the client for "
            f"Job # {job_number}, summarizing where each line item stands "
            "(fabrication, furniture received, invoiced, paid) based only "
            "on the data above. Do not invent details that aren't present "
            "in the data."
        )
        return self._client.query(question, context)

    def query(self, question: str) -> str:
        """Ask Claude a free-form question grounded in all loaded records."""
        context = self._records_to_context(
            self._records_cached(), title=f"Airtable table '{self._table}'"
        )
        return self._client.query(question, context)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _records_to_context(
        self, records: list[dict[str, Any]], *, title: str
    ) -> str:
        lines = [f"{title} — {len(records)} record(s):\n"]
        for rec in records:
            row = ", ".join(f"{k}: {v}" for k, v in rec.items() if k != "id")
            lines.append(f"- {row}")
        return "\n".join(lines)
