from __future__ import annotations
from typing import Optional, Sequence, TypeVar, Dict, Any, Type
from jsonclasses import jsonclass, types, PersistableJSONObject, Types
from jsonclasses import ObjectNotFoundException, fields, FieldType, FieldStorage
from jsonclasses import collection_argument_type_to_types
from pymongo.collection import Collection
from pymongo.database import Database
from bson.objectid import ObjectId
from inflection import pluralize
from .utils import default_db, ref_field_key, ref_field_keys, ref_db_field_key
from .encoder import Encoder
from .decoder import Decoder
from.write_to_db import write_to_db

T = TypeVar('T', bound='MongoObject')

@jsonclass
class MongoObject(PersistableJSONObject):
  '''Abstract and base class for jsonclasses_pymongo objects. You should define
  subclasses of this class to interact with mongoDB collections.
  '''

  id: str = types.str.readonly.default(lambda: str(ObjectId())).required

  @classmethod
  def db(self) -> Database:
    return default_db()

  @classmethod
  def collection(self) -> Collection:
    try:
      return self.__collection
    except AttributeError:
      self.__collection = self.db().get_collection(pluralize(self.__name__).lower())
      return self.__collection

  def _include(self, key_path: str):
    field = next(field for field in fields(self) if field.field_name == key_path)
    fd = field.field_types.field_description
    if fd.field_type == FieldType.INSTANCE and fd.field_storage == FieldStorage.LOCAL_KEY:
      ref_id = getattr(self, ref_field_key(field.field_name))
      if ref_id is not None:
        Cls = collection_argument_type_to_types(fd.instance_types, graph_sibling=self.__class__).field_description.instance_types
        setattr(self, field.field_name, Cls.find_by_id(ref_id))
    elif fd.field_type == FieldType.INSTANCE and fd.field_storage == FieldStorage.FOREIGN_KEY:
      foreign_key_name = ref_db_field_key(fd.foreign_key, self.__class__)
      Cls = collection_argument_type_to_types(fd.instance_types, graph_sibling=self.__class__).field_description.instance_types
      setattr(self, field.field_name, Cls.find_one({ foreign_key_name: ObjectId(self.id) }))
    elif fd.field_type == FieldType.LIST and fd.field_storage == FieldStorage.LOCAL_KEY:
      ref_ids = getattr(self, ref_field_keys(field.field_name))
      if ref_ids is not None:
        item_types = collection_argument_type_to_types(fd.list_item_types, self.__class__)
        Cls = collection_argument_type_to_types(item_types.field_description.instance_types, self.__class__)
        setattr(self, field.field_name, Cls.find({ '_id': { '$in': [ObjectId(id) for id in ref_ids] }}))
    elif fd.field_type == FieldType.LIST and fd.field_storage == FieldStorage.FOREIGN_KEY:
      foreign_key_name = ref_db_field_key(fd.foreign_key, self.__class__)
      item_types = collection_argument_type_to_types(fd.list_item_types, self.__class__)
      Cls = collection_argument_type_to_types(item_types.field_description.instance_types, self.__class__).field_description.instance_types
      setattr(self, field.field_name, Cls.find({ foreign_key_name: ObjectId(self.id) }))
    else:
      pass

  def include(self: T, *args: str) -> T:
    for arg in args:
      self._include(arg)
    return self

  def save(
    self: T,
    validate_all_fields: bool = False,
    skip_validation :bool = False
  ) -> T:
    if not skip_validation:
      self.validate(all_fields=validate_all_fields)
    commands = Encoder().encode_root(self)
    write_to_db(commands)
    return self

  @classmethod
  def find_by_id(self: Type[T], id: str) -> T:
    mongo_object = self.collection().find_one({ '_id': ObjectId(id) })
    if mongo_object is None:
      raise ObjectNotFoundException(f'{self.__name__} record with id \'{id}\' is not found.')
    else:
      return Decoder().decode_root(mongo_object, self)

  @classmethod
  def find_one(self: Type[T], *args, **kwargs) -> T:
    mongo_object = self.collection().find_one(*args, **kwargs)
    if mongo_object is None:
      raise ObjectNotFoundException(f'{self.__name__} record is not found.')
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
  def find_one_or_create(self: Type[T], input: Dict[str, Any], *args, **kwargs) -> T:
    try:
      return self.find_one(self, *args, **kwargs)
    except ObjectNotFoundException:
      return self(**input)

  @classmethod
  def find(self: Type[T], *args, **kwargs) -> Sequence[T]:
    cursor = self.collection().find(*args, **kwargs)
    retval = [doc for doc in cursor]
    return list(map(lambda mongo_object: Decoder().decode_root(mongo_object, self), retval))

  @classmethod
  def delete_by_id(self, id: str) -> None:
    deletion_result = self.collection().delete_one({ '_id': ObjectId(id) })
    if deletion_result.deleted_count < 1:
      raise ObjectNotFoundException(f'{self.__name__} with id \'{id}\' is not found.')
    else:
      return None

  @classmethod
  def delete(self, *args, **kwargs) -> int:
    if len(args) == 0:
      args = [{}]
    return self.collection().delete_many(*args, **kwargs).deleted_count
