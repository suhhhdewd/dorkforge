"""Build clickable search URLs from a rendered query, per surface.

URL construction only. No network calls are made here.
"""

import base64
from collections.abc import Callable
from urllib.parse import quote_plus


def _google(query: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(query)}"


def _bing(query: str) -> str:
    return f"https://www.bing.com/search?q={quote_plus(query)}"


def _duckduckgo(query: str) -> str:
    return f"https://duckduckgo.com/?q={quote_plus(query)}"


def _shodan(query: str) -> str:
    return f"https://www.shodan.io/search?query={quote_plus(query)}"


def _censys(query: str) -> str:
    return f"https://search.censys.io/search?resource=hosts&q={quote_plus(query)}"


def _github(query: str) -> str:
    return f"https://github.com/search?type=code&q={quote_plus(query)}"


def _gitlab(query: str) -> str:
    return f"https://gitlab.com/search?scope=blobs&search={quote_plus(query)}"


def _fofa(query: str) -> str:
    # FOFA reads the query from a base64 parameter, not a plain q=.
    encoded = base64.b64encode(query.encode()).decode()
    return f"https://en.fofa.info/result?qbase64={encoded}"


_BUILDERS: dict[str, Callable[[str], str]] = {
    "Google": _google,
    "Bing": _bing,
    "DuckDuckGo": _duckduckgo,
    "Shodan": _shodan,
    "Censys": _censys,
    "GitHub": _github,
    "GitLab": _gitlab,
    "FOFA": _fofa,
}


def build_url(surface: str, query: str) -> str:
    """Return a clickable search URL for ``query`` on ``surface``.

    Raises:
        ValueError: if ``surface`` is not a known search surface.
    """
    try:
        builder = _BUILDERS[surface]
    except KeyError:
        raise ValueError(
            f"unknown surface '{surface}'; known surfaces are {sorted(_BUILDERS)}"
        ) from None
    return builder(query)
