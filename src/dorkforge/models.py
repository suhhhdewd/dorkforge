"""Pydantic data models."""

from enum import StrEnum


class RunMode(StrEnum):
    """How queries are generated.

    TARGETED requires a scope value; BROAD takes none.
    """

    TARGETED = "targeted"
    BROAD = "broad"
