"""
Parse Jupyter notebooks (.ipynb) into clean text for use as Claude context.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ParsedNotebook:
    """Holds the extracted text content of a notebook."""

    path: str
    title: str
    cells: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        """Full notebook text with a header."""
        header = f"=== Notebook: {self.title} ===\n"
        return header + "\n\n".join(self.cells)

    def __repr__(self) -> str:
        return f"ParsedNotebook(title={self.title!r}, cells={len(self.cells)})"


def _cell_outputs_to_text(outputs: list[dict[str, Any]]) -> str:
    """Convert notebook cell outputs to plain text."""
    parts: list[str] = []
    for output in outputs:
        output_type = output.get("output_type", "")
        if output_type == "stream":
            text = output.get("text", "")
            if isinstance(text, list):
                text = "".join(text)
            parts.append(text.strip())
        elif output_type in ("display_data", "execute_result"):
            data = output.get("data", {})
            # Prefer plain text; fall back to nothing for images etc.
            if "text/plain" in data:
                txt = data["text/plain"]
                if isinstance(txt, list):
                    txt = "".join(txt)
                parts.append(txt.strip())
        elif output_type == "error":
            ename = output.get("ename", "Error")
            evalue = output.get("evalue", "")
            parts.append(f"{ename}: {evalue}")
    return "\n".join(parts)


def _source_to_str(source: str | list[str]) -> str:
    if isinstance(source, list):
        return "".join(source)
    return source


def parse_notebook(path: str | Path) -> ParsedNotebook:
    """
    Parse a single Jupyter notebook and return a :class:`ParsedNotebook`.

    Supports .ipynb format (nbformat 4).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Notebook not found: {path}")
    if path.suffix.lower() != ".ipynb":
        raise ValueError(f"Expected a .ipynb file, got: {path}")

    with path.open(encoding="utf-8") as fh:
        nb = json.load(fh)

    # Derive a human-readable title from the filename or first markdown heading
    title = path.stem
    cells_text: list[str] = []

    for cell in nb.get("cells", []):
        cell_type = cell.get("cell_type", "")
        source = _source_to_str(cell.get("source", ""))

        if not source.strip():
            continue

        if cell_type == "markdown":
            # Use the first H1 as the title if we haven't found one yet
            if title == path.stem:
                for line in source.splitlines():
                    if line.startswith("# "):
                        title = line.lstrip("# ").strip()
                        break
            cells_text.append(source)

        elif cell_type == "code":
            block = f"```python\n{source}\n```"
            outputs = _cell_outputs_to_text(cell.get("outputs", []))
            if outputs:
                block += f"\n# Output:\n{outputs}"
            cells_text.append(block)

        elif cell_type == "raw":
            cells_text.append(source)

    return ParsedNotebook(path=str(path.resolve()), title=title, cells=cells_text)


def parse_notebooks(paths: list[str | Path]) -> list[ParsedNotebook]:
    """Parse multiple notebooks and return a list of :class:`ParsedNotebook`."""
    return [parse_notebook(p) for p in paths]
