"""Abstract interface for v2 live execution via official APIs.

v1 is emit-only: nothing in this package makes network requests, and no
concrete Executor may be implemented or registered until v2. This module
exists so the rest of the codebase can be designed around the seam.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class ExecutorResult(BaseModel):
    """A single result returned by an official search API."""

    title: str
    url: str
    snippet: str | None = None


class Executor(ABC):
    """Runs a generated query against an official API (e.g. Google CSE, Shodan).

    Implementations must use the provider's official, authenticated API,
    respect its terms and rate limits, and never scrape.
    """

    #: Stable identifier, e.g. "google_cse" or "shodan".
    name: str

    @abstractmethod
    def supports(self, engine: str) -> bool:
        """Return True if this executor can run queries written for ``engine``."""

    @abstractmethod
    def execute(self, query: str, *, limit: int = 10) -> list[ExecutorResult]:
        """Execute ``query`` and return up to ``limit`` results."""
