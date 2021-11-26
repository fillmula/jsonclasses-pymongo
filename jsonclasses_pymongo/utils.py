from __future__ import annotations
from typing import cast, TYPE_CHECKING
from jsonclasses.fdef import FSubtype
from jsonclasses.jobject import JObject
from jsonclasses.jfield import JField
from inflection import singularize
from bson.objectid import ObjectId
from .connection import Connection
if TYPE_CHECKING:
    from .pobject import PObject


# These 4 helpers are for join table

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


def list_inst_type(field: JField) -> type[PObject]:
    from .pobject import PObject
    return cast(PObject, field.types.fdef.item_types.fdef.inst_cls)


def join_table_name(this: JField) -> str:
    from .pobject import PObject
    that = this.foreign_field
    this_cls = cast(type[PObject], this.cdef.cls)
    that_cls = cast(type[PObject], that.cdef.cls)
    this_fname = this_cls.pconf.to_db_key(this.name)
    that_fname = that_cls.pconf.to_db_key(that.name)
    connection = Connection.from_class(this_cls)
    cabase = connection.collection_from(this_cls).name
    cbbase = connection.collection_from(that_cls).name
    ca = cabase + this_fname.lower()
    cb = cbbase + that_fname.lower()
    return ca + cb if ca < cb else cb + ca
