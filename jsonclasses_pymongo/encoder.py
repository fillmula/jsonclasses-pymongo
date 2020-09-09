from __future__ import annotations
from typing import Dict, Any
from datetime import date, datetime
from jsonclasses import fields, Config
from jsonclasses.field_description import FieldType
from bson.objectid import ObjectId
from . import MongoObject

class Encoder():
  def encode_root(self, root: MongoObject) -> Dict[str, Any]:
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
      else:
        retval[db_field_name] = field_value
    return retval
