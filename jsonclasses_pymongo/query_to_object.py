from __future__ import annotations
from typing import Any


def raise_qsparser_kindly():
    raise ModuleNotFoundError('please install qsparser for receiving query '
                              'string as find argument')


def query_to_object(query: str) -> dict[str, Any]:
    try:
        from qsparser import parse
    except ModuleNotFoundError as e:
        raise_qsparser_kindly()
    return parse(query)
