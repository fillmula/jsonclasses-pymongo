from __future__ import annotations
from typing import TYPE_CHECKING
from inflection import singularize
if TYPE_CHECKING:
    from .pymongo_object import PymongoObject


def ref_key(key: str, cls: type[PymongoObject]) -> tuple[str, str]:
    field_name = key + '_id'
    db_field_name = cls.pconf.to_db_key(field_name)
    return (field_name, db_field_name)


def ref_field_key(key: str) -> str:
    return key + '_id'


def ref_db_field_key(key: str, cls: type[PymongoObject]) -> str:
    field_name = ref_field_key(key)
    db_field_name = cls.pconf.to_db_key(field_name)
    return db_field_name


def ref_field_keys(key: str) -> str:
    return singularize(key) + '_ids'


def ref_db_field_keys(key: str, cls: type[PymongoObject]) -> str:
    field_name = ref_field_keys(key)
    db_field_name = cls.pconf.to_db_key(field_name)
    return db_field_name
