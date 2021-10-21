from __future__ import annotations
from typing import Union, TYPE_CHECKING
from inflection import camelize
from jsonclasses.fdef import FType
if TYPE_CHECKING:
    from .pymongo_object import PymongoObject


def ref_key(key: str, cls: type[PymongoObject]) -> tuple[str, str]:
    field_name = key + '_id'
    if cls.pconf.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return (field_name, db_field_name)


def ref_field_key(key: str) -> str:
    return key + '_id'


def ref_db_field_key(key: str, cls: type[PymongoObject]) -> str:
    field_name = ref_field_key(key)
    if cls.pconf.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return db_field_name


def ref_field_keys(key: str) -> str:
    from inflection import singularize
    return singularize(key) + '_ids'


def ref_db_field_keys(key: str, cls: type[PymongoObject]) -> str:
    field_name = ref_field_keys(key)
    if cls.pconf.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return db_field_name
