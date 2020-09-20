from jsonclasses import types
from jsonclasses_pymongo import MongoObject


class Template(MongoObject):
    name: str = types.str.trim.required
