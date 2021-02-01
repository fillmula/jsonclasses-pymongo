from __future__ import annotations
from typing import ClassVar, TypeVar, Any, Union, Type, overload
from jsonclasses import jsonclass, ORMObject, ObjectNotFoundException
from pymongo.collection import Collection
from pymongo.database import Database
from bson.objectid import ObjectId
from inflection import pluralize
from .utils import default_db
from .encoder import Encoder
from .query import IDQuery, ListQuery


@jsonclass
class BaseMongoObject(ORMObject):
    """BaseMongoObject is a `JSONObject` subclass for defining your business
    models with MongoDB. A `BaseMongoObject` class represents a MongoDB
    collection. This class doesn't define standard primary key field and
    timestamp fields. If you want to use standard fields, consider using
    `MongoObject`.
    """

    _collection: ClassVar[Collection]

    @classmethod
    def db(cls) -> Database:
        return default_db()

    @classmethod
    def collection(cls) -> Collection:
        try:
            return cls._collection
        except AttributeError:
            cls._collection = cls.db().get_collection(
                                    pluralize(cls.__name__).lower())
            return cls._collection

    # def _include(self, key_path: str):
    #     field = next(field for field in fields(self)
    #                  if field.field_name == key_path)
    #     fd = field.field_types.field_description
    #     if (fd.field_type == FieldType.INSTANCE and
    #             fd.field_storage == FieldStorage.LOCAL_KEY):
    #         ref_id = getattr(self, ref_field_key(field.field_name))
    #         if ref_id is not None:
    #             Cls = cast(Type[MongoObject], resolve_types(
    #                     fd.instance_types,
    #                     graph_sibling=self.__class__
    #                 ).field_description.instance_types)
    #             setattr(self, field.field_name, Cls.find_by_id(ref_id))
    #     elif (fd.field_type == FieldType.INSTANCE and
    #             fd.field_storage == FieldStorage.FOREIGN_KEY):
    #         foreign_key_name = ref_db_field_key(cast(str, fd.foreign_key),
    #                                             self.__class__)
    #         Cls = cast(Type[MongoObject], resolve_types(
    #             fd.instance_types,
    #             graph_sibling=self.__class__).field_description.instance_types)
    #         setattr(self, field.field_name, Cls.find_one(
    #             {foreign_key_name: ObjectId(self.id)}))
    #     elif (fd.field_type == FieldType.LIST and
    #             fd.field_storage == FieldStorage.LOCAL_KEY):
    #         ref_ids = getattr(self, ref_field_keys(field.field_name))
    #         if ref_ids is not None:
    #             item_types = resolve_types(
    #                 fd.list_item_types, self.__class__)
    #             Cls = cast(Type[MongoObject], resolve_types(
    #                 item_types.field_description.instance_types,
    #                 self.__class__))
    #             setattr(self, field.field_name, Cls.find_many(
    #                 {'_id': {'$in': [ObjectId(id) for id in ref_ids]}}))
    #     elif (fd.field_type == FieldType.LIST and
    #             fd.field_storage == FieldStorage.FOREIGN_KEY):
    #         if fd.use_join_table:
    #             decoder = Decoder()
    #             self_class = self.__class__
    #             other_class = decoder.list_instance_type(
    #                 field, self.__class__)
    #             join_table_name = decoder.join_table_name(
    #                 self_class,
    #                 field.field_name,
    #                 other_class,
    #                 cast(str, fd.foreign_key)
    #             )
    #             jt_collection = self_class.db().get_collection(join_table_name)
    #             cursor = jt_collection.aggregate([
    #                 {
    #                     '$match': {
    #                         ref_db_field_key(self_class.__name__, self_class):
    #                             ObjectId(self.id)
    #                     }
    #                 },
    #                 {
    #                     '$lookup': {
    #                         'from': other_class.collection().name,
    #                         'localField': ref_db_field_key(
    #                                 other_class.__name__,
    #                                 other_class),
    #                         'foreignField': '_id',
    #                         'as': 'result'
    #                     }
    #                 },
    #                 {
    #                     '$project': {
    #                         'result': {'$arrayElemAt': ['$result', 0]}
    #                     }
    #                 },
    #                 {
    #                     '$replaceRoot': {
    #                         'newRoot': '$result'
    #                     }
    #                 }
    #             ])
    #             results = [decoder.decode_root(
    #                 doc, other_class) for doc in cursor]
    #             setattr(self, field.field_name, results)
    #         else:
    #             foreign_key_name = ref_db_field_key(
    #                 cast(str, fd.foreign_key), self.__class__)
    #             item_types = resolve_types(
    #                 fd.list_item_types, self.__class__)
    #             Cls = cast(Type[MongoObject], resolve_types(
    #                 item_types.field_description.instance_types,
    #                 self.__class__).field_description.instance_types)
    #             setattr(self, field.field_name, Cls.find_many(
    #                 {foreign_key_name: ObjectId(self.id)}))
    #     else:
    #         pass

    # def include(self: T, *args: str) -> T:
    #     for arg in args:
    #         self._include(arg)
    #     return self

    def save(
        self: T,
        validate_all_fields: bool = False,
        skip_validation: bool = False
    ) -> T:
        if not skip_validation:
            self.validate(all_fields=validate_all_fields)
        Encoder().encode_root(self).execute()
        setattr(self, '_is_new', False)
        setattr(self, '_is_modified', False)
        setattr(self, '_modified_fields', set())
        return self

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

    @overload
    @classmethod
    def find(cls: Type[T], id: Union[str, ObjectId]) -> IDQuery: ...

    @overload
    @classmethod
    def find(cls: Type[T], query: dict[str, Any]) -> ListQuery: ...

    @overload
    @classmethod
    def find(cls: Type[T]) -> ListQuery: ...

    @classmethod
    def find(cls: Type[T], *args, **kwargs) -> Union[IDQuery, ListQuery]:
        id = kwargs.get('id') or args[0] if len(args) > 0 else None
        query = kwargs.get('query') or args[0] if len(args) > 0 else None
        arg = id if id is not None else query
        if isinstance(arg, str) or isinstance(arg, ObjectId):
            return IDQuery(cls=cls, id=arg)
        return ListQuery(cls=cls, filter=arg)


T = TypeVar('T', bound=BaseMongoObject)
