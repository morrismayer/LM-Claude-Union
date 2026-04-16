"""
Example: communicate with your real Google NotebookLM notebooks via Claude.

Prerequisites
-------------
1. Enable the Google Drive API and Google Docs API in Google Cloud Console.
2. Download an OAuth 2.0 client-secrets JSON (or a service-account key).
3. Set environment variables:

       export ANTHROPIC_API_KEY=sk-ant-...

4. Install dependencies:

       pip install -e ".[all]"

Run
---
    python examples/google_notebooklm_bridge.py
"""
from lm_claude_union import NotebookLMBridge, NotebookLMClaude

# ─────────────────────────────────────────────────────────────────────────────
# Option A: Direct bridge — reads your real Google NotebookLM notebooks
# ─────────────────────────────────────────────────────────────────────────────

CREDENTIALS = "client_secret.json"   # ← path to your Google OAuth JSON

print("=== Discovering Google NotebookLM notebooks ===\n")

bridge = NotebookLMBridge(credentials_file=CREDENTIALS)

notebooks = bridge.list_notebooks()
if not notebooks:
    print(
        "No NotebookLM notebooks found in your Google Drive.\n"
        "Create a notebook at https://notebooklm.google.com first."
    )
else:
    for nb in notebooks:
        print(f"  • {nb['name']}  (id: {nb['id']})")

    # Pick the first notebook and connect it
    first = notebooks[0]["name"]
    print(f"\n=== Connecting to: '{first}' ===\n")

    conn = bridge.connect_notebook(first)
    print(f"Loaded {len(conn)} source(s): {conn.source_titles}\n")

    questions = [
        "What are the main topics covered in my notebook sources?",
        "Give me a concise summary of the key points.",
    ]
    for q in questions:
        print(f"Q: {q}")
        print(f"A: {conn.query(q)}\n")

    # Connect MULTIPLE notebooks at once
    if len(notebooks) >= 2:
        names = [nb["name"] for nb in notebooks[:2]]
        print(f"=== Multi-notebook: {names} ===\n")
        multi = bridge.connect_notebooks(names)
        print(multi.query("What themes are common across all my notebooks?"))


# ─────────────────────────────────────────────────────────────────────────────
# Option B: Manual source connection (mix any source types)
# ─────────────────────────────────────────────────────────────────────────────

print("\n=== Manual multi-source session ===\n")

conn2 = NotebookLMClaude(google_credentials_file=CREDENTIALS)

# Uncomment the sources you want to use:
# conn2.add_google_doc("https://docs.google.com/document/d/YOUR_DOC_ID/edit")
# conn2.add_youtube("https://youtu.be/YOUR_VIDEO_ID")
# conn2.add_pdf("path/to/report.pdf")
# conn2.add_url("https://example.com/article")
# conn2.add_notebook("examples/sample_notebook.ipynb")
# conn2.add_text("My custom text goes here.", title="Custom Note")

# For demonstration without real credentials, add the sample notebooks:
conn2.add_notebook("examples/sample_notebook.ipynb")
conn2.add_notebook("examples/sample_notebook_2.ipynb")

print(f"Sources: {conn2.source_titles}\n")
print("Q: What do these sources have in common?")
print(f"A: {conn2.query('What do these sources have in common?')}\n")

# Streaming
print("Q: Give a brief summary of each source.\nA: ", end="", flush=True)
for token in conn2.query("Give a brief summary of each source.", stream=True):
    print(token, end="", flush=True)
print("\n")
