"""Serialize rendered dorks to export formats.

Shared by the CLI and the web GUI so the two cannot diverge. No I/O here: this
module only turns rows into strings and reports their media type / extension.
"""

import csv
import io
import json
from html import escape

from dorkforge.selection import RenderedDork

FORMATS: tuple[str, ...] = ("txt", "csv", "json", "markdown", "html")

_FIELDS: tuple[str, ...] = ("id", "category", "risk", "surface", "purpose", "query", "url")

CONTENT_TYPES: dict[str, str] = {
    "txt": "text/plain; charset=utf-8",
    "csv": "text/csv; charset=utf-8",
    "json": "application/json",
    "markdown": "text/markdown; charset=utf-8",
    "html": "text/html; charset=utf-8",
}

EXTENSIONS: dict[str, str] = {
    "txt": "txt",
    "csv": "csv",
    "json": "json",
    "markdown": "md",
    "html": "html",
}


def serialize(rows: list[RenderedDork], fmt: str) -> str:
    """Serialize export ``rows`` to ``fmt``.

    Raises:
        ValueError: if ``fmt`` is not one of :data:`FORMATS`.
    """
    if fmt not in FORMATS:
        raise ValueError(f"format must be one of {list(FORMATS)}, got '{fmt}'")

    records = [{k: getattr(row, k) for k in _FIELDS} for row in rows]

    if fmt == "json":
        return json.dumps(records, indent=2)

    if fmt == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=_FIELDS)
        writer.writeheader()
        writer.writerows(records)
        return buffer.getvalue()

    if fmt == "txt":
        lines: list[str] = []
        for r in records:
            lines.append(f"[{r['id']}] {r['category']} | {r['risk']} | {r['surface']}")
            lines.append(f"  purpose: {r['purpose']}")
            lines.append(f"  query:   {r['query']}")
            lines.append(f"  url:     {r['url']}")
            lines.append("")
        return "\n".join(lines)

    if fmt == "markdown":
        header = "| " + " | ".join(_FIELDS) + " |"
        sep = "| " + " | ".join("---" for _ in _FIELDS) + " |"
        body = [
            "| " + " | ".join(str(r[k]).replace("|", "\\|") for k in _FIELDS) + " |"
            for r in records
        ]
        return "\n".join([header, sep, *body]) + "\n"

    # html
    head = "".join(f"<th>{escape(k)}</th>" for k in _FIELDS)
    body_rows = []
    for r in records:
        cells = "".join(f"<td>{escape(str(r[k]))}</td>" for k in _FIELDS)
        body_rows.append(f"<tr>{cells}</tr>")
    return (
        "<table>\n<thead><tr>"
        + head
        + "</tr></thead>\n<tbody>\n"
        + "\n".join(body_rows)
        + "\n</tbody>\n</table>\n"
    )
