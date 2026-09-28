"""Local web GUI (FastAPI). Intended to be served on 127.0.0.1 only."""

from fastapi import FastAPI

from dorkforge import __version__

app = FastAPI(title="dorkforge", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
