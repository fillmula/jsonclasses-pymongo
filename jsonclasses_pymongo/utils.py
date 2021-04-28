from __future__ import annotations
from typing import Union, TYPE_CHECKING
from inflection import camelize
from jsonclasses.field_definition import FieldType
if TYPE_CHECKING:
    from .pymongo_object import PymongoObject


def ref_key(key: str, cls: type[PymongoObject]) -> tuple[str, str]:
    field_name = key + '_id'
    if cls.dbconf.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return (field_name, db_field_name)


def ref_field_key(key: str) -> str:
    return key + '_id'


def ref_db_field_key(key: str, cls: type[PymongoObject]) -> str:
    field_name = ref_field_key(key)
    if cls.dbconf.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return db_field_name


def ref_field_keys(key: str) -> str:
    return key + '_ids'


def ref_db_field_keys(key: str, cls: type[PymongoObject]) -> str:
    field_name = ref_field_keys(key)
    if cls.dbconf.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return db_field_name


def btype_from_ftype(field_type: FieldType) -> Union[str, list[str]]:
    if field_type == FieldType.STR:
        return 'string'
    elif field_type == FieldType.INT:
        return ['int', 'long', 'decimal']
    elif field_type == FieldType.FLOAT:
        return 'double'
    elif field_type == FieldType.BOOL:
        return 'bool'
    elif field_type == FieldType.DATE:
        return 'date'
    elif field_type == FieldType.DATETIME:
        return 'date'
    else:
        return []
