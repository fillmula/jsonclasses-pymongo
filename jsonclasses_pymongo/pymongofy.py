from __future__ import annotations
from typing import TypeVar, Any, Union, cast
from re import search
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from inflection import camelize, underscore
from jsonclasses.exceptions import UniqueConstraintException
from .pymongo_object import PymongoObject
from .query import ListQuery, SingleQuery, IDQuery
from .encoder import Encoder


T = TypeVar('T', bound=PymongoObject)


def find(cls: type[T], **kwargs: Any) -> ListQuery[T]:
    return ListQuery(cls=cls, filter=kwargs)


def one(cls: type[T], **kwargs: Any) -> SingleQuery[T]:
    return SingleQuery(cls=cls, filter=kwargs)


def pymongo_id(cls: type[T], id: Union[str, ObjectId]) -> IDQuery[T]:
    return IDQuery(cls=cls, id=id)


def _database_write(self: T) -> None:
    try:
        Encoder().encode_root(self).execute()
    except DuplicateKeyError as exception:
        result = search('index: (.+?)_1', exception._message)
        db_key = result.group(1)
        pt_key = db_key
        json_key = db_key
        if self.__class__.config.camelize_db_keys:
            pt_key = underscore(db_key)
            json_key = pt_key
        if self.__class__.config.camelize_json_keys:
            json_key = camelize(pt_key, False)
        raise UniqueConstraintException(
                getattr(self, pt_key), json_key) from None

def pymongofy(class_: type) -> PymongoObject:
    # do not install methods for subclasses
    if hasattr(class_, '__is_pymongo__'):
        return cast(PymongoObject, class_)
    # type marks
    setattr(class_, '__is_pymongo__', True)
    # public methods
    class_.find = classmethod(find)
    class_.one = one
    class_.id = pymongo_id
    # protected methods
    class_._database_write = _database_write

    return class_
