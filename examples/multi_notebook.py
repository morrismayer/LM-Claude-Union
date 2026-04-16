"""
Example: connect multiple notebooks at once and query across all of them.

Set your ANTHROPIC_API_KEY environment variable before running:

    export ANTHROPIC_API_KEY=sk-ant-...
    python examples/multi_notebook.py
"""
from lm_claude_union import NotebookLMClaude

NOTEBOOKS = [
    "examples/sample_notebook.ipynb",    # Climate Data Analysis
    "examples/sample_notebook_2.ipynb",  # Renewable Energy Capacity
]

print("=== Multi-notebook session ===\n")

# Connect all notebooks in one call
conn = NotebookLMClaude(*NOTEBOOKS)
print(f"Connected {len(conn)} notebooks: {conn.notebook_titles}\n")

questions = [
    "What do these notebooks have in common?",
    "Which notebook discusses temperature anomalies, and what are its main findings?",
    "How does the renewable energy data relate to the climate findings?",
    "What policy mechanisms are mentioned for driving clean energy growth?",
]

for q in questions:
    print(f"Q: {q}")
    answer = conn.query(q)
    print(f"A: {answer}\n")

# --- Dynamic connection management ---
print("=== Dynamic connection ===\n")
conn2 = NotebookLMClaude()              # start empty
conn2.connect("examples/sample_notebook.ipynb")
print(f"After connect():      {conn2.notebook_titles}")

conn2.connect("examples/sample_notebook_2.ipynb")
print(f"After second connect: {conn2.notebook_titles}")

conn2.disconnect("examples/sample_notebook.ipynb")
print(f"After disconnect():   {conn2.notebook_titles}")

conn2.clear()
print(f"After clear():        {conn2.notebook_titles}")
