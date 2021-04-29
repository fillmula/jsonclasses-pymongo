from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo(collection_name='simplepeople')
@jsonclass(class_graph='simple')
class SimplePerson(BaseObject):
    name: str = types.str.unique.required
