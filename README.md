# dorkforge

Emit-only search-query generator for **authorized** security recon and
**personal footprint self-audit**. dorkforge turns a curated library of search
operators ("dorks") into ready-to-run query strings and clickable search URLs.

> **Status:** early skeleton (v0.1.0). Not yet functional.

## What it does (and doesn't)

- ✅ Generates query strings and search-engine URLs you can open yourself.
- ❌ Makes **no** network requests to search engines or targets. No scraping.
- ❌ Live API execution (Google CSE, Shodan, …) is planned for v2 only.

Use it only against scopes you own or are explicitly authorized to assess.

## Run modes

- **targeted** — requires a scope value (e.g. `example.com`, your own name).
- **broad** — no scope; generic operator queries.

## Install (dev)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"   # Windows
# .venv/bin/python -m pip install -e ".[dev]"     # macOS/Linux
dorkforge --help
```

## License

MIT — see [LICENSE](LICENSE).
