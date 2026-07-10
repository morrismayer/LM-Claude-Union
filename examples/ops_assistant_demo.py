"""
Ops assistant demo — job lookups, "ready to invoice" / payment-mismatch
worklists, and a Claude-drafted client update email, all grounded in an
Airtable job tracker.

Requires:
    export AIRTABLE_API_KEY=pat...
    export ANTHROPIC_API_KEY=sk-ant-...
"""
from lm_claude_union import OpsAssistant

# Replace with your own base/table — field names follow OpsAssistant's
# DEFAULT_FIELDS (Job #, Item #, Client/Project Name, Due Date,
# Furniture Received, Invoice Completed, Paid In Full, Invoice Link).
# Pass field_map={...} to OpsAssistant() if your columns are named differently.
BASE_ID = "appXXXXXXXXXXXXXX"
TABLE = "Jobs"

assistant = OpsAssistant(BASE_ID, TABLE)

# --- Status lookup by job number ---
job_number = "43140"
print(f"--- Line items for Job # {job_number} ---")
for item in assistant.lookup_job(job_number):
    print(item)

# --- Ready-to-invoice worklist (grouped by job, not by line item) ---
print("\n--- Ready to invoice ---")
for job in assistant.find_ready_to_invoice():
    print(f"Job # {job['job_number']} ({job['client']}): {job['item_count']} item(s) pending invoice")

# --- Payment mismatches (conservative: flags only fully-uninvoiced-unpaid jobs) ---
print("\n--- Payment mismatches ---")
mismatches = assistant.find_payment_mismatches()
print(mismatches["caveat"])
for job in mismatches["unpaid_jobs"]:
    print(f"Job # {job['job_number']} ({job['client']}): {job['invoiced_item_count']} invoiced item(s), none marked paid")

# --- Claude-drafted client update ---
print("\n--- Drafted client update ---")
print(assistant.draft_client_update(job_number))

# --- Free-form question across all records ---
print("\n--- Free-form query ---")
print(assistant.query("Which jobs are furthest past their due date and still incomplete?"))
