from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedRecord:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    desc: str
    age: int
    score: float
    contents: list[LinkedContent] = types.nonnull.listof('LinkedContent').linkedby('record')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedContent:
    id: str = types.readonly.str.primary.mongoid.required
    title: str | None
    paper: str | None
    count: int | None
    record: LinkedRecord = types.objof('LinkedRecord').linkto.required
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
