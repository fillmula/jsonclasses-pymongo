from __future__ import annotations
from typing import Optional
from enum import Enum
from datetime import datetime
from jsonclasses import jsonclass, types, jsonenum
from jsonclasses_pymongo import pymongo


@jsonenum
class Gender(Enum):
    MALE = 1
    FEMALE = 2


@pymongo
@jsonclass(class_graph='simple')
class SimpleSex:
    id: str = types.readonly.str.primary.mongoid.required
    gender: Optional[Gender] = types.enum(Gender)
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
