from __future__ import annotations
from typing import List, Dict, Any, Optional, TypeVar, Tuple, Type, TYPE_CHECKING
from datetime import date, datetime
from jsonclasses import fields, Types, Config, FieldType, FieldStorage, collection_argument_type_to_types
from inflection import camelize
from bson.objectid import ObjectId
from .coder import Coder
from .utils import ref_field_key, ref_field_keys, ref_db_field_key, ref_db_field_keys

if TYPE_CHECKING:
  from .mongo_object import MongoObject
  T = TypeVar('T', bound=MongoObject)

class Encoder(Coder):

  def encode_list(
    self,
    value: Optional[List[Any]],
    types: Any,
    parent: Optional[T] = None,
    parent_linkedby: Optional[str] = None
  ) -> Tuple[List[Any], List[Tuple(Dict[str, Any], Type[T])]]:
    if value is None:
      return None
    types = collection_argument_type_to_types(types)
    dest = []
    write_commands = []
    for item in value:
      new_value, commands = self.encode_item(
        value=item, types=types, parent=parent, parent_linkedby=parent_linkedby
      )
      dest.append(new_value)
      write_commands.extend(commands)
    return dest, write_commands

  def encode_dict(
    self,
    value: Optional[Dict[str, Any]],
    types: Any,
    parent: Optional[T] = None,
    parent_linkedby: Optional[str] = None
  ) -> Tuple[Dict[str, Any], List[Tuple(Dict[str, Any], Type[T])]]:
    if value is None:
      return None, []
    types = collection_argument_type_to_types(types)
    dest = {}
    write_commands = []
    for (key, item) in value.items():
      new_value, commands = self.encode_item(
        value=item, types=types, parent=parent, parent_linkedby=parent_linkedby
      )
      dest[key] = new_value
      write_commands.extend(commands)
    return dest, write_commands

  def encode_shape(
    self,
    value: Optional[Dict[str, Any]],
    types: Dict[str, Any],
    parent: Optional[T] = None,
    parent_linkedby: Optional[str] = None
  ) -> Tuple[Dict[str, Any], List[Tuple(Dict[str, Any], Type[T])]]:
    if value is None:
      return None, []
    dest = {}
    write_commands = []
    for (key, item) in value.items():
      new_value, commands = self.encode_item(
        value=item,
        types=collection_argument_type_to_types(types[key]),
        parent=parent,
        parent_linkedby=parent_linkedby
      )
      dest[key] = new_value
      write_commands.extend(commands)
    return dest, write_commands

  def encode_instance(
    self,
    value: Optional[T],
    parent: Optional[T] = None,
    parent_linkedby: Optional[str] = None
  ) -> Tuple[Dict[str, Any], List[Tuple(Dict[str, Any], Type[T])]]:
    if value is None:
      return None, []
    dest = {}
    write_commands = []
    for field in fields(value):
      if self.is_id_field(field):
        dest['_id'] = ObjectId(value.get('id'))
      elif self.is_foreign_key_reference_field(field):
        # not assign, but get write commands
        value_at_field = getattr(value, field.field_name)
        if value_at_field is not None:
          _encoded, commands = self.encode_instance(
            value=value_at_field,
            parent=value,
            parent_linkedby=field.field_types.field_description.foreign_key
          )
          write_commands.extend(commands)
      elif self.is_foreign_keys_reference_field(field):
        # not assign, but get a list of write commands
        value_at_field = getattr(value, field.field_name)
        if value_at_field is not None:
          _encoded, commands = self.encode_list(
            value=value_at_field,
            types=field.field_types,
            parent=value,
            parent_linkedby=field.field_types.field_description.foreign_key
          )
          write_commands.extend(commands)
      elif self.is_local_key_reference_field(field):
        # assign a local key, and get write commands
        value_at_field = getattr(value, field.field_name)
        if value_at_field is not None:
          setattr(value, ref_field_key(field.field_name), value_at_field.id)
          encoded, commands = self.encode_instance(
            value=value_at_field,
            parent=value,
            parent_linkedby=field.field_types.field_description.foreign_key
          )
          dest[ref_db_field_key(field.field_name, value.__class__)] = encoded['_id']
          write_commands.extend(commands)
        elif parent_linkedby == field.field_name:
          setattr(value, ref_field_key(field.field_name), parent.id)
          dest[ref_field_key(field.field_name)] = ObjectId(parent.id)
      elif self.is_local_keys_reference_field(field):
        # assign a list of local keys, and get write commands
        value_at_field = getattr(value, field.field_name)
        if value_at_field is not None:
          setattr(value, ref_field_keys(field.field_name), [v.id for v in value_at_field])
          encoded, commands = self.encode_list(
            value=value_at_field,
            types=field.field_types,
            parent=value,
            parent_linkedby=field.field_name
          )
          dest[ref_db_field_keys(field.field_name, value.__class__)] = [v['_id'] for v in encoded]
          write_commands.extend(commands)
      else:
        value, new_write_commands = self.encode_item(
          value=getattr(value, field.field_name),
          types=field.field_types,
          parent=parent,
          parent_linkedby=parent_linkedby
        )
        dest[field.db_field_name] = value
        write_commands.extend(new_write_commands)
    write_commands.append((dest, value.__class__))
    return dest, write_commands

  def encode_item(
    self,
    value: Any,
    types: Types,
    parent: Optional[T] = None,
    parent_linkedby: Optional[str] = None
  ) -> Tuple[Any, List[Tuple(Dict[str, Any], Type[T])]]:
    if value is None:
      return (value, [])
    if types.field_description.field_type == FieldType.DATE:
      return datetime.fromisoformat(value.isoformat()), []
    elif types.field_description.field_type == FieldType.LIST:
      return self.encode_list(value=value, types=types, parent=parent, parent_linkedby=parent_linkedby)
    elif types.field_description.field_type == FieldType.DICT:
      return self.encode_dict(value=value, types=types, parent=parent, parent_linkedby=parent_linkedby)
    elif types.field_description.field_type == FieldType.SHAPE:
      return self.encode_shape(value=value, types=types, parent=parent, parent_linkedby=parent_linkedby)
    elif types.field_description.field_type == FieldType.INSTANCE:
      return self.encode_instance(value=value, parent=parent, parent_linkedby=parent_linkedby)
    else:
      return value, []

  # return save commands
  def encode_root(self, root: T) -> Tuple[Dict[str, Any], List[Tuple(Dict[str, Any], Type[T])]]:
    return self.encode_instance(value=root, parent=None, parent_linkedby=None)

      # elif field.field_types.field_description.field_type == FieldType.LIST:
      #   if field.field_types.field_description.field_storage == FieldStorage.FOREIGN_KEY:
      #     if field_value is not None:
      #       for item in field_value:
      #         self.encode_root(item, parent=root, parent_linkedby=field.field_types.field_description.foreign_key)
      #   elif field.field_types.field_description.field_storage == FieldStorage.LOCAL_KEY:
      #     local_key_field_name = field_name + '_ids'
      #     local_key_db_field_name = camelize(local_key_field_name, False) if config.camelize_db_keys else local_key_field_name
      #     if field_value is None:
      #       retval[local_key_db_field_name] = []
      #     else:
      #       ids = []
      #       for item in field_value:
      #         ids.append(ObjectId(self.encode_root(item)['_id']))
      #       retval[local_key_db_field_name] = ids
      #   else:
      #     retval[db_field_name] = self.encode_list(field_value, field.field_types.field_description.list_item_types)

      #root.__class__.collection().update_one({ '_id': retval['_id'] }, { '$set': retval }, upsert=True)
