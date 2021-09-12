from __future__ import annotations
from typing import Any, cast
from datetime import datetime, date, timedelta
from re import compile, escape, IGNORECASE
from inflection import camelize
from bson.objectid import ObjectId
from jsonclasses.fdef import FStore, FType
from .pymongo_object import PymongoObject
from .readers import (
    readbool, readdate, readdatetime, readenum, readfloat, readint, readorder
)


class QueryReader:

    def __init__(self: QueryReader,
                 query: dict[str, Any],
                 cls: type[PymongoObject]) -> None:
        self.query = query
        self.cls = cls

    def result(self: QueryReader) -> Any:
        instructors = {}
        fields = {}
        for key, value in self.query.items():
            if key.startswith('_'):
                instructors[key] = value
            else:
                fields[key] = value
        iresult = self.instructors_result(instructors)
        fresult = self.fields_result(fields)
        return {'_match': fresult, **iresult}

    def instructors_result(self: QueryReader,
                           instructors: dict[str, Any]) -> Any:
        result: dict[str, Any] = {}
        for raw_key, value in instructors.items():
            key = self.cls.cdef.jconf.key_decoding_strategy(raw_key)
            if key == '_skip':
                result['_skip'] = readint(value)
            elif key == '_limit':
                result['_limit'] = readint(value)
            elif key == '_page_size':
                result['_page_size'] = readint(value)
            elif key == '_page_number':
                result['_page_number'] = readint(value)
            elif key == '_page_no':
                result['_page_number'] = readint(value)
            elif key == '_order':
                result['_sort'] = self.readorders(value)
        return result

    def readorders(self: QueryReader, val: Any) -> list[tuple[str, int]]:
        result = []
        if isinstance(val, dict):
            for raw_key, value in val.items():
                key = self.cls.cdef.jconf.key_decoding_strategy(raw_key)
                result.append((key, readorder(value)))
            return result
        if isinstance(val, list):
            for obj in val:
                result.extend(self.readorders(obj))
            return result
        if isinstance(val, str):
            if val.startswith('-'):
                o = -1
                val = val[1:]
            else:
                o = 1
            key = self.cls.cdef.jconf.key_decoding_strategy(val)
            result.append((key, o))
            return result
        raise ValueError('unaccepted order descriptor')

    def fields_result(self: QueryReader,
                      query: dict[str, Any],
                      prefix: list[str] = []) -> Any:
        result = {}
        for raw_key, value in query.items():
            key = self.cls.cdef.jconf.key_decoding_strategy(raw_key)
            if self.cls.pconf.camelize_db_keys:
                dbkey = camelize(key, False)
            else:
                dbkey = key
            if key in self.cls.cdef.reference_names:
                result[dbkey] = ObjectId(value) if value is not None else None
                continue
            field = self.cls.cdef.field_named(key)
            if field is None:
                raise ValueError(f'unexist field {key}')
            if field.fdef.primary is True:
                result['_id'] = ObjectId(value) if value is not None else None
            elif field.fdef.field_type == FType.STR:
                result[dbkey] = self.str_descriptor(value)
            elif field.fdef.field_type == FType.INT:
                result[dbkey] = self.num_descriptor(value, False)
            elif field.fdef.field_type == FType.FLOAT:
                result[dbkey] = self.num_descriptor(value, True)
            elif field.fdef.field_type == FType.BOOL:
                result[dbkey] = self.bool_descriptor(value)
            elif field.fdef.field_type == FType.DATE:
                result[dbkey] = self.date_descriptor(value, True)
                result[dbkey] = readdate(value)
            elif field.fdef.field_type == FType.DATETIME:
                result[dbkey] = self.date_descriptor(value, False)
                result[dbkey] = readdatetime(value)
            elif field.fdef.field_type == FType.ENUM:
                result[dbkey] = readenum(value, field.fdef.enum_class)
            else:
                result[dbkey] = value
        return result

    def str_descriptor(self: QueryReader, val: Any) -> Any:
        if val is None:
            return val
        if type(val) is str:
            return val
        if isinstance(val, dict):
            result = {}
            for raw_key, value in val.items():
                if raw_key.startswith('$'):
                    result[raw_key] = value
                    continue
                key = self.cls.cdef.jconf.key_decoding_strategy(raw_key)
                if key == '_contains':
                    result['$regex'] = compile(escape(value))
                elif key == '_prefix':
                    result['$regex'] = compile('^' + escape(value))
                elif key == '_suffix':
                    result['$regex'] = compile(escape(value) + '$')
                elif key == '_match':
                    result['$regex'] = compile(value)
                elif key == '_containsi':
                    result['$regex'] = compile(escape(value), IGNORECASE)
                elif key == '_prefixi':
                    result['$regex'] = compile('^' + escape(value), IGNORECASE)
                elif key == '_suffixi':
                    result['$regex'] = compile(escape(value) + '$', IGNORECASE)
                elif key == '_matchi':
                    result['$regex'] = compile(value, IGNORECASE)
                elif key == '_equal':
                    result['$eq'] = value
                elif key == '_field_exists':
                    result['$exists'] = readbool(value)
                elif key == '_not':
                    if type(value) is str:
                        result['$ne'] = value
                    else:
                        result['$not'] = self.str_descriptor(value)
                else:
                    raise ValueError(f'unrecognized str matcher key {key}')
            return result

    def num_descriptor(self: QueryReader, val: Any, float: bool) -> Any:
        if val is None:
            return val
        if type(val) is float:
            return val
        if type(val) is int:
            return val
        if type(val) is str:
            return readfloat(val) if float else readint(val)
        if isinstance(val, dict):
            result = {}
            for raw_key, value in val.items():
                if raw_key.startswith('$'):
                    result[raw_key] = value
                    continue
                key = self.cls.cdef.jconf.key_decoding_strategy(raw_key)
                if key == '_eq':
                    result['$eq'] = readfloat(value) if float else readint(value)
                elif key == '_gt':
                    result['$gt'] = readfloat(value) if float else readint(value)
                elif key == '_gte':
                    result['$gte'] = readfloat(value) if float else readint(value)
                elif key == '_lt':
                    result['$lt'] = readfloat(value) if float else readint(value)
                elif key == '_lte':
                    result['$lte'] = readfloat(value) if float else readint(value)
                elif key == '_not':
                    if type(value) is str or type(value) is float or type(value) is int:
                        result['$ne'] = readfloat(value) if float else readint(value)
                    else:
                        result['$not'] = self.num_descriptor(value, float)
                else:
                    raise ValueError(f'unrecognized str matcher key {key}')
            return result

    def bool_descriptor(self: QueryReader, val: Any) -> Any:
        if val is None:
            return val
        if type(val) is bool:
            return val
        if type(val) is str:
            return readbool(val)
        if isinstance(val, dict):
            result = {}
            for raw_key, value in val.items():
                if raw_key.startswith('$'):
                    result[raw_key] = value
                    continue
                key = self.cls.cdef.jconf.key_decoding_strategy(raw_key)
                if key == '_ne':
                    result['$ne'] = readbool(value)
                elif key == '_eq':
                    result['$eq'] = readbool(value)
                elif key == '_is':
                    result['$eq'] = readbool(value)
            return result

    def date_descriptor(self: QueryReader, val: Any, is_date: bool) -> Any:
        if val is None:
            return val
        if type(val) is float:
            return readdate(val) if is_date else readdatetime(val)
        if type(val) is int:
            return readdate(val) if is_date else readdatetime(val)
        if type(val) is str:
            return readdate(val) if is_date else readdatetime(val)
        if isinstance(val, dict):
            result = {}
            for raw_key, value in val.items():
                if raw_key.startswith('$'):
                    result[raw_key] = value
                    continue
                key = self.cls.cdef.jconf.key_decoding_strategy(raw_key)
                if key == '_eq':
                    result['$eq'] = readdate(value) if is_date else readdatetime(value)
                elif key == '_gt':
                    result['$gt'] = readdate(value) if is_date else readdatetime(value)
                elif key == '_gte':
                    result['$gte'] = readdate(value) if is_date else readdatetime(value)
                elif key == '_lt':
                    result['$lt'] = readdate(value) if is_date else readdatetime(value)
                elif key == '_lte':
                    result['$lte'] = readdate(value) if is_date else readdatetime(value)
                elif key == '_after':
                    result['$gt'] = readdate(value) if is_date else readdatetime(value)
                elif key == '_before':
                    result['$lt'] = readdate(value) if is_date else readdatetime(value)
                elif key == '_on':
                    day = cast(date, readdate(value))
                    nextday = day + timedelta(days=1)
                    result['$gte'] = day
                    result['lt'] = nextday
                elif key == '_not':
                    if type(value) is str or type(value) is float or type(value) is int or type(value) is date or type(value) is datetime:
                        result['$ne'] = readdate(value) if is_date else readdatetime(value)
                    else:
                        result['$not'] = self.date_descriptor(value, is_date)
                else:
                    raise ValueError(f'unrecognized str matcher key {key}')
            return result
