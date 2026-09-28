"""Pure, network-free core engine: query rendering, broad mode, and filtering.

This module only transforms strings and filters records. It performs no I/O
and makes no network requests.
"""

import re

from dorkforge.models import Dork

#: The exact set of substitution tokens the library uses. Any other bracketed
#: text in a query (e.g. the literal "[Jenkins]" in a dashboard title) is not a
#: placeholder and is left untouched.
PLACEHOLDER_VOCAB: frozenset[str] = frozenset(
    {"asn", "company", "domain", "ip", "name", "socialplatform"}
)

#: Google-style surfaces where a ``site:`` filter is meaningful.
_GOOGLE_STYLE: frozenset[str] = frozenset({"Google", "Bing", "DuckDuckGo"})

#: Target-scoping fragments removed to widen a query internet-wide, longest
#: first so more specific patterns are stripped before their substrings.
_SCOPE_PATTERNS: tuple[str, ...] = (
    "ssl.cert.subject.cn:[domain]",
    "autonomous_system.asn:[asn]",
    'org:"[company]"',
    "hostname:[domain]",
    'domain="[domain]"',
    "org:[company]",
    "site:[domain]",
    "net:[ip]",
    "ip:[ip]",
)

_DOUBLE_SPACE = re.compile(r"\s{2,}")


def render(dork: Dork, values: dict[str, str]) -> str:
    """Render a dork query for targeted mode by substituting placeholders.

    Only tokens from :data:`PLACEHOLDER_VOCAB` that appear as ``[token]`` in
    ``dork.query`` are substituted. Non-vocabulary bracketed text is left as
    literal query text.

    Raises:
        ValueError: if ``values`` contains a key outside PLACEHOLDER_VOCAB
            (typo guard), or if a placeholder declared in ``dork.placeholders``
            has no supplied value.
    """
    unknown = set(values) - PLACEHOLDER_VOCAB
    if unknown:
        raise ValueError(
            f"unknown value key(s) {sorted(unknown)}; "
            f"allowed placeholders are {sorted(PLACEHOLDER_VOCAB)}"
        )

    for token in dork.placeholders:
        if token not in values:
            raise ValueError(f"missing value for required placeholder '{token}'")

    query = dork.query
    for token in PLACEHOLDER_VOCAB:
        if token in values:
            query = query.replace(f"[{token}]", values[token])
    return query


def to_broad(dork: Dork, tld: str | None = None, country: str | None = None) -> str:
    """Widen a dork query to run internet-wide (broad mode).

    Strips target-scoping tokens, then optionally re-narrows: ``tld`` prepends
    ``site:<tld>`` on Google-style surfaces, and ``country`` appends the
    engine-appropriate country filter where it applies.

    Raises:
        ValueError: if ``dork.broad_capable`` is False.
    """
    if not dork.broad_capable:
        raise ValueError(f"dork id={dork.id} is not broad_capable")

    query = dork.query
    for pattern in _SCOPE_PATTERNS:
        query = query.replace(pattern, "")
    query = _DOUBLE_SPACE.sub(" ", query).strip()

    if tld and dork.surface in _GOOGLE_STYLE:
        query = f"site:{tld} {query}".strip()

    if country:
        if dork.surface in {"Shodan", "Censys"}:
            query = f'{query} country:"{country}"'.strip()
        elif dork.surface == "FOFA":
            query = f'{query} country="{country}"'.strip()

    return query


def filter_dorks(
    dorks: list[Dork],
    *,
    category: str | None = None,
    risk: str | None = None,
    surface: str | None = None,
    passive_active: str | None = None,
    text: str | None = None,
) -> list[Dork]:
    """Return records matching every provided filter.

    ``text`` is a case-insensitive substring match across ``query``,
    ``purpose``, and ``description``.
    """
    needle = text.lower() if text else None

    def matches(dork: Dork) -> bool:
        if category is not None and dork.category != category:
            return False
        if risk is not None and dork.risk != risk:
            return False
        if surface is not None and dork.surface != surface:
            return False
        if passive_active is not None and dork.passive_active != passive_active:
            return False
        haystack = f"{dork.query}\n{dork.purpose}\n{dork.description}".lower()
        return not (needle is not None and needle not in haystack)

    return [dork for dork in dorks if matches(dork)]
