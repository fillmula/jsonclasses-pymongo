from __future__ import annotations
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pymongo.collection import Collection

class WriteCommand:

  @classmethod
  def write_commands_to_db(cls, commands: List[WriteCommand]):
    for command in commands:
      command.write_to_db()

  def __init__(self, object: Dict[str, Any], collection: Collection, matcher: Optional[Dict[str, Any]] = None):
    self.object = object
    self.collection = collection
    if matcher is None:
      self.matcher = { '_id': object['_id'] }

  def write_to_db(self):
    self.collection.update_one(self.matcher, { '$set': self.object }, upsert=True)
