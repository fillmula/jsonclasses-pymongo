from __future__ import annotations
from typing import Optional
from enum import Enum
from jsonclasses import jsonclass, types, jsonenum
from jsonclasses_pymongo import pymongo, BaseObject


@jsonenum
class Gender(Enum):
    MALE = 1
    FEMALE = 2


@pymongo
@jsonclass(class_graph='simple')
class SimpleSex(BaseObject):
    gender: Optional[Gender] = types.enum(Gender)
