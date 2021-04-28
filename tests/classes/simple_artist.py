from __future__ import annotations
from enum import Enum
from jsonclasses import jsonclass, jsonenum
from jsonclasses_pymongo import pymongo, BaseObject


@jsonenum(class_graph='simple')
class Gender(Enum):
    MALE = 1
    FEMALE = 2


@pymongo
@jsonclass(class_graph='simple')
class SimpleArtist(BaseObject):
    name: str
    gender: Gender
