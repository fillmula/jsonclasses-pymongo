from __future__ import annotations
from typing import Dict, Any, Type
from datetime import date, datetime
from jsonclasses import fields, Config
from jsonclasses.field_description import FieldType
from . import MongoObject

class Decoder():
  def decode_root(self, root: Dict[str, Any], cls: Type[MongoObject]) -> Type[MongoObject]:
    retval = cls()
    for field in fields(root):
      if field.field_name == 'id':
        setattr(retval, 'id', str(root['_id']))
      elif field.field_types.field_description.field_type == FieldType.DATE:
        datetime_value = root[field.db_field_name]
        setattr(retval, field.field_name, date.fromisoformat(datetime_value.isoformat()[:10]))
      else:
        setattr(retval, field.field_name, root[field.db_field_name])
    return retval
