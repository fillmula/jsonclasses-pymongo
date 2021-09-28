from __future__ import annotations
from datetime import date
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo
from datetime import datetime


@pymongo
@jsonclass(class_graph='simple')
class SimpleDate():
    id: str = types.readonly.str.primary.mongoid.required
    represents: date
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
