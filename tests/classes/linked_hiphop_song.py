from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class HiphopSinger:
    id: str = types.readonly.str.primary.mongoid.required
    hiphop_songs: list[HiphopSong] = types.listof('HiphopSong').linkedby('hiphop_singers')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class HiphopSong:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    hiphop_singers: list[HiphopSinger] = types.listof(HiphopSinger).linkto.required
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
