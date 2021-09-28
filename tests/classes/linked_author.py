from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo
if TYPE_CHECKING:
    from .linked_post import LinkedPost



@pymongo
@jsonclass(class_graph='linked')
class LinkedAuthor:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    posts: list[LinkedPost] = types.nonnull.listof('LinkedPost') \
                                   .linkedby('author')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
