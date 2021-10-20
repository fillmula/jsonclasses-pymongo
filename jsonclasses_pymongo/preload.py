from __future__ import annotations
from typing import Any
from os import getcwd
from pathlib import Path
from json import load
from bson.objectid import ObjectId
from jsonclasses.cgraph import CGraph
from jsonclasses.jfield import JField
from jsonclasses.fdef import FStore
from pymongo import ASCENDING
from pymongo.collection import Collection
from .pymongo_object import PymongoObject
from .connection import Connection


_refkeycolls: dict[str, Collection] = {}


def getrefkeycoll(cls: type[PymongoObject]) -> Collection:
    global _refkeycolls
    gname = cls.cdef.jconf.cgraph.name
    if _refkeycolls.get(gname) is not None:
        return _refkeycolls.get(gname)
    coll = Connection(gname).collection('_refkeys')
    coll.create_index([
        ('graph', ASCENDING), ('class', ASCENDING), ('sid', ASCENDING)
    ], name='graph_class_sid', unique=True)
    coll.create_index('oid', name='oid_1', unique=True)
    _refkeycolls[gname] = coll
    return _refkeycolls[gname]


def getidref(cls: type[PymongoObject], id: str | int) -> str | int:
    coll = getrefkeycoll(cls)
    matcher = {
        'graph': cls.cdef.jconf.cgraph.name, 'cls': cls.__name__, 'sid': id
    }
    result = coll.find_one(matcher)
    if result is not None:
        oid = result['oid']
        return str(oid) if type(oid) is ObjectId else oid
    else:
        oid = ObjectId()
        coll.insert_one({**matcher, 'oid': oid})
        return str(oid)


def getfieldvalue(obj: dict[str, Any], field: JField) -> Any | None:
    val = obj.get(field.name)
    if val is None:
        return obj.get(field.json_name)
    return val


def seedobject(cls: type[PymongoObject], obj: dict[str, Any], oid: str | int, original: PymongoObject) -> None:
    result: dict[str, Any] = {}
    for field in cls.cdef.fields:
        if field.fdef.primary:
            continue
        elif field.fdef.fstore == FStore.EMBEDDED:
            result[field.name] = getfieldvalue(obj, field)
        elif field.fdef.fstore == FStore.LOCAL_KEY:
            frcls = field.foreign_class
            field_ref_name = cls.cdef.jconf.ref_key_encoding_strategy(field)
            result[field_ref_name] = getidref(frcls, getfieldvalue(obj, field))
    if original:
        original.set(**result).save()
    else:
        pobj = cls(**result)
        setattr(pobj, cls.cdef.primary_field.name, oid)
        pobj.save()


def loadobject(cls: type[PymongoObject], obj: dict[str, Any]) -> None:
    fvalues: dict[str, Any] = {}
    behaviors: dict[str, Any] = {}
    for key, value in obj.items():
        if key.startswith('_'):
            behaviors[key] = value
        else:
            fvalues[key] = value
    strategy = behaviors.get('_strategy') or 'seed'
    pfield = cls.cdef.primary_field
    if pfield is None:
        raise ValueError('class should have a primary field')
    fval = getfieldvalue(fvalues, pfield)
    if fval is None:
        raise ValueError('please assign a primary key name')
    oid = getidref(cls, fval)
    exist_object = cls.id(oid).optional.exec()
    if exist_object is None:
        seedobject(cls, fvalues, oid, None)
    elif strategy == 'reseed':
        seedobject(cls, fvalues, oid, exist_object)


def loadjson(jsondata: list[Any] | dict[str, Any]) -> None:
    if isinstance(jsondata, list):
        enumerator = enumerate(jsondata)
    elif isinstance(jsondata, dict):
        enumerator = jsondata.items()
    else:
        enumerator = enumerate([])
    for _, item in enumerator:
        class_name = item['class']
        graph = item.get('graph') or 'default'
        objects = item['objects']
        cgraph = CGraph(graph)
        cls = cgraph.fetch(class_name).cls
        for obj in objects:
            loadobject(cls, obj)


def preload(filepath: str | list[str] = 'data.json') -> None:
    filepaths = [filepath] if type(filepath) is str else filepath
    cwd = Path(getcwd())
    for filepath in filepaths:
        fullpath = cwd / filepath
        if fullpath.is_file():
            with open(fullpath) as filedata:
                jsondata = load(filedata)
                loadjson(jsondata)
