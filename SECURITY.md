# Security Policy

## Design intent: emit-only

dorkforge is **emit-only**. At runtime it generates search query strings and
URLs and makes **no network requests** to search engines or targets: no
scraping, no fetching of result pages, no link checking, and no HTTP client in
its runtime dependencies. The only network listener it provides is an optional
local web GUI bound to `127.0.0.1`.

This guarantee is enforced by a test (`tests/test_no_network.py`) that blocks
all non-loopback socket connections and then runs a targeted build, a broad
build, and an export end-to-end, asserting none attempt an outbound connection.

A test-only HTTP client (`httpx`, used by FastAPI's in-process `TestClient`)
lives in the `dev` extra and is never a runtime dependency.

## Intended use

- Authorized security reconnaissance against assets you own or are explicitly
  authorized to assess.
- Self-audit of your own online footprint.

dorkforge only *generates* queries. Executing them and acting on results are
the user's responsibility and must stay within authorization. See the Rules of
Engagement in [README.md](README.md#authorized-use).

## Reporting a vulnerability

If you find a security issue in dorkforge itself (for example, a code path that
could cause the runtime to make an outbound network request, contradicting the
emit-only guarantee), please open a private report to the maintainers rather
than a public issue, and allow reasonable time for a fix before disclosure.

Please do **not** include, in any report, data obtained by running generated
queries against systems you are not authorized to test.

## Scope reminder

Out of scope for this project by design: live execution/scraping in v1, and any
physical or imagery-based reconnaissance (street-view, satellite, geolocation,
EXIF, camera/webcam, or facial-imagery features).
