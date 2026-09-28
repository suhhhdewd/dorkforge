"""Typer CLI entry point."""

from collections import Counter
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from dorkforge import __version__
from dorkforge.export import FORMATS, serialize
from dorkforge.library import load_dorks
from dorkforge.selection import select_and_render

app = typer.Typer(
    name="dorkforge",
    help="Emit-only search-query generator for authorized recon and self-audit.",
    no_args_is_help=True,
)
console = Console()

BROAD_NOTICE = (
    "Note: broad results are internet-wide, third-party data, research-only. "
    "Do not act on findings without authorization."
)


@app.callback()
def main() -> None:
    """dorkforge CLI."""


@app.command()
def version() -> None:
    """Print the dorkforge version."""
    typer.echo(__version__)


def _require_authorization(authorized: bool) -> None:
    """Interim authorization gate for targeted mode.

    Targeted queries are scoped to a specific target, so the user must confirm
    they are authorized to test it. The full gate design lands in a later
    change; keep this the single choke point so it can be extended here.
    """
    if not authorized:
        console.print(
            "[red]Refusing to build targeted queries without authorization.[/red]\n"
            "Pass --authorized to confirm you are authorized to test this target."
        )
        raise typer.Exit(code=1)


def _collect_values(
    target: str | None,
    company: str | None,
    ip: str | None,
    asn: str | None,
    name: str | None,
) -> dict[str, str]:
    """Map CLI value flags to placeholder tokens, omitting those not supplied."""
    raw = {
        "domain": target,
        "company": company,
        "ip": ip,
        "asn": asn,
        "name": name,
    }
    return {token: value for token, value in raw.items() if value is not None}


@app.command(name="list")
def list_() -> None:
    """Summarize the library: counts by category, by surface, and the total."""
    dorks = load_dorks()

    by_category = Counter(d.category for d in dorks)
    by_surface = Counter(d.surface for d in dorks)

    cat_table = Table(title="Dorks by category")
    cat_table.add_column("Category")
    cat_table.add_column("Count", justify="right")
    for category, count in sorted(by_category.items()):
        cat_table.add_row(category, str(count))
    console.print(cat_table)

    surf_table = Table(title="Dorks by surface")
    surf_table.add_column("Surface")
    surf_table.add_column("Count", justify="right")
    for surface, count in sorted(by_surface.items()):
        surf_table.add_row(surface, str(count))
    console.print(surf_table)

    console.print(f"[bold]Total dorks:[/bold] {len(dorks)}")


@app.command()
def build(
    category: Annotated[str | None, typer.Option(help="Filter by exact category.")] = None,
    risk: Annotated[str | None, typer.Option(help="Filter by risk level.")] = None,
    surface: Annotated[str | None, typer.Option(help="Filter by surface/engine.")] = None,
    text: Annotated[
        str | None, typer.Option(help="Substring match in query/purpose/description.")
    ] = None,
    broad: Annotated[bool, typer.Option("--broad", help="Broad (internet-wide) mode.")] = False,
    authorized: Annotated[
        bool, typer.Option("--authorized", help="Confirm you are authorized to test the target.")
    ] = False,
    target: Annotated[str | None, typer.Option(help="Value for the [domain] placeholder.")] = None,
    company: Annotated[str | None, typer.Option(help="Value for [company].")] = None,
    ip: Annotated[str | None, typer.Option(help="Value for [ip].")] = None,
    asn: Annotated[str | None, typer.Option(help="Value for [asn].")] = None,
    name: Annotated[str | None, typer.Option(help="Value for [name].")] = None,
    tld: Annotated[
        str | None, typer.Option(help="Broad mode: prepend site:<tld> on Google-style surfaces.")
    ] = None,
    country: Annotated[
        str | None, typer.Option(help="Broad mode: append a country filter where supported.")
    ] = None,
    limit: Annotated[int | None, typer.Option(help="Cap the number of rows shown.")] = None,
) -> None:
    """Generate rendered queries and clickable search URLs for matching dorks."""
    if not broad:
        _require_authorization(authorized)

    values = _collect_values(target, company, ip, asn, name)
    result = select_and_render(
        load_dorks(),
        broad=broad,
        values=values,
        category=category,
        risk=risk,
        surface=surface,
        text=text,
        tld=tld,
        country=country,
    )
    rows = result.rows

    if broad:
        console.print(f"[yellow]{BROAD_NOTICE}[/yellow]")

    shown = rows if limit is None else rows[:limit]

    # When output is piped/captured (no real terminal) render wide so long
    # URLs are not folded across lines; use natural width for interactive use.
    render_console = console if console.is_terminal else Console(width=1000)

    table = Table(title="dorkforge queries")
    for col in ("id", "category", "risk", "surface", "query", "url"):
        table.add_column(col)
    for row in shown:
        table.add_row(
            str(row.id),
            row.category,
            row.risk,
            row.surface,
            row.query,
            row.url,
        )
    render_console.print(table)

    if limit is not None and len(rows) > limit:
        console.print(f"Showing {limit} of {len(rows)} matching dorks.")

    if result.skipped:
        if broad:
            console.print(
                f"Skipped {result.skipped} dorks (not broad-capable or empty when broadened)."
            )
        else:
            console.print(f"skipped {result.skipped} dorks needing values you did not supply")


