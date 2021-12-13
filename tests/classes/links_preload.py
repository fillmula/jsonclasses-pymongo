from __future__ import annotations
from os import name
from typing import Annotated
from datetime import datetime
from jsonclasses import jsonclass, types, linkedby, linkto
from jsonclasses.typing import linkedthru
from jsonclasses_pymongo import pymongo

@pymongo
@jsonclass(class_graph='preload')
class LPLUser:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    articles: Annotated[list[LPLArticle], linkedthru('authors')]
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='preload')
class LPLArticle:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    authors: Annotated[list[LPLUser], linkedthru('articles')]
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
