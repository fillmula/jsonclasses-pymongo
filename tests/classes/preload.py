from __future__ import annotations
from typing import Annotated
from datetime import datetime
from jsonclasses import jsonclass, types, linkedby, linkto
from jsonclasses_pymongo import pymongo

@pymongo
@jsonclass(class_graph='preload')
class PLUser:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    articles: Annotated[list[PLArticle], linkedby('author')]
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='preload')
class PLArticle:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    author: Annotated[PLUser, linkto]
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
