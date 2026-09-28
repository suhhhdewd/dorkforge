"""Typer CLI entry point."""

import typer

from dorkforge import __version__

app = typer.Typer(
    name="dorkforge",
    help="Emit-only search-query generator for authorized recon and self-audit.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """dorkforge CLI."""


@app.command()
def version() -> None:
    """Print the dorkforge version."""
    typer.echo(__version__)
