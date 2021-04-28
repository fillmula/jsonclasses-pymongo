from __future__ import annotations
from typing import TypeVar, Any, Union, cast
from re import search
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from inflection import camelize, underscore
from pymongo.collection import Collection
from jsonclasses.exceptions import (UniqueConstraintException,
                                    ObjectNotFoundException)
from .pymongo_object import PymongoObject
from .query import ListQuery, SingleQuery, IDQuery
from .encoder import Encoder
from .connection import Connection
from .utils import btype_from_ftype


T = TypeVar('T', bound=PymongoObject)


def find(cls: type[T], **kwargs: Any) -> ListQuery[T]:
    return ListQuery(cls=cls, filter=kwargs)


def one(cls: type[T], **kwargs: Any) -> SingleQuery[T]:
    return ListQuery(cls=cls, filter=kwargs).first


def pymongo_id(cls: type[T], id: Union[str, ObjectId]) -> IDQuery[T]:
    return IDQuery(cls=cls, id=id)


def delete_by_id(cls: type[T], id: str) -> None:
    collection = Connection.get_collection(cls)
    deletion_result = collection.delete_one({'_id': ObjectId(id)})
    if deletion_result.deleted_count < 1:
        raise ObjectNotFoundException(
            f'{cls.__name__} with id \'{id}\' is not found.')
    else:
        return None


def delete_many(cls: type[T], *args, **kwargs) -> int:
    if len(args) == 0:
        args = ({},)
    collection = Connection.get_collection(cls)
    return collection.delete_many(*args, **kwargs).deleted_count


def _database_write(self: T) -> None:
    try:
        Encoder().encode_root(self).execute()
    except DuplicateKeyError as exception:
        result = search('index: (.+?)_1', exception._message)
        assert result is not None
        db_key = result.group(1)
        pt_key = db_key
        json_key = db_key
        if self.__class__.dbconf.camelize_db_keys:
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
    class_.one = classmethod(one)
    class_.id = classmethod(pymongo_id)
    class_.delete_many = classmethod(delete_many)
    class_.delete_by_id = classmethod(delete_by_id)
    # protected methods
    class_._database_write = _database_write
    connection = Connection.from_class(class_)
    if class_.definition.config.abstract:
        return class_
    def callback(coll: Collection):
        info = coll.index_information()
        for field in class_.definition.fields:
            name = field.name
            if class_.dbconf.camelize_db_keys:
                name = camelize(field.name, False)
            index = field.definition.index
            unique = field.definition.unique
            required = field.definition.required
            index_name = f'{name}_1'
            ftype = field.definition.field_type
            if unique:
                if required:
                    coll.create_index(name, name=index_name, unique=True)
                else:
                    coll.create_index(
                        name, name=index_name, unique=True,
                        partialFilterExpression={
                            name: {'$type': btype_from_ftype(ftype)}
                        })
            elif index:
                if required:
                    coll.create_index(name, name=index_name)
                else:
                    coll.create_index(
                        name, name=index_name,
                        partialFilterExpression={
                            name: {'$type': btype_from_ftype(ftype)}
                        })
            else:
                if index_name in info.keys():
                    coll.drop_index(index_name)
    connection.add_connected_callback(class_.dbconf.collection_name, callback)
    return class_
