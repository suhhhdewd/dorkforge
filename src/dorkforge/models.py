"""Pydantic data models."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class RunMode(StrEnum):
    """How queries are generated.

    TARGETED requires a scope value; BROAD takes none.
    """

    TARGETED = "targeted"
    BROAD = "broad"


Risk = Literal["Critical", "High", "Medium", "Low", "Info"]
PassiveActive = Literal["Passive", "Active"]
Surface = Literal[
    "Google",
    "Bing",
    "DuckDuckGo",
    "Shodan",
    "Censys",
    "FOFA",
    "GitHub",
    "GitLab",
]


class Dork(BaseModel):
    """One curated search operator record from the library.

    Fields mirror the YAML records in ``data/dorks.yaml`` exactly.
    """

    id: int
    category: str
    query: str
    purpose: str
    description: str
    operators: str
    risk: Risk
    passive_active: PassiveActive
    surface: Surface
    defensive: str
    reference: str
    handling: str
    placeholders: list[str]
    broad_capable: bool
