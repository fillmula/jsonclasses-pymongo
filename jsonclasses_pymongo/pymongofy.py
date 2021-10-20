from __future__ import annotations
from typing import TypeVar, Any, Union, cast
from re import search
from bson.objectid import ObjectId
from jsonclasses.jfield import JField
from pymongo.errors import DuplicateKeyError
from inflection import camelize, underscore
from pymongo.collection import Collection
from pymongo import ASCENDING
from jsonclasses.fdef import FStore, FType
from jsonclasses.excs import UniqueConstraintException
from jsonclasses.excs import DeletionDeniedException
from .pymongo_object import PymongoObject
from .query import BaseQuery, ExistQuery, IterateQuery, ListQuery, SingleQuery, IDQuery
from .encoder import Encoder
from .connection import Connection
from .utils import ref_db_field_key
from .coder import Coder


T = TypeVar('T', bound=PymongoObject)


def find(cls: type[T], *args, **kwargs: Any) -> ListQuery[T]:
    if len(args) > 0:
        return ListQuery(cls=cls, filter=args[0])
    else:
        return ListQuery(cls=cls, filter=kwargs)


def one(cls: type[T], *args, **kwargs: Any) -> SingleQuery[T]:
    if len(args) > 0:
        return SingleQuery(cls=cls, filter=args[0])
    else:
        return SingleQuery(cls=cls, filter=kwargs)


def pymongo_id(cls: type[T], id: str | ObjectId, *args, **kwargs: Any) -> IDQuery[T]:
    if len(args) > 0:
        return IDQuery(cls=cls, id=id, matcher=args[0])
    else:
        return IDQuery(cls=cls, id=id, matcher=kwargs)


def linked(cls: type[T], *args, **kwargs: Any) -> BaseQuery[T]:
    if len(args) > 0:
        return SingleQuery(cls=cls, filter=args[0])
    else:
        return SingleQuery(cls=cls, filter=kwargs)


def exist(cls: type[T], **kwargs: Any) -> ExistQuery[T]:
    return ExistQuery(cls=cls, filter=kwargs)


def iterate(cls: type[T], **kwargs: Any) -> IterateQuery[T]:
    return IterateQuery(cls=cls, filter=kwargs)


def _database_write(self: T) -> None:
    try:
        Encoder().encode_root(self).execute()
    except DuplicateKeyError as exception:
        result = search('index: (.+?) dup key', exception._message)
        assert result is not None
        index_key = result.group(1)
        single_key = True
        if index_key.endswith('_1'):
            db_key = index_key[:-2]
            single_key = True
        else:
            db_key = index_key
            single_key = False
        if single_key:
            pt_key = db_key
            if self.__class__.pconf.camelize_db_keys:
                pt_key = underscore(db_key)
            raise UniqueConstraintException(pt_key) from None
        else:
            results = []
            for field in self.__class__.cdef.fields:
                if field.fdef.cindex and db_key in field.fdef.cindex_names:
                    results.append(field.name)
            ek = self.__class__.cdef.jconf.key_encoding_strategy
            raise UniqueConstraintException([ek(r) for r in results], f'voilated unique compound index \'{index_key}\'')

def _orm_delete(self: T, no_raise: bool = False) -> None:
    # deny test
    for field in self.__class__.cdef.deny_fields:
        if field.fdef.fstore == FStore.LOCAL_KEY:
            key = self.__class__.cdef.jconf.ref_key_encoding_strategy(field)
            if hasattr(self, key) and getattr(self, key) is not None:
                if no_raise:
                    return
                else:
                    raise DeletionDeniedException()
        elif field.fdef.fstore == FStore.FOREIGN_KEY:
            if field.fdef.ftype == FType.LIST:
                oc = field.fdef.item_types.fdef.inst_cls
            else:
                oc = field.fdef.inst_cls
            f = cast(JField, field.foreign_field)
            if field.fdef.use_join_table:
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
                key = oc.cdef.jconf.ref_key_encoding_strategy(f)
                exist = oc.exist(**{key: ObjectId(self._id)}).exec()
                if exist:
                    if no_raise:
                        return
                    else:
                        raise DeletionDeniedException()

    collection = Connection.get_collection(self.__class__)
    collection.delete_one({'_id': ObjectId(self._id)})

    # delete chain - nullify
    for field in self.__class__.cdef.nullify_fields:
        if field.fdef.fstore == FStore.FOREIGN_KEY:
            if field.fdef.ftype == FType.LIST:
                oc = field.fdef.item_types.fdef.inst_cls
            else:
                oc = field.fdef.inst_cls
            f = cast(JField, field.foreign_field)
            if field.fdef.use_join_table:
                jtname = Coder().join_table_name(
                    self.__class__,
                    field.name,
                    oc,
                    f.name)
                coll = Connection.from_class(self.__class__).collection(jtname)
                key = ref_db_field_key(self.__class__.__name__, self.__class__)
                coll.delete_many({key: ObjectId(self._id)})
            else:
                key = oc.cdef.jconf.ref_key_encoding_strategy(f)
                for o in oc.iterate(**{key: ObjectId(self._id)}).exec():
                    setattr(o, f.name, None)
                    setattr(o, key, None)
                    o.save(skip_validation=True)

    # delete chain - cascade
    for field in self.__class__.cdef.cascade_fields:
        if field.fdef.ftype == FType.LIST:
            oc = field.fdef.item_types.fdef.inst_cls
        else:
            oc = field.fdef.inst_cls
        f = cast(JField, field.foreign_field)
        if field.fdef.fstore == FStore.LOCAL_KEY:
            key = self.__class__.cdef.jconf.ref_key_encoding_strategy(field)
            if getattr(self, key) is not None:
                item = oc.id(getattr(self, key)).optional.exec()
                if item is not None:
                    item._orm_delete(no_raise=True)
        elif field.fdef.fstore == FStore.FOREIGN_KEY:
            if field.fdef.use_join_table:
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
                key = oc.cdef.jconf.ref_key_encoding_strategy(f)
                for o in oc.iterate(**{key: ObjectId(self._id)}).exec():
                    o._orm_delete(no_raise=True)

    setattr(self, '_is_deleted', True)


