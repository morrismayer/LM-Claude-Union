"""
lm-claude-union
===============

Direct connection between Jupyter notebooks and Claude.
Connect one notebook or many at a time, then ask questions across all of them.

Usage::

    from lm_claude_union import NotebookLMClaude

    # Single notebook (context-manager cleans up automatically)
    with NotebookLMClaude("my_analysis.ipynb") as conn:
        answer = conn.query("What is the main conclusion?")
        print(answer)

    # Multiple notebooks
    conn = NotebookLMClaude("intro.ipynb", "results.ipynb")
    print(conn.query("Compare the methods described in the notebooks."))
    conn.clear()
"""

from .connector import NotebookLMClaude
from .notebook_parser import ParsedNotebook, parse_notebook, parse_notebooks

__all__ = [
    "NotebookLMClaude",
    "ParsedNotebook",
    "parse_notebook",
    "parse_notebooks",
]
