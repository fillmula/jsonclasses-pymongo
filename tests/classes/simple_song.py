from __future__ import annotations
from jsonclasses import jsonclass
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='simple')
class SimpleSong(BaseObject):
    name: str
    year: int
    artist: str
