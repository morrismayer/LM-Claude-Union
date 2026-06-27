"""
Example: connect a single notebook and ask questions.

Set your ANTHROPIC_API_KEY environment variable before running:

    export ANTHROPIC_API_KEY=sk-ant-...
    python examples/single_notebook.py
"""
from lm_claude_union import NotebookLMClaude

NOTEBOOK = "examples/sample_notebook.ipynb"

# --- Option A: context manager (cleans up automatically) ---
print("=== Single-notebook session ===\n")
with NotebookLMClaude(NOTEBOOK) as conn:
    print(f"Connected notebooks: {conn.notebook_titles}\n")

    questions = [
        "What dataset is used in this notebook and where does it come from?",
        "What are the key findings about temperature change?",
        "What was the temperature anomaly difference between early and recent periods?",
    ]
    for q in questions:
        print(f"Q: {q}")
        answer = conn.query(q)
        print(f"A: {answer}\n")

# --- Option B: streaming response ---
print("=== Streaming example ===\n")
conn = NotebookLMClaude(NOTEBOOK)
print("Q: Summarise the notebook's conclusion.\nA: ", end="", flush=True)
for token in conn.query("Summarise the notebook's conclusion.", stream=True):
    print(token, end="", flush=True)
print("\n")
conn.clear()
