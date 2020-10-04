from __future__ import annotations
from typing import (ClassVar, Optional, Sequence, TypeVar, Dict, Any, Union,
                    Type, cast)
from jsonclasses import (jsonclass, types, JSONObject,
                         fields, FieldType, FieldStorage,
                         resolve_types, ObjectNotFoundException)
from datetime import datetime
from pymongo.collection import Collection
from pymongo.database import Database
from bson.objectid import ObjectId
from inflection import pluralize
from .utils import default_db, ref_field_key, ref_field_keys, ref_db_field_key
from .encoder import Encoder
from .decoder import Decoder
from .write_command import WriteCommand

T = TypeVar('T', bound='MongoObject')


@jsonclass
class MongoObject(JSONObject):
    """Abstract and base class for JSON Classes Pymongo objects. You should
    define subclasses of this class to interact with mongoDB collections.
    """

    id: str = types.str.readonly.default(lambda: str(ObjectId())).required
    """The id string of the object. This field is readonly. A user must not set
    an object's id through web request bodies.
    """

    created_at: datetime = (types.datetime.readonly.default(datetime.now)
                            .required)
    """This field records when this object is created. The value of this field
    is managed internally thus cannot be updated externally with web request
    bodies.
    """

    updated_at: datetime = (types.datetime.readonly.default(datetime.now)
                            .required)
    """This field records when this object is last updated. The value of this
    field is managed internally thus cannot be updated externally with web
    request bodies.
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

    def _include(self, key_path: str):
        field = next(field for field in fields(self)
                     if field.field_name == key_path)
        fd = field.field_types.field_description
        if (fd.field_type == FieldType.INSTANCE and
                fd.field_storage == FieldStorage.LOCAL_KEY):
            ref_id = getattr(self, ref_field_key(field.field_name))
            if ref_id is not None:
                Cls = cast(Type[MongoObject], resolve_types(
                        fd.instance_types,
                        graph_sibling=self.__class__
                    ).field_description.instance_types)
                setattr(self, field.field_name, Cls.find_by_id(ref_id))
        elif (fd.field_type == FieldType.INSTANCE and
                fd.field_storage == FieldStorage.FOREIGN_KEY):
            foreign_key_name = ref_db_field_key(cast(str, fd.foreign_key),
                                                self.__class__)
            Cls = cast(Type[MongoObject], resolve_types(
                fd.instance_types,
                graph_sibling=self.__class__).field_description.instance_types)
            setattr(self, field.field_name, Cls.find_one(
                {foreign_key_name: ObjectId(self.id)}))
        elif (fd.field_type == FieldType.LIST and
                fd.field_storage == FieldStorage.LOCAL_KEY):
            ref_ids = getattr(self, ref_field_keys(field.field_name))
            if ref_ids is not None:
                item_types = resolve_types(
                    fd.list_item_types, self.__class__)
                Cls = cast(Type[MongoObject], resolve_types(
                    item_types.field_description.instance_types,
                    self.__class__))
                setattr(self, field.field_name, Cls.find(
                    {'_id': {'$in': [ObjectId(id) for id in ref_ids]}}))
        elif (fd.field_type == FieldType.LIST and
                fd.field_storage == FieldStorage.FOREIGN_KEY):
            if fd.use_join_table:
                decoder = Decoder()
                self_class = self.__class__
                other_class = decoder.list_instance_type(
                    field, self.__class__)
                join_table_name = decoder.join_table_name(
                    self_class,
                    field.field_name,
                    other_class,
                    cast(str, fd.foreign_key)
                )
                jt_collection = self_class.db().get_collection(join_table_name)
                cursor = jt_collection.aggregate([
                    {
                        '$match': {
                            ref_db_field_key(self_class.__name__, self_class):
                                ObjectId(self.id)
                        }
                    },
                    {
                        '$lookup': {
                            'from': other_class.collection().name,
                            'localField': ref_db_field_key(
                                    other_class.__name__,
                                    other_class),
                            'foreignField': '_id',
                            'as': 'result'
                        }
                    },
                    {
                        '$project': {
                            'result': {'$arrayElemAt': ['$result', 0]}
                        }
                    },
                    {
                        '$replaceRoot': {
                            'newRoot': '$result'
                        }
                    }
                ])
                results = [decoder.decode_root(
                    doc, other_class) for doc in cursor]
                setattr(self, field.field_name, results)
            else:
                foreign_key_name = ref_db_field_key(
                    cast(str, fd.foreign_key), self.__class__)
                item_types = resolve_types(
                    fd.list_item_types, self.__class__)
                Cls = cast(Type[MongoObject], resolve_types(
                    item_types.field_description.instance_types,
                    self.__class__).field_description.instance_types)
                setattr(self, field.field_name, Cls.find(
                    {foreign_key_name: ObjectId(self.id)}))
        else:
            pass

    def include(self: T, *args: str) -> T:
        for arg in args:
            self._include(arg)
        return self

    def save(
        self: T,
        validate_all_fields: bool = False,
        skip_validation: bool = False
    ) -> T:
        if not skip_validation:
            self.validate(all_fields=validate_all_fields)
        commands = Encoder().encode_root(self)
        WriteCommand.write_commands_to_db(commands)
        return self

    def add_to(self: T,
               list_field_name: str,
               *args: Union[MongoObject, ObjectId, str]) -> T:
        field = next(field for field in fields(self)
                     if field.field_name == list_field_name)
        decoder = Decoder()
        if not decoder.is_join_table_field(field):
            return self
        write_commands = []
        for arg in args:
            object_id = arg.id if isinstance(arg, MongoObject) else arg
            if type(object_id) is str:
                object_id = ObjectId(object_id)
            other_class = decoder.list_instance_type(
                field, self.__class__)
            join_table_name = decoder.join_table_name(
                self.__class__,
                field.field_name,
                other_class,
                cast(str, field.field_types.field_description.foreign_key)
            )
            join_table_collection = self.__class__.db().get_collection(
                                        join_table_name)
            this_field_name = ref_db_field_key(
                self.__class__.__name__, self.__class__)
            other_field_name = ref_db_field_key(
                other_class.__name__, other_class)
            write_commands.append(WriteCommand({
                this_field_name: ObjectId(self.id),
                other_field_name: object_id
            }, join_table_collection, {
                this_field_name: ObjectId(self.id),
                other_field_name: object_id
            }))
        WriteCommand.write_commands_to_db(write_commands)
        return self

    def remove_from(self: T,
                    list_field_name: str,
                    *args: Union[MongoObject, ObjectId]) -> T:
        field = next(field for field in fields(self)
                     if field.field_name == list_field_name)
        decoder = Decoder()
        if not decoder.is_join_table_field(field):
            return self
        write_commands = []
        for arg in args:
            object_id = arg.id if isinstance(arg, MongoObject) else arg
            if type(object_id) is str:
                object_id = ObjectId(object_id)
            other_class = decoder.list_instance_type(
                field, self.__class__)
            join_table_name = decoder.join_table_name(
                self.__class__,
                field.field_name,
                other_class,
                cast(str, field.field_types.field_description.foreign_key)
            )
            join_table_collection = self.__class__.db().get_collection(
                                            join_table_name)
            this_field_name = ref_db_field_key(
                self.__class__.__name__, self.__class__)
            other_field_name = ref_db_field_key(
                other_class.__name__, other_class)
            write_commands.append(WriteCommand({
                this_field_name: ObjectId(self.id),
                other_field_name: object_id
            }, join_table_collection, {
                this_field_name: ObjectId(self.id),
                other_field_name: object_id
            }))
        WriteCommand.remove_commands_from_db(write_commands)
        return self

    @classmethod
    def find_by_id(self: Type[T], id: str) -> T:
        mongo_object = self.collection().find_one({'_id': ObjectId(id)})
        if mongo_object is None:
            raise ObjectNotFoundException(
                f'{self.__name__} record with id \'{id}\' is not found.')
        else:
            return Decoder().decode_root(mongo_object, self)

    @classmethod
    def find_one(self: Type[T], *args, **kwargs) -> T:
        mongo_object = self.collection().find_one(*args, **kwargs)
        if mongo_object is None:
            raise ObjectNotFoundException(
                f'{self.__name__} record is not found.')
        else:
            return Decoder().decode_root(mongo_object, self)

    @classmethod
    def find_one_or_none(self: Type[T], *args, **kwargs) -> Optional[T]:
        try:
            return self.find_one(self, *args, **kwargs)
        except ObjectNotFoundException:
            return None

    @classmethod
    def find_one_or_new(self: Type[T], *args, **kwargs) -> T:
        try:
            return self.find_one(self, *args, **kwargs)
        except ObjectNotFoundException:
            return self()

    @classmethod
    def find_one_or(self: Type[T], callable, *args, **kwargs) -> Optional[T]:
        try:
            return self.find_one(self, *args, **kwargs)
        except ObjectNotFoundException:
            return callable()

    @classmethod
    def find_one_or_create(self: Type[T],
                           input: Dict[str, Any],
                           *args,
                           **kwargs) -> T:
        try:
            return self.find_one(self, *args, **kwargs)
        except ObjectNotFoundException:
            return self(**input)

    @classmethod
    def find(self: Type[T], *args, **kwargs) -> Sequence[T]:
        cursor = self.collection().find(*args, **kwargs)
        retval = [doc for doc in cursor]
        return list(
            map(lambda mongo_object: Decoder().decode_root(mongo_object, self),
                retval))

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
