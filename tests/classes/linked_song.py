from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedSong:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    singers: list[LinkedSinger] = types.nonnull.listof('LinkedSinger').linkto
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedSinger:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    songs: list[LinkedSong] = types.nonnull.listof('LinkedSong').linkedby('singers')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
