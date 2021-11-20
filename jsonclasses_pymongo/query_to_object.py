from __future__ import annotations
from typing import Any
from qsparser import parse


def query_to_object(query: str) -> dict[str, Any]:
    return parse(query)
