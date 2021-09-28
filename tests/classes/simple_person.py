from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo
from datetime import datetime


@pymongo(collection_name='simplepeople')
@jsonclass(class_graph='simple')
class SimplePerson():
    id: str = types.readonly.str.primary.mongoid.required
    name: str = types.str.unique.required
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
