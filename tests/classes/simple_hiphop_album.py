from __future__ import annotations
from typing import Optional
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='simple')
class SimpleHiphopAlbum:
    id: str = types.readonly.str.primary.mongoid.required
    name: str | None
    release_year: int | None
    note: str | None
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
