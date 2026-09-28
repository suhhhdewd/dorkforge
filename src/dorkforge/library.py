"""Loader for the packaged dork library."""

from importlib.resources import files

import yaml
from pydantic import ValidationError

from dorkforge.models import Dork


def load_dorks() -> list[Dork]:
    """Load, parse, and validate the packaged dork library.

    Reads ``data/dorks.yaml`` from packaged data, parses it as a top-level
    list, and validates every record into a :class:`Dork`.

    Raises:
        ValueError: if the file is not a top-level list, or if any record
            fails validation. The message names the offending record's id
            and the field error so bad data fails loudly.
    """
    raw = files("dorkforge.data").joinpath("dorks.yaml").read_text(encoding="utf-8")
    data = yaml.safe_load(raw)

    if not isinstance(data, list):
        raise ValueError(f"dorks.yaml must be a top-level list, got {type(data).__name__}")

    dorks: list[Dork] = []
    for index, record in enumerate(data):
        record_id = record.get("id") if isinstance(record, dict) else None
        label = f"id={record_id}" if record_id is not None else f"index {index}"
        try:
            dorks.append(Dork.model_validate(record))
        except ValidationError as exc:
            raise ValueError(f"Invalid dork record ({label}): {exc}") from exc

    return dorks
