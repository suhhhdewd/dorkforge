"""Local web GUI (FastAPI).

A thin adapter over the shared core / selection / export logic. It is intended
to be served on 127.0.0.1 only and makes no network calls to search engines:
it only builds queries and URLs that the user's browser opens when clicked.
"""

from importlib.resources import files

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from dorkforge import __version__
from dorkforge.export import CONTENT_TYPES, EXTENSIONS, FORMATS, serialize
from dorkforge.library import load_dorks
from dorkforge.selection import select_and_render

app = FastAPI(title="dorkforge", version=__version__)

BROAD_NOTICE = (
    "Broad results are internet-wide, third-party data, research-only. "
    "Do not act on findings without authorization."
)

_STATIC = files("dorkforge.web").joinpath("static")


def _read_static(name: str) -> str:
    return _STATIC.joinpath(name).read_text(encoding="utf-8")


class BuildRequest(BaseModel):
    category: str | None = None
    risk: str | None = None
    surface: str | None = None
    passive_active: str | None = None
    text: str | None = None
    mode: str = "targeted"
    values: dict[str, str] = {}
    tld: str | None = None
    country: str | None = None
    authorized: bool = False


class ExportRequest(BuildRequest):
    format: str = "json"


def _run_selection(req: BuildRequest):
    broad = req.mode == "broad"
    # Server-side authorization gate: targeted mode requires explicit consent.
    if not broad and not req.authorized:
        return None, broad
    result = select_and_render(
        load_dorks(),
        broad=broad,
        values=req.values,
        category=req.category,
        risk=req.risk,
        surface=req.surface,
        passive_active=req.passive_active,
        text=req.text,
        tld=req.tld,
        country=req.country,
    )
    return result, broad


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(_read_static("index.html"))


@app.get("/style.css")
def style() -> Response:
    return Response(_read_static("style.css"), media_type="text/css")


@app.get("/app.js")
def app_js() -> Response:
    return Response(_read_static("app.js"), media_type="text/javascript")


@app.post("/api/build")
def api_build(req: BuildRequest) -> Response:
    result, broad = _run_selection(req)
    if result is None:
        return _bad_request(
            "Targeted mode requires authorization. Set authorized=true to confirm "
            "you are authorized to test this target, or use broad mode."
        )
    return _json_response(
        {
            "rows": [row.model_dump() for row in result.rows],
            "skipped": result.skipped,
            "broad": broad,
            "notice": BROAD_NOTICE if broad else None,
        }
    )


@app.post("/api/export")
def api_export(req: ExportRequest) -> Response:
    if req.format not in FORMATS:
        return _bad_request(f"format must be one of {list(FORMATS)}")

    result, _ = _run_selection(req)
    if result is None:
        return _bad_request(
            "Targeted mode requires authorization. Set authorized=true to confirm "
            "you are authorized to test this target, or use broad mode."
        )

    body = serialize(result.rows, req.format)
    filename = f"dorkforge.{EXTENSIONS[req.format]}"
    return Response(
        content=body,
        media_type=CONTENT_TYPES[req.format],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _json_response(payload: dict) -> Response:
    import json

    return Response(content=json.dumps(payload), media_type="application/json")


def _bad_request(message: str) -> Response:
    import json

    return Response(
        content=json.dumps({"detail": message}),
        status_code=400,
        media_type="application/json",
    )
