import base64
from urllib.parse import quote_plus

import pytest

from dorkforge.urls import build_url


def test_each_surface_base_and_param() -> None:
    q = "site:example.com inurl:admin"
    enc = quote_plus(q)
    assert build_url("Google", q) == f"https://www.google.com/search?q={enc}"
    assert build_url("Bing", q) == f"https://www.bing.com/search?q={enc}"
    assert build_url("DuckDuckGo", q) == f"https://duckduckgo.com/?q={enc}"
    assert build_url("Shodan", q) == f"https://www.shodan.io/search?query={enc}"
    assert build_url("Censys", q) == f"https://search.censys.io/search?resource=hosts&q={enc}"
    assert build_url("GitHub", q) == f"https://github.com/search?type=code&q={enc}"
    assert build_url("GitLab", q) == f"https://gitlab.com/search?scope=blobs&search={enc}"


def test_special_characters_encode() -> None:
    q = 'site:example.com intitle:"admin panel" (login) port:9200 a|b'
    url = build_url("Google", q)
    enc = url.split("q=", 1)[1]
    # No raw special characters survive in the query parameter.
    for raw in ['"', " ", "(", ")", "|", ":"]:
        assert raw not in enc
    # Spot-check specific encodings.
    assert "%22" in enc  # double quote
    assert "+" in enc  # space -> plus
    assert "%28" in enc and "%29" in enc  # parentheses
    assert "%7C" in enc  # pipe
    assert "%3A" in enc  # colon
    # And it decodes back exactly.
    from urllib.parse import unquote_plus

    assert unquote_plus(enc) == q


def test_fofa_qbase64_roundtrip() -> None:
    q = 'domain="example.com" && port="443"'
    url = build_url("FOFA", q)
    assert url.startswith("https://en.fofa.info/result?qbase64=")
    b64 = url.split("qbase64=", 1)[1]
    assert base64.b64decode(b64).decode() == q


def test_unknown_surface_raises() -> None:
    with pytest.raises(ValueError, match="unknown surface"):
        build_url("Yandex", "test")