@app.command()
def export(
    out: Annotated[Path, typer.Option(help="Destination file path.")],
    fmt: Annotated[
        str, typer.Option("--format", help="txt, csv, json, markdown, or html.")
    ] = "json",
    category: Annotated[str | None, typer.Option(help="Filter by exact category.")] = None,
    risk: Annotated[str | None, typer.Option(help="Filter by risk level.")] = None,
    surface: Annotated[str | None, typer.Option(help="Filter by surface/engine.")] = None,
    text: Annotated[
        str | None, typer.Option(help="Substring match in query/purpose/description.")
    ] = None,
    broad: Annotated[bool, typer.Option("--broad", help="Broad (internet-wide) mode.")] = False,
    authorized: Annotated[
        bool, typer.Option("--authorized", help="Confirm you are authorized to test the target.")
    ] = False,
    target: Annotated[str | None, typer.Option(help="Value for the [domain] placeholder.")] = None,
    company: Annotated[str | None, typer.Option(help="Value for [company].")] = None,
    ip: Annotated[str | None, typer.Option(help="Value for [ip].")] = None,
    asn: Annotated[str | None, typer.Option(help="Value for [asn].")] = None,
    name: Annotated[str | None, typer.Option(help="Value for [name].")] = None,
    tld: Annotated[
        str | None, typer.Option(help="Broad mode: prepend site:<tld> on Google-style surfaces.")
    ] = None,
    country: Annotated[
        str | None, typer.Option(help="Broad mode: append a country filter where supported.")
    ] = None,
) -> None:
    """Write rendered queries and URLs for matching dorks to a file."""
    if fmt not in FORMATS:
        raise typer.BadParameter(f"--format must be one of {list(FORMATS)}")

    if not broad:
        _require_authorization(authorized)

    values = _collect_values(target, company, ip, asn, name)
    result = select_and_render(
        load_dorks(),
        broad=broad,
        values=values,
        category=category,
        risk=risk,
        surface=surface,
        text=text,
        tld=tld,
        country=country,
    )

    out.write_text(serialize(result.rows, fmt), encoding="utf-8")

    if broad:
        console.print(f"[yellow]{BROAD_NOTICE}[/yellow]")
    console.print(f"Wrote {len(result.rows)} dorks to {out} ({fmt}).")
    if result.skipped:
        console.print(f"Skipped {result.skipped} dorks.")


@app.command()
def serve(
    host: Annotated[
        str, typer.Option(help="Interface to bind (localhost by default).")
    ] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="Port to listen on.")] = 8765,
) -> None:
    """Run the local web GUI (bound to 127.0.0.1 by default, per CLAUDE.md)."""
    import uvicorn

    console.print(f"dorkforge web GUI on http://{host}:{port}  (Ctrl+C to stop)")
    uvicorn.run("dorkforge.web.app:app", host=host, port=port, log_level="info")
