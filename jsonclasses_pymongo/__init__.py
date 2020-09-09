from datetime import date, datetime
from dataclasses import dataclass, fields
from jsonclasses import jsonclass, types, PersistableJSONObject
from jsonclasses.types import Types
from jsonclasses.exceptions import ObjectNotFoundException
from pymongo.collection import Collection
from pymongo.database import Database
from bson.objectid import ObjectId
from inflection import pluralize
from .utils import default_db
from .encoder import Encoder
from .decoder import Decoder

@jsonclass
class MongoObject(PersistableJSONObject):
  '''Abstract and base class for jsonclasses_pymongo objects. You should define
  subclasses of this class to interact with mongoDB collections.
  '''

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

  def save(self, validate_all_fields=False, skip_validation=False):
    if not skip_validation:
      self.validate(all_fields=validate_all_fields)
      encoded = Encoder().encode_root(self)
    if getattr(self, 'id') is None:
      insertion_result = self.__class__.collection().insert_one(encoded)
      setattr(self, 'id', str(insertion_result.inserted_id))
    else:
      self.__class__.collection().update_one({ '_id': encoded['_id'] }, { '$set': encoded })
    return self

  @classmethod
  def find_by_id(self, id: str):
    mongo_object = self.collection().find_one({ '_id': ObjectId(id) })
    if mongo_object is None:
      raise ObjectNotFoundException(f'{self.__name__} record with id \'{id}\' is not found.')
    else:
      return Decoder().decode_root(mongo_object, self)

  @classmethod
  def find_one(self, *args, **kwargs):
    mongo_object = self.collection().find_one(*args, **kwargs)
    if mongo_object is None:
      raise ObjectNotFoundException(f'{self.__name__} record is not found.')
    else:
      return Decoder().decode_root(mongo_object, self)

  @classmethod
  def find_one_or_none(self, *args, **kwargs):
    try:
      return self.find_one(self, *args, **kwargs)
    except ObjectNotFoundException:
      return None

  @classmethod
  def find_one_or_new(self, *args, **kwargs):
    try:
      return self.find_one(self, *args, **kwargs)
    except ObjectNotFoundException:
      return self()

  @classmethod
  def find_one_or(self, callable, *args, **kwargs):
    try:
      return self.find_one(self, *args, **kwargs)
    except ObjectNotFoundException:
      return callable()

  @classmethod
  def find_one_or_create(self, input, *args, **kwargs):
    try:
      return self.find_one(self, *args, **kwargs)
    except ObjectNotFoundException:
      return self(**input)

  @classmethod
  def find(self, *args, **kwargs):
    cursor = self.collection().find(*args, **kwargs)
    retval = [doc for doc in cursor]
    return list(map(lambda mongo_object: Decoder().decode_root(mongo_object, self), retval))

  @classmethod
  def delete_by_id(self, id: str):
    deletion_result = self.collection().delete_one({ '_id': ObjectId(id) })
    if deletion_result.deleted_count < 1:
      raise ObjectNotFoundException(f'{self.__name__} with id \'{id}\' is not found.')
    else:
      return None
