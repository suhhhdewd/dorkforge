import re
import typing

from dorkforge.library import load_dorks
from dorkforge.models import Dork, PassiveActive, Risk, Surface

_PLACEHOLDER = re.compile(r"\[([^\[\]]+)\]")

_ALLOWED_RISK = set(typing.get_args(Risk))
_ALLOWED_PASSIVE_ACTIVE = set(typing.get_args(PassiveActive))
_ALLOWED_SURFACE = set(typing.get_args(Surface))


def test_load_dorks_returns_dork_list() -> None:
    dorks = load_dorks()
    assert isinstance(dorks, list)
    assert all(isinstance(d, Dork) for d in dorks)


def test_library_meets_record_floor() -> None:
    assert len(load_dorks()) >= 550


def test_ids_are_unique() -> None:
    ids = [d.id for d in load_dorks()]
    assert len(ids) == len(set(ids))


def test_query_placeholders_are_declared() -> None:
    dorks = load_dorks()
    # The placeholder vocabulary is the set of tokens declared anywhere in the
    # library. A bracketed token in a query that is not in this vocabulary is
    # literal query text (e.g. the page title "[Jenkins]"), not a substitution
    # slot, so it is not expected to appear in a record's placeholders list.
    vocabulary = {token for dork in dorks for token in dork.placeholders}
    for dork in dorks:
        used = set(_PLACEHOLDER.findall(dork.query)) & vocabulary
        missing = used - set(dork.placeholders)
        assert not missing, (
            f"dork id={dork.id} query uses placeholder(s) {sorted(missing)} "
            f"not declared in placeholders {dork.placeholders}"
        )


def test_enum_fields_only_hold_allowed_values() -> None:
    for dork in load_dorks():
        assert dork.risk in _ALLOWED_RISK
        assert dork.passive_active in _ALLOWED_PASSIVE_ACTIVE
        assert dork.surface in _ALLOWED_SURFACE
