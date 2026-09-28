# CLAUDE.md — dorkforge

dorkforge is a search-query generator for **authorized** security recon and
**personal footprint self-audit**. It turns a curated library of search
operators ("dorks") into ready-to-run query strings and clickable search URLs.

## Hard constraints (non-negotiable)

1. **v1 is EMIT-ONLY.** dorkforge generates query strings and search URLs.
   It makes **NO network requests** to search engines or targets. **No
   scraping**, no fetching result pages, no "preview" requests, no link
   checking. The only network listener allowed is the local web GUI bound to
   `127.0.0.1`.
2. **Live execution is v2 and NOT implemented.** Execution via official APIs
   (Google Programmable Search / CSE, Shodan, etc.) must be designed as a
   pluggable interface now (`src/dorkforge/executors/base.py`), but no
   concrete executor may be implemented, registered, or shipped in v1. Do not
   add HTTP client dependencies (requests, httpx, aiohttp, API SDKs) in v1.
3. **Physical/imagery recon is out of scope.** No street-view, satellite,
   geolocation, EXIF, camera/webcam, or facial-imagery dorks or features.
4. **Everything is authorization-gated.** Query generation requires an
   explicit authorization step. (Gate design is specified in a later prompt;
   until then, do not add any code path that bypasses where the gate will go.)
5. **Two run modes:**
   - `targeted` — requires a scope value (e.g. a domain or the user's own
     name/handle). Queries are constrained to that scope.
   - `broad` — no scope value; generic operator queries.

## Stack

- Python 3.11+ (src layout: `src/dorkforge/`)
- Typer (CLI), Rich (CLI tables)
- FastAPI + Uvicorn (local web GUI, `127.0.0.1` only)
- Pydantic v2 (data models), PyYAML (dork library data file)
- pytest (tests), ruff (lint + format)

Keep dependencies minimal. Adding a dependency requires a clear reason.

## Layout

```
src/dorkforge/
  __init__.py        version
  __main__.py        `python -m dorkforge`
  cli.py             Typer app (console entry point `dorkforge`)
  models.py          Pydantic models
  executors/base.py  v2 executor interface (abstract only — no implementations)
  web/app.py         FastAPI app (local GUI)
  data/dorks.yaml    curated dork library
tests/
```

## Commands

Virtualenv lives at `.venv/` (Windows: `.venv\Scripts\python`).

```
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m pytest
.venv/Scripts/python -m ruff check .
.venv/Scripts/python -m ruff format .
```
