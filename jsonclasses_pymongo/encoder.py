from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from jsonclasses import fields, Config, FieldType, FieldStorage, collection_argument_type_to_types
from inflection import camelize
from bson.objectid import ObjectId

class Encoder():

  def encode_item(self, item_to_encode, item_types) -> Any:
    if item_to_encode is None:
      return None
    if item_types.field_description.field_type == FieldType.DATE:
      return datetime.fromisoformat(item_to_encode.isoformat())
    elif item_types.field_description.field_type == FieldType.LIST:
      return self.encode_list(item_to_encode, item_types.field_description.field_type.list_item_types)
    elif item_types.field_description.field_type == FieldType.DICT:
      return self.encode_dict(item_to_encode, item_types.field_description.field_type.dict_item_types)
    else:
      return item_to_encode

  def encode_list(self, list_to_encode, item_types) -> List[Any]:
    if list_to_encode is None:
      return None
    types = collection_argument_type_to_types(item_types)
    retval = []
    for item in list_to_encode:
      retval.append(self.encode_item(item, types))
    return retval

  def encode_dict(self, dict_to_encode, item_types) -> Dict[str, Any]:
    if dict_to_encode is None:
      return None
    types = collection_argument_type_to_types(item_types)
    retval = {}
    for (key, item) in dict_to_encode.items():
      retval[key] = self.encode_item(item, types)
    return retval

  def encode_shape(self, shape_to_encode, shape_types) -> Dict[str, Any]:
    if shape_to_encode is None:
      return None
    retval = {}
    for (key, value) in shape_to_encode.items():
      retval[key] = self.encode_item(value, collection_argument_type_to_types(shape_types[key]))
    return retval

  def encode_root(
    self,
    root: 'MongoObject',
    parent: 'MongoObject' = None,
    parent_linkedby: Optional[str] = None,
    save: bool = True
  ) -> Dict[str, Any]:
    retval = {}
    config: Config = root.__class__.config
    for field in fields(root):
      field_name = field.field_name
      db_field_name = field.db_field_name
      field_value = getattr(root, field_name)
      if field_name == 'id' and field_value is not None:
        retval['_id'] = ObjectId(field_value)
      elif type(field_value) is date:
        retval[db_field_name] = datetime.fromisoformat(field_value.isoformat())
      elif field.field_types.field_description.field_type == FieldType.LIST:
        if field.field_types.field_description.field_storage == FieldStorage.FOREIGN_KEY:
          if field_value is not None:
            for item in field_value:
              self.encode_root(item, parent=root, parent_linkedby=field.field_types.field_description.foreign_key)
        elif field.field_types.field_description.field_storage == FieldStorage.LOCAL_KEY:
          local_key_field_name = field_name + '_ids'
          local_key_db_field_name = camelize(local_key_field_name, False) if config.camelize_db_keys else local_key_field_name
          if field_value is None:
            retval[local_key_db_field_name] = []
          else:
            ids = []
            for item in field_value:
              ids.append(ObjectId(self.encode_root(item)['_id']))
            retval[local_key_db_field_name] = ids
        else:
          retval[db_field_name] = self.encode_list(field_value, field.field_types.field_description.list_item_types)
      elif field.field_types.field_description.field_type == FieldType.DICT:
        retval[db_field_name] = self.encode_dict(field_value, field.field_types.field_description.dict_item_types)
      elif field.field_types.field_description.field_type == FieldType.SHAPE:
        retval[db_field_name] = self.encode_shape(field_value, field.field_types.field_description.shape_types)
      elif field.field_types.field_description.field_type == FieldType.INSTANCE:
        if field.field_types.field_description.field_storage == FieldStorage.FOREIGN_KEY:
          if getattr(root, field_name) is not None:
            self.encode_root(getattr(root, field_name), parent=root, parent_linkedby=field.field_types.field_description.foreign_key)
        elif field.field_types.field_description.field_storage == FieldStorage.LOCAL_KEY:
          if getattr(root, field_name) is not None:
            local_key_field_name = field_name + '_id'
            local_key_db_field_name = camelize(local_key_field_name, False) if config.camelize_db_keys else local_key_field_name
            retval[local_key_db_field_name] = ObjectId(getattr(root, field_name).id)
            self.encode_root(getattr(root, field_name))
          elif parent_linkedby == field.field_name:
            local_key_field_name = field_name + '_id'
            local_key_db_field_name = camelize(local_key_field_name, False) if config.camelize_db_keys else local_key_field_name
            retval[local_key_db_field_name] = ObjectId(parent.id)
        else:
          encoded = self.encode_root(getattr(root, field_name), save=False)
          retval[db_field_name] = encoded
      else:
        retval[db_field_name] = field_value
    if save:
      root.__class__.collection().update_one({ '_id': retval['_id'] }, { '$set': retval }, upsert=True)
    return retval