def _orm_complete(self: T) -> None:
    this_pick = []
    mfields = self.modified_fields
    for field in self.__class__.cdef.fields:
        if field.fdef.fstore == FStore.EMBEDDED:
            if field.name not in self._partial_picks:
                this_pick.append(field.name)
        elif field.fdef.fstore == FStore.LOCAL_KEY:
            kr = self.__class__.cdef.jconf.ref_key_encoding_strategy
            ref_key = kr(field)
            if ref_key not in self._partial_picks:
                this_pick.append(ref_key)
    result = self.__class__.id(self._id, {'_pick': this_pick}).exec()
    for k in this_pick:
        if k not in mfields:
            setattr(self, k, getattr(result, k))
    setattr(self, '_is_partial', False)


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
    class_._orm_complete = _orm_complete
    connection = Connection.from_class(class_)
    if class_.cdef.jconf.abstract:
        return class_
    def callback(coll: Collection):
        info = coll.index_information()
        existing_index_keys = list(info.keys())
        compound_fields: dict[str, list[JField]] = {}
        compound_ufields: dict[str, list[JField]] = {}
        for field in class_.cdef.fields:
            fname = field.name
            if class_.pconf.camelize_db_keys:
                fname = camelize(field.name, False)
            index = field.fdef.index
            unique = field.fdef.unique
            required = field.fdef.required
            index_name = f'{fname}_1'
            cindex = field.fdef.cindex
            cindex_names = field.fdef.cindex_names
            cunique = field.fdef.cunique
            cunique_names = field.fdef.cunique_names
            # check single index
            if unique or index:
                coll.create_index(fname, name=index_name, unique=unique, sparse=not required)
                if index_name in existing_index_keys:
                    existing_index_keys.remove(index_name)
            else:
                if index_name in existing_index_keys:
                    coll.drop_index(index_name)
                    existing_index_keys.remove(index_name)
            # check compound index
            if cindex:
                for ciname in cindex_names:
                    if ciname not in compound_fields:
                        compound_fields[ciname] = []
                    if field.fdef.fstore == FStore.LOCAL_KEY:
                        res = field.fdef.cdef.jconf.ref_key_encoding_strategy
                        compound_fields[ciname].append(field)
                    else:
                        compound_fields[ciname].append(field)
            if cunique:
                for cuname in cunique_names:
                    if cuname not in compound_ufields:
                        compound_ufields[cuname] = []
                    if field.fdef.fstore == FStore.LOCAL_KEY:
                        res = field.fdef.cdef.jconf.ref_key_encoding_strategy
                        compound_ufields[cuname].append(field)
                    else:
                        compound_ufields[cuname].append(field)
        for index_name, fields in compound_fields.items():
            sparse: bool = False
            keys: list[tuple[str, Any]] = []
            for field in fields:
                if field.fdef.fstore == FStore.LOCAL_KEY:
                    res = field.fdef.cdef.jconf.ref_key_encoding_strategy
                    key = res(field)
                else:
                    key = field.name
                if class_.pconf.camelize_db_keys:
                    key = camelize(key, False)
                if not field.fdef.required:
                    sparse = True
                keys.append((key, ASCENDING))
            coll.create_index(keys, name=index_name, sparse=sparse)
            if index_name in existing_index_keys:
                existing_index_keys.remove(index_name)
        for index_name, fields in compound_ufields.items():
            sparse: bool = False
            keys: list[tuple[str, Any]] = []
            for field in fields:
                if field.fdef.fstore == FStore.LOCAL_KEY:
                    res = field.fdef.cdef.jconf.ref_key_encoding_strategy
                    key = res(field)
                else:
                    key = field.name
                if class_.pconf.camelize_db_keys:
                    key = camelize(key, False)
                if not field.fdef.required:
                    sparse = True
                keys.append((key, ASCENDING))
            coll.create_index(keys, name=index_name, unique=True, sparse=sparse)
            if index_name in existing_index_keys:
                existing_index_keys.remove(index_name)
        for left_key in existing_index_keys:
            if left_key != '_id_':
                coll.drop_index(left_key)
    connection.add_connected_callback(class_.pconf.collection_name, callback)
    return class_
