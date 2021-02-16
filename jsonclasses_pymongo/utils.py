from __future__ import annotations
from typing import TYPE_CHECKING
from inflection import camelize
if TYPE_CHECKING:
    from .base_mongo_object import BaseMongoObject


def ref_key(key: str, cls: type[BaseMongoObject]) -> tuple[str, str]:
    field_name = key + '_id'
    if cls.config.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return (field_name, db_field_name)


def ref_field_key(key: str) -> str:
    return key + '_id'


def ref_db_field_key(key: str, cls: type[BaseMongoObject]) -> str:
    field_name = ref_field_key(key)
    if cls.config.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return db_field_name


def ref_field_keys(key: str) -> str:
    return key + '_ids'


def ref_db_field_keys(key: str, cls: type[BaseMongoObject]) -> str:
    field_name = ref_field_keys(key)
    if cls.config.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return db_field_name
