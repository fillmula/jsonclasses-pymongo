from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='simple')
class SimpleRecord:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    desc: str
    age: int
    score: float
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='simple')
class SimpleORecord:
    id: str = types.readonly.str.primary.mongoid.required
    name: str | None
    desc: str | None
    age: int | None
    score: float | None
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
