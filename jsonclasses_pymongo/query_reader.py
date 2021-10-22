from __future__ import annotations
from typing import Any, cast
from datetime import datetime, date, timedelta
from re import compile, escape, IGNORECASE
from inflection import camelize
from bson.objectid import ObjectId
from jsonclasses.fdef import FStore, FType, Fdef
from .pymongo_object import PymongoObject
from .readers import (
    readstr, readbool, readdate, readdatetime, readenum, readfloat, readint,
    readorder
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
        if '_virtual' in fresult:
            virtual = fresult['_virtual']
            fresult.pop('_virtual')
            iresult['_virtual'] = virtual
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
            elif key == '_includes':
                result['_includes'] = value
            elif key == '_omit':
                result['_omit'] = value
            elif key == '_pick':
                result['_pick'] = value
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
            # handle local key query
            if key in self.cls.cdef.reference_names:
                idval = readstr(value)
                result[dbkey] = ObjectId(idval) if idval is not None else None
                continue
            # handle local keys
            if key in self.cls.cdef.list_reference_names:
                and_mode = False
                if isinstance(value, dict):
                    if value.get('_or'):
                        value = value['_or']
                    elif value.get('_and'):
                        value = value['_and']
                        and_mode = True
                if not and_mode:
                    result[dbkey] = {'$in': [ObjectId(v) for v in value]}
                else:
                    result[dbkey] = {'$all': [ObjectId(v) for v in value]}
                continue
            # handle virtual local keys
            if key in self.cls.cdef.virtual_reference_names:
                if result.get('_virtual') is None:
                    result['_virtual'] = []
                f = self.cls.cdef.virtual_reference_fields[key]
                result['_virtual'].append((key, f, value))
                continue
            # handle embedded fields
            field = self.cls.cdef.field_named(key)
            if field is None:
                raise ValueError(f'unexist field {key}')
            fdef = field.fdef
            if fdef.primary is True:
                result['_id'] = ObjectId(value) if value is not None else None
            else:
                result[dbkey] = self.readval(value, fdef)
        return result

    def readval(self: QueryReader, val: Any, fdef: Fdef):
        if fdef.ftype == FType.STR:
            return self.str_descriptor(val)
        elif fdef.ftype == FType.INT:
            return self.num_descriptor(val, False)
        elif fdef.ftype == FType.FLOAT:
            return self.num_descriptor(val, True)
        elif fdef.ftype == FType.BOOL:
            return self.bool_descriptor(val)
        elif fdef.ftype == FType.DATE:
            return self.date_descriptor(val, True)
        elif fdef.ftype == FType.DATETIME:
            return self.date_descriptor(val, False)
        elif fdef.ftype == FType.ENUM:
            return readenum(val, fdef.enum_class)
        elif fdef.ftype == FType.LIST and fdef.fstore == FStore.EMBEDDED:
            return self.list_descriptor(val, fdef)
        elif fdef.ftype == FType.DICT:
            return self.dict_descriptor(val, fdef)
        else:
            return val

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
        if type(val) is datetime:
            return readdate(val) if is_date else readdatetime(val)
        if type(val) is date:
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

    def list_descriptor(self: QueryReader, val: Any, fdef: Fdef) -> Any:
        if val is None:
            return val
        if isinstance(val, list):
            return [self.readval(item, fdef.item_types.fdef) for item in val]
        if isinstance(val, dict):
            result = {}
            for raw_key, value in val.items():
                if raw_key.startswith('$'):
                    result[raw_key] = value
                    continue
                key = self.cls.cdef.jconf.key_decoding_strategy(raw_key)
                if key == '_eq':
                    result['$eq'] = [self.readval(item, fdef.item_types.fdef) for item in value]
                elif key == '_contains':
                    if isinstance(value, list):
                        result['$all'] = [self.readval(item, fdef.item_types.fdef) for item in value]
                    else:
                        result['$all'] = [self.readval(value, fdef.item_types.fdef)]
                # TODO: contains a matcher or matchers, object matcher, list matcher, primitive types matcher
            return result

    def dict_descriptor(self: QueryReader, val: Any, fdef: Fdef) -> Any:
        if val is None:
            return val
        if isinstance(val, dict):
            pass
