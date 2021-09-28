from __future__ import annotations
from enum import Enum
from datetime import datetime
from jsonclasses import jsonclass, jsonenum, types
from jsonclasses_pymongo import pymongo


@jsonenum(class_graph='simple')
class Gender(Enum):
    MALE = 1
    FEMALE = 2


@pymongo
@jsonclass(class_graph='simple')
class SimpleArtist:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    gender: Gender
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
