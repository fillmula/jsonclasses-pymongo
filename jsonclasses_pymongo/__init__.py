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

@jsonclass
class MongoObject(PersistableJSONObject):
  '''Abstract and base class for jsonclasses_pymongo objects. You should define
  subclasses of this class to interact with mongoDB collections.
  '''

  @property
  def db(self) -> Database:
    return default_db()

  @property
  def collection(self) -> Collection:
    try:
      return self.__collection
    except AttributeError:
      self.__collection = self.db.get_collection(pluralize(self.__class__.__name__).lower())
      return self.__collection

  def __to_mongo_object(self):
    retval = {}
    for object_field in fields(self):
      name = object_field.name
      value = getattr(self, name)
      if name == 'id':
        if value is not None:
          retval['_id'] = ObjectId(value)
      elif type(value) is date:
        retval[name] = datetime.fromisoformat(value.isoformat())
      else:
        retval[name] = getattr(self, name)
    return retval

  def __from_mongo_object(self, mongo_object):
    object_fields = { f.name: f for f in fields(self) }
    for k, v in mongo_object.items():
      if k == '_id':
        k = 'id'
        v = str(v)
      object_field = object_fields[k]
      object_type = object_field.type
      print(object_type)
      if object_type is date and type(v) is datetime:
        v = date.fromisoformat(v.isoformat()[:10])
      setattr(self, k, v)
    return self

  def save(self, validate_all_fields=False, skip_validation=False):
    if not skip_validation:
      self.validate(all_fields=validate_all_fields)
    mongo_object = self.__to_mongo_object()
    if getattr(self, 'id') is None:
      insertion_result = self.collection.insert_one(mongo_object)
      setattr(self, 'id', str(insertion_result.inserted_id))
    else:
      self.collection.update_one({ '_id': mongo_object['_id'] }, { '$set': mongo_object })
    return self

  @classmethod
  def find_by_id(self, id: str):
    retval = self()
    mongo_object = retval.collection.find_one({ '_id': ObjectId(id) })
    if mongo_object is None:
      raise ObjectNotFoundException(f'{retval.__class__.__name__} with id \'{id}\' is not found.')
    else:
      return retval.__from_mongo_object(mongo_object)

  @classmethod
  def find_one(self, *args, **kwargs):
    retval = self()
    mongo_object = retval.collection.find_one(*args, **kwargs)
    if mongo_object is None:
      raise ObjectNotFoundException(f'{retval.__class__.__name__} is not found.')
    else:
      return retval.__from_mongo_object(mongo_object)

  @classmethod
  def find(self, *args, **kwargs):
    an_instance = self()
    cursor = an_instance.collection.find(*args, **kwargs)
    retval = [doc for doc in cursor]
    return list(map(lambda v: self().__from_mongo_object(v), retval))

  @classmethod
  def delete_by_id(self, id: str):
    an_instance = self()
    deletion_result = an_instance.collection.delete_one({ '_id': ObjectId(id) })
    if deletion_result.deleted_count < 1:
      raise ObjectNotFoundException(f'{an_instance.__class__.__name__} with id \'{id}\' is not found.')
    else:
      return None
