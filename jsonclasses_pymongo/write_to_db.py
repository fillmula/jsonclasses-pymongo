from __future__ import annotations
from typing import List, Dict, Any, Optional, TypeVar, Tuple, Type, TYPE_CHECKING

if TYPE_CHECKING:
  from .mongo_object import MongoObject
  T = TypeVar('T', bound=MongoObject)

def write_to_db(commands: List[Tuple(Dict[str, Any], Type[T])]):
  for command in commands:
    data, Kls = command
    Kls.collection().update_one({ '_id': data['_id'] }, { '$set': data }, upsert=True)
