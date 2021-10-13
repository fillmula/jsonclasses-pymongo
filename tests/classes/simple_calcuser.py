from __future__ import annotations
from enum import Enum
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='simple')
class SimpleCalcUser:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    first_name: str = types.str.getter(lambda u: u.name.split(" ")[0])
    last_name: str = types.str.getter(types.this.fval('name').split(' ').at(1))
    base_score: float
    score: float = types.float.getter(types.this.fval('base_score').mul(2)).negative
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
