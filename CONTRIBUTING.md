# Contributing to dorkforge

Thanks for your interest. dorkforge has a narrow, deliberate scope; please keep
contributions within it.

## Non-negotiable constraints

These are enforced in [CLAUDE.md](CLAUDE.md) and by tests:

1. **v1 is emit-only.** The runtime must make no network requests to search
   engines or targets, and must ship no HTTP client in its runtime
   dependencies. Do not add `requests`, `httpx`, `aiohttp`, or API SDKs to the
   runtime dependencies. (`httpx` is allowed in the `dev` extra for the
   in-process `TestClient` only.)
2. **The local web GUI binds to `127.0.0.1` only.**
3. **No physical/imagery reconnaissance** (street-view, satellite, geolocation,
   EXIF, camera/webcam, or facial-imagery features).
4. **Authorization gating stays intact.** Targeted query generation must remain
   behind the authorization gate.

## Live execution (v2) — official APIs only

Any future live-execution feature **must**:

- Use the search provider's **official, authenticated API** (e.g. Google
  Programmable Search / CSE, Shodan, Censys), implemented behind the existing
  `src/dorkforge/executors/base.py` interface.
- **Never scrape** search engines or fetch/parse result pages.
- Respect each provider's Terms of Service and rate limits.
- Keep execution opt-in and clearly separated from the emit-only default.

A contribution that scrapes, or that reaches a target/search engine directly
without an official API, will not be accepted.

## Development

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"   # Windows
.venv/Scripts/python -m pytest
.venv/Scripts/python -m ruff check .
.venv/Scripts/python -m ruff format .
```

Please add or update tests with your change, and keep `ruff` clean. New
dork records must validate against the `Dork` model and declare any placeholder
tokens they use.
