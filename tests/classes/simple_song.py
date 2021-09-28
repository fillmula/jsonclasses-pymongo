from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo
from datetime import datetime


@pymongo
@jsonclass(class_graph='simple')
class SimpleSong():
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    year: int
    artist: str
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
