from __future__ import annotations
from typing import TypeVar, Any, Union
from jsonclasses import (jsonclass, ORMObject, get_fields,
                         ObjectNotFoundException, UniqueConstraintException)
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from inflection import camelize, pluralize, underscore
from re import search
from .encoder import Encoder
from .query import IDQuery, ListQuery, SingleQuery, OptionalSingleQuery
from .connector import connector
from .utils import btype_from_ftype


@jsonclass(abstract=True)
class BaseMongoObject(ORMObject):
    """BaseMongoObject is a `JSONObject` subclass for defining your business
    models with MongoDB. A `BaseMongoObject` class represents a MongoDB
    collection. This class doesn't define standard primary key field and
    timestamp fields. If you want to use standard fields, consider using
    `MongoObject`.
    """

    @classmethod
    def collection(cls: type[T]) -> Collection:
        name = pluralize(cls.__name__).lower()
        return connector.collection(name)

    @classmethod
    def __loaded__(cls: type[T], class_: type[T]) -> None:
        if class_.config.abstract:
            return
        name = pluralize(class_.__name__).lower()

        def sync_db_settings(coll: Collection) -> None:
            fields = get_fields(class_)
            info = coll.index_information()
            for field in fields:
                name = field.db_field_name
                index = field.fdesc.index
                unique = field.fdesc.unique
                required = field.fdesc.required
                index_name = f'{name}_1'
                ftype = field.fdesc.field_type
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

        connector._add_callback(name, sync_db_settings)

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

    @classmethod
    def delete_by_id(self, id: str) -> None:
        deletion_result = self.collection().delete_one({'_id': ObjectId(id)})
        if deletion_result.deleted_count < 1:
            raise ObjectNotFoundException(
                f'{self.__name__} with id \'{id}\' is not found.')
        else:
            return None

    @classmethod
    def delete(self, *args, **kwargs) -> int:
        if len(args) == 0:
            args = ({},)
        return self.collection().delete_many(*args, **kwargs).deleted_count

    @classmethod
    def find_by_id(cls: type[T], id: Union[str, ObjectId]) -> IDQuery:
        return IDQuery(cls=cls, id=id)

    @classmethod
    def with_id(cls: type[T], id: Union[str, ObjectId]) -> IDQuery:
        return cls.find_by_id(id)

    @classmethod
    def find(cls: type[T], **kwargs: Any) -> ListQuery:
        return ListQuery(cls=cls, filter=kwargs)

    @classmethod
    def find_one(cls: type[T], **kwargs: Any) -> SingleQuery:
        if kwargs.get('id'):
            kwargs['_id'] = ObjectId(kwargs['id'])
            del kwargs['id']
        return SingleQuery(ListQuery(cls=cls, filter=kwargs))

    @classmethod
    def find_by(cls: type[T], **kwargs: Any) -> OptionalSingleQuery:
        return OptionalSingleQuery(cls.find_one(**kwargs))


T = TypeVar('T', bound=BaseMongoObject)
