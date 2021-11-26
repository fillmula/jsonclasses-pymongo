from __future__ import annotations
from typing import TYPE_CHECKING
from jsonclasses.fdef import FSubtype
from jsonclasses.jobject import JObject
from jsonclasses.jfield import JField
from inflection import singularize
from bson.objectid import ObjectId
if TYPE_CHECKING:
    from .pobject import PObject


def ref_key(key: str, cls: type[PObject]) -> tuple[str, str]:
    field_name = key + '_id'
    db_field_name = cls.pconf.to_db_key(field_name)
    return (field_name, db_field_name)


def ref_field_key(key: str) -> str:
    return key + '_id'


def ref_db_field_key(key: str, cls: type[PObject]) -> str:
    field_name = ref_field_key(key)
    db_field_name = cls.pconf.to_db_key(field_name)
    return db_field_name


def ref_field_keys(key: str) -> str:
    return singularize(key) + '_ids'


def ref_db_field_keys(key: str, cls: type[PObject]) -> str:
    field_name = ref_field_keys(key)
    db_field_name = cls.pconf.to_db_key(field_name)
    return db_field_name


def idval(field: JField, val: str) -> str | ObjectId:
    if field.fdef.fsubtype == FSubtype.MONGOID:
        return ObjectId(val)
    return val

def dbid(obj: JObject) -> str | ObjectId:
    field = obj.__class__.cdef.primary_field
    val = obj._id
    return idval(field, val)
