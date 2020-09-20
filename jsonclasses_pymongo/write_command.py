from __future__ import annotations
from typing import List, Dict, Any, Optional
from pymongo.collection import Collection


class WriteCommand:

    @classmethod
    def write_commands_to_db(cls, commands: List[WriteCommand]):
        for command in commands:
            command.write_to_db()

    @classmethod
    def remove_commands_from_db(cls, commands: List[WriteCommand]):
        for command in commands:
            command.delete_from_db()

    def __init__(self,
                 object: Dict[str, Any],
                 collection: Collection,
                 matcher: Optional[Dict[str, Any]] = None):
        self.object = object
        self.collection = collection
        self.matcher = matcher if matcher is not None else {
            '_id': object['_id']}

    def write_to_db(self):
        self.collection.update_one(
            self.matcher, {'$set': self.object}, upsert=True)

    def delete_from_db(self):
        self.collection.delete_one(self.matcher)

    def __repr__(self) -> str:
        return f'<WriteCommand(\'{self.collection.name}\') {self.object}>'

    def __eq__(self, other) -> bool:
        if type(other) is not WriteCommand:
            return False
        other_command: WriteCommand = other
        return (self.object == other_command.object and
                self.collection == other_command.collection and
                self.matcher == other_command.matcher)
