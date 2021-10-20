from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedAlbum:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    artists: list[LinkedArtist] = types.nonnull.listof('LinkedArtist').linkedthru('albums')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedArtist:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    albums: list[LinkedAlbum] = types.nonnull.listof('LinkedAlbum').linkedthru('artists')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
