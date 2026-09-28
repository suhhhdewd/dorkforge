"""Shared selection-and-render logic used by every front-end.

The CLI and the web GUI both call :func:`select_and_render` so the two cannot
diverge in how they filter dorks, render queries, build URLs, or decide which
records to skip. This module makes no network calls.
"""

from pydantic import BaseModel

from dorkforge.core import filter_dorks, render, to_broad
from dorkforge.models import Dork
from dorkforge.safety import BROAD_ADVISORY, TARGETED_ADVISORY
from dorkforge.urls import build_url


class RenderedDork(BaseModel):
    """One rendered result: the dork's identity plus its query and search URL.

    ``mode`` and ``advisory`` carry the authorization/status tag with every row
    so the broad, third-party, research-only nature is explicit on each result
    and in exports, not only in a single banner line.
    """

    id: int
    category: str
    risk: str
    surface: str
    mode: str
    advisory: str
    purpose: str
    query: str
    url: str


class Selection(BaseModel):
    """Result of selecting and rendering dorks.

    ``skipped`` counts records dropped for any reason: in targeted mode, a
    declared placeholder had no supplied value; in broad mode, the dork is not
    broad-capable or its broadened query is empty/whitespace-only.
    """

    rows: list[RenderedDork]
    skipped: int


def select_and_render(
    dorks: list[Dork],
    *,
    broad: bool = False,
    values: dict[str, str] | None = None,
    category: str | None = None,
    risk: str | None = None,
    surface: str | None = None,
    passive_active: str | None = None,
    text: str | None = None,
    tld: str | None = None,
    country: str | None = None,
) -> Selection:
    """Filter ``dorks``, render each match, and return rows plus a skip count."""
    values = values or {}
    matched = filter_dorks(
        dorks,
        category=category,
        risk=risk,
        surface=surface,
        passive_active=passive_active,
        text=text,
    )

    mode = "broad" if broad else "targeted"
    advisory = BROAD_ADVISORY if broad else TARGETED_ADVISORY

    rows: list[RenderedDork] = []
    skipped = 0
    for dork in matched:
        if broad:
            if not dork.broad_capable:
                skipped += 1
                continue
            query = to_broad(dork, tld=tld, country=country)
            if not query.strip():
                # A scope-only dork (e.g. domain="[domain]") broadens to
                # nothing; there is no meaningful internet-wide query to emit.
                skipped += 1
                continue
        else:
            if set(dork.placeholders) - set(values):
                skipped += 1
                continue
            query = render(dork, values)

        rows.append(
            RenderedDork(
                id=dork.id,
                category=dork.category,
                risk=dork.risk,
                surface=dork.surface,
                mode=mode,
                advisory=advisory,
                purpose=dork.purpose,
                query=query,
                url=build_url(dork.surface, query),
            )
        )

    return Selection(rows=rows, skipped=skipped)
