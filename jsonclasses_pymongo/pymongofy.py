from __future__ import annotations
from typing import TypeVar, Any, Union, cast
from re import search
from bson.objectid import ObjectId
from jsonclasses.jsonclass_field import JSONClassField
from pymongo.errors import DuplicateKeyError
from inflection import camelize, underscore
from pymongo.collection import Collection
from jsonclasses.field_definition import FieldStorage, FieldType
from jsonclasses.exceptions import UniqueConstraintException
from jsonclasses.types_resolver import TypesResolver
from jsonclasses.exceptions import DeletionDeniedException
from .pymongo_object import PymongoObject
from .query import BaseQuery, ExistQuery, IterateQuery, ListQuery, SingleQuery, IDQuery
from .encoder import Encoder
from .connection import Connection
from .utils import btype_from_ftype, ref_db_field_key
from .coder import Coder


T = TypeVar('T', bound=PymongoObject)


def find(cls: type[T], **kwargs: Any) -> ListQuery[T]:
    return ListQuery(cls=cls, filter=kwargs)


def one(cls: type[T], **kwargs: Any) -> SingleQuery[T]:
    return SingleQuery(cls=cls, filter=kwargs)


def pymongo_id(cls: type[T], id: Union[str, ObjectId]) -> IDQuery[T]:
    return IDQuery(cls=cls, id=id)


def linked(cls: type[T]) -> BaseQuery[T]:
    return BaseQuery(cls=cls)


def exist(cls: type[T], **kwargs: Any) -> ExistQuery[T]:
    return ExistQuery(cls=cls, filter=kwargs)


def iterate(cls: type[T], **kwargs: Any) -> IterateQuery[T]:
    return IterateQuery(cls=cls, filter=kwargs)


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
        if self.__class__.definition.config.camelize_json_keys:
            json_key = camelize(pt_key, False)
        raise UniqueConstraintException(
                getattr(self, pt_key), json_key) from None


def _orm_delete(self: T, no_raise: bool = False) -> None:
    # deny test
    for field in self.__class__.definition.deny_fields:
        if field.definition.field_storage == FieldStorage.LOCAL_KEY:
            key = self.__class__.definition.config.key_transformer(field)
            if hasattr(self, key) and getattr(self, key) is not None:
                if no_raise:
                    return
                else:
                    raise DeletionDeniedException()
        elif field.definition.field_storage == FieldStorage.FOREIGN_KEY:
            r = TypesResolver()
            if field.definition.field_type == FieldType.LIST:
                t = r.resolve_types(field.definition.raw_item_types,
                                    self.__class__.definition.config)
            else:
                t = r.resolve_types(field.definition.instance_types,
                                    self.__class__.definition.config)
            types = t
            oc = cast(type[PymongoObject], types.definition.instance_types)
            f = cast(JSONClassField, field.foreign_field)
            if field.definition.use_join_table:
                jtname = Coder().join_table_name(
                    self.__class__,
                    field.name,
                    oc,
                    f.name)
                coll = Connection.from_class(self.__class__).collection(jtname)
                key = ref_db_field_key(self.__class__.__name__, self.__class__)
                e = coll.count_documents({key: ObjectId(self._id)}, limit=1)
                exist = e > 0
                if exist:
                    if no_raise:
                        return
                    else:
                        raise DeletionDeniedException()
            else:
                key = oc.definition.config.key_transformer(f)
                exist = oc.exist(**{key: ObjectId(self._id)}).exec()
                if exist:
                    if no_raise:
                        return
                    else:
                        raise DeletionDeniedException()

    collection = Connection.get_collection(self.__class__)
    collection.delete_one({'_id': ObjectId(self._id)})

    # delete chain - nullify
    for field in self.__class__.definition.nullify_fields:
        if field.definition.field_storage == FieldStorage.FOREIGN_KEY:
            r = TypesResolver()
            if field.definition.field_type == FieldType.LIST:
                t = r.resolve_types(field.definition.raw_item_types,
                                    self.__class__.definition.config)
            else:
                t = r.resolve_types(field.definition.instance_types,
                                    self.__class__.definition.config)
            types = t
            oc = cast(type[PymongoObject], types.definition.instance_types)
            f = cast(JSONClassField, field.foreign_field)
            if field.definition.use_join_table:
                jtname = Coder().join_table_name(
                    self.__class__,
                    field.name,
                    oc,
                    f.name)
                coll = Connection.from_class(self.__class__).collection(jtname)
                key = ref_db_field_key(self.__class__.__name__, self.__class__)
                coll.delete_many({key: ObjectId(self._id)})
            else:
                key = oc.definition.config.key_transformer(f)
                for o in oc.iterate(**{key: ObjectId(self._id)}).exec():
                    setattr(o, f.name, None)
                    setattr(o, key, None)
                    o.save(skip_validation=True)

    # delete chain - cascade
    for field in self.__class__.definition.cascade_fields:
        r = TypesResolver()
        if field.definition.field_type == FieldType.LIST:
            t = r.resolve_types(field.definition.raw_item_types,
                                self.__class__.definition.config)
        else:
            t = r.resolve_types(field.definition.instance_types,
                                self.__class__.definition.config)
        types = t
        types = t
        oc = cast(type[PymongoObject], types.definition.instance_types)
        f = cast(JSONClassField, field.foreign_field)
        if field.definition.field_storage == FieldStorage.LOCAL_KEY:
            key = self.__class__.definition.config.key_transformer(field)
            if getattr(self, key) is not None:
                item = oc.id(getattr(self, key)).optional.exec()
                if item is not None:
                    item._orm_delete(no_raise=True)
        elif field.definition.field_storage == FieldStorage.FOREIGN_KEY:
            if field.definition.use_join_table:
                jtname = Coder().join_table_name(
                    self.__class__,
                    field.name,
                    oc,
                    f.name)
                coll = Connection.from_class(self.__class__).collection(jtname)
                key = ref_db_field_key(self.__class__.__name__, self.__class__)
                other_key = ref_db_field_key(oc.__name__, oc)
                for rel in coll.find({key: ObjectId(self._id)}):
                    other_id = rel[other_key]
                    item = oc.id(other_id).optional.exec()
                    if item is not None:
                        item._orm_delete(no_raise=True)
                coll.delete_many({key: ObjectId(self._id)})
            else:
                key = oc.definition.config.key_transformer(f)
                for o in oc.iterate(**{key: ObjectId(self._id)}).exec():
                    o._orm_delete(no_raise=True)

    setattr(self, '_is_deleted', True)


def _orm_restore(self: T) -> None:
    pass


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
    class_.linked = classmethod(linked)
    class_.exist = classmethod(exist)
    class_.iterate = classmethod(iterate)
    # protected methods
    class_._database_write = _database_write
    class_._orm_delete = _orm_delete
    class_._orm_restore = _orm_restore
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
