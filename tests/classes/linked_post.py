from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo
if TYPE_CHECKING:
    from .linked_author import LinkedAuthor


@pymongo
@jsonclass(class_graph='linked')
class LinkedPost:
    id: str = types.readonly.str.primary.mongoid.required
    title: str
    content: str
    author: LinkedAuthor = types.linkto.objof('LinkedAuthor')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
