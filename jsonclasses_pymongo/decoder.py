from __future__ import annotations
from typing import List, Dict, Any, Type, Optional
from datetime import date, datetime
from jsonclasses import fields, Types, Config, Field, FieldType, FieldStorage, collection_argument_type_to_types
from .utils import ref_field_key, ref_field_keys, ref_db_field_key, ref_db_field_keys

class Decoder():

  def is_id_field(self, field: Field) -> bool:
    return field.field_name == 'id'

  def is_instance_field(self, field: Field) -> bool:
    return field.field_types.field_description.field_type == FieldType.INSTANCE

  def is_list_field(self, field: Field) -> bool:
    return field.field_types.field_description.field_type == FieldType.LIST

  def is_local_key_storage(self, field: Field) -> bool:
    return field.field_types.field_description.field_storage == FieldStorage.LOCAL_KEY

  def is_foreign_key_storage(self, field: Field) -> bool:
    return field.field_types.field_description.field_storage == FieldStorage.FOREIGN_KEY

  def is_local_key_reference_field(self, field: Field) -> bool:
    return self.is_instance_field(field) and self.is_local_key_storage(field)

  def is_local_keys_reference_field(self, field: Field) -> bool:
    return self.is_list_field(field) and self.is_local_key_storage(field)

  def decode_list(self, value: List[Any], cls: Type['MongoObject'], types: Types) -> List[Any]:
    if value is None:
      return None
    if types.field_description.field_storage == FieldStorage.FOREIGN_KEY:
      return None
    elif types.field_description.field_storage == FieldStorage.LOCAL_KEY:
      return [str(value) for item in value]
    else:
      item_types = types.field_description.list_item_types
      return [self.decode_item(value=item, cls=cls, types=item_types) for item in value]

  def decode_dict(self, value: Dict[str, Any], cls: Type['MongoObject'], types: Types) -> Dict[str, Any]:
    if value is None:
      return None
    if types.field_description.field_storage == FieldStorage.FOREIGN_KEY:
      return None
    if types.field_description.field_storage == FieldStorage.LOCAL_KEY:
      return { k: str(v) for k, v in value.items() }
    else:
      item_types = types.field_description.dict_item_types
      return { k: self.decode_item(value=v, cls=cls, types=item_types) for k, v in value.items() }

  def decode_shape(self, value: Dict[str, Any], cls: Type['MongoObject'], types: Types) -> Dict[str, Any]:
    shape_types = types.field_description.shape_types
    retval = {}
    for k, item_types in shape_types.items():
      retval[k] = self.decode_item(value=value[k], cls=cls, types=item_types)
    return retval

  def decode_instance(self, value: Dict[str, Any], cls: Type['MongoObject'], types: Types) -> Any:
    if types.field_description.field_storage == FieldStorage.FOREIGN_KEY:
      return None
    elif types.field_description.field_storage == FieldStorage.LOCAL_KEY:
      return str(value)
    else:
      return self.decode_root(
        root=value,
        cls=collection_argument_type_to_types(types, graph_sibling=cls)
      )

  def decode_item(self, value: Any, cls: Type['MongoObject'], types: Types) -> Any:
    if value is None:
      return value
    if types.field_description.field_type == FieldType.DATE:
      return date.fromisoformat(value.isoformat()[:10])
    elif types.field_description.field_type == FieldType.LIST:
      return self.decode_list(value=value, cls=cls, types=types)
    elif types.field_description.field_type == FieldType.DICT:
      return self.decode_dict(value=value, cls=cls, types=types)
    elif types.field_description.field_type == FieldType.SHAPE:
      return self.decode_shape(value=value, cls=cls, types=types)
    elif types.field_description.field_type == FieldType.INSTANCE:
      return self.decode_instance(value=value, cls=cls, types=types)
    else:
      return value

  def decode_root(self, root: Optional[Dict[str, Any]], cls: Type['MongoObject']) -> Optional[Type['MongoObject']]:
    if root is None:
      return None
    dest = cls()
    for field in fields(cls):
      if self.is_id_field(field):
        setattr(dest, 'id', str(root.get('_id')))
      elif self.is_foreign_key_storage(field):
        pass
      elif self.is_local_key_reference_field(field):
        setattr(
          dest,
          ref_field_key(field.field_name),
          self.decode_item(
            value=root.get(ref_db_field_key(field.db_field_name, cls=cls)),
            types=field.field_types,
            cls=cls
          )
        )
      elif self.is_local_keys_reference_field(field):
        setattr(
          dest,
          ref_field_keys(field.field_name),
          self.decode_item(
            value=root.get(ref_db_field_keys(field.db_field_name, cls=cls)),
            types=field.field_types,
            cls=cls
          )
        )
      else:
        setattr(
          dest,
          field.field_name,
          self.decode_item(
            value=root.get(field.db_field_name),
            types=field.field_types,
            cls=cls
          )
        )
    return dest
