from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class MusicProduct:
    id: str = types.readonly.str.primary.mongoid.required
    music_users: list[MusicProduct] = types.listof('MusicUser').linkedby('music_products')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class MusicUser:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    music_products: list[MusicUser] = types.listof(MusicProduct).linkto.required
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
