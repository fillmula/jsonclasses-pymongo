from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='simple')
class SimpleAnimal:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    can_fly: bool
