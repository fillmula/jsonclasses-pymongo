from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class PopSinger:
    id: str = types.readonly.str.primary.mongoid.required
    pop_song: PopSong = types.objof('PopSong').linkedby('pop_singer')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class PopSong:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    pop_singer: PopSinger = types.objof(PopSinger).linkto.required
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
