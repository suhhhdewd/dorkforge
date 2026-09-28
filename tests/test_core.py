import pytest

from dorkforge.core import PLACEHOLDER_VOCAB, filter_dorks, render, to_broad
from dorkforge.models import Dork


def make_dork(**overrides) -> Dork:
    base = dict(
        id=1,
        category="Admin & Login Panels",
        query="site:[domain] inurl:admin",
        purpose="Admin Panel",
        description="Finds admin interfaces on a target domain",
        operators="site:, inurl:",
        risk="High",
        passive_active="Passive",
        surface="Google",
        defensive="restrict access",
        reference="GHDB",
        handling="document only",
        placeholders=["domain"],
        broad_capable=True,
    )
    base.update(overrides)
    return Dork(**base)


def test_render_substitutes_domain() -> None:
    dork = make_dork()
    assert render(dork, {"domain": "example.com"}) == "site:example.com inurl:admin"


def test_render_leaves_non_vocab_bracket_untouched() -> None:
    dork = make_dork(
        query='intitle:"Dashboard [Jenkins]" site:[domain]',
        placeholders=["domain"],
    )
    assert render(dork, {"domain": "example.com"}) == (
        'intitle:"Dashboard [Jenkins]" site:example.com'
    )


def test_render_raises_on_unknown_value_key() -> None:
    dork = make_dork()
    with pytest.raises(ValueError, match="unknown value key"):
        render(dork, {"domian": "example.com"})


def test_render_raises_on_missing_required_placeholder() -> None:
    dork = make_dork(query="site:[domain] intext:[company]", placeholders=["domain", "company"])
    with pytest.raises(ValueError, match="company"):
        render(dork, {"domain": "example.com"})


def test_to_broad_strips_google_scope() -> None:
    dork = make_dork(query="site:[domain] inurl:admin", surface="Google")
    assert to_broad(dork) == "inurl:admin"


def test_to_broad_strips_shodan_scope() -> None:
    dork = make_dork(
        query='org:"[company]" port:9200 product:"Elasticsearch"',
        surface="Shodan",
        placeholders=["company"],
    )
    assert to_broad(dork) == 'port:9200 product:"Elasticsearch"'


def test_to_broad_prepends_tld_on_google() -> None:
    dork = make_dork(query="site:[domain] inurl:admin", surface="Google")
    assert to_broad(dork, tld="*.gov") == "site:*.gov inurl:admin"


def test_to_broad_appends_country_for_shodan() -> None:
    dork = make_dork(
        query='org:"[company]" port:9200',
        surface="Shodan",
        placeholders=["company"],
    )
    assert to_broad(dork, country="US") == 'port:9200 country:"US"'


def test_to_broad_appends_country_for_fofa() -> None:
    dork = make_dork(
        query='domain="[domain]"',
        surface="FOFA",
        placeholders=["domain"],
    )
    assert to_broad(dork, country="US") == 'country="US"'


def test_to_broad_tld_ignored_on_shodan() -> None:
    dork = make_dork(
        query='org:"[company]" port:9200',
        surface="Shodan",
        placeholders=["company"],
    )
    assert to_broad(dork, tld="*.gov") == "port:9200"


def test_to_broad_raises_when_not_broad_capable() -> None:
    dork = make_dork(broad_capable=False)
    with pytest.raises(ValueError, match="not broad_capable"):
        to_broad(dork)


def test_filter_by_each_field() -> None:
    dorks = [
        make_dork(id=1, category="A", risk="High", surface="Google", passive_active="Passive"),
        make_dork(id=2, category="B", risk="Low", surface="Shodan", passive_active="Passive"),
    ]
    assert [d.id for d in filter_dorks(dorks, category="A")] == [1]
    assert [d.id for d in filter_dorks(dorks, risk="Low")] == [2]
    assert [d.id for d in filter_dorks(dorks, surface="Shodan")] == [2]
    assert [d.id for d in filter_dorks(dorks, passive_active="Passive")] == [1, 2]


def test_filter_by_text_is_case_insensitive() -> None:
    dorks = [
        make_dork(id=1, query="inurl:admin", purpose="Admin Panel", description="interfaces"),
        make_dork(id=2, query="inurl:db", purpose="Database", description="exposed store"),
    ]
    assert [d.id for d in filter_dorks(dorks, text="ADMIN")] == [1]
    assert [d.id for d in filter_dorks(dorks, text="databASE")] == [2]


def test_vocab_is_exact() -> None:
    assert set(PLACEHOLDER_VOCAB) == {"asn", "company", "domain", "ip", "name", "socialplatform"}
