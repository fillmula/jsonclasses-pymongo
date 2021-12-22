from __future__ import annotations
from os import name
from typing import Annotated
from datetime import datetime
from jsonclasses import jsonclass, types, linkedby, linkto
from jsonclasses.typing import linkedthru
from jsonclasses_pymongo import pymongo

@pymongo
@jsonclass(class_graph='preload')
class LJPLUser:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    articles: Annotated[list[LJPLArticle], linkedthru('authors')]
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='preload')
class LJPLArticle:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    authors: Annotated[list[LJPLUser], linkedthru('articles')]
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required

# @pymongo
# @jsonclass(class_graph='preload')
# class LLPLArticle:
#     id: str = types.readonly.str.primary.mongoid.required
#     name: str
#     # lauthors: Annotated[LLPLUser, linkto]
#     authors: Annotated[LLPLUser, linkto]
#     created_at: datetime = types.readonly.datetime.tscreated.required
#     updated_at: datetime = types.readonly.datetime.tsupdated.required

# @pymongo
# @jsonclass(class_graph='preload')
# class LLPLUser:
#     id: str = types.readonly.str.primary.mongoid.required
#     name: str
#     articles: Annotated[list[LLPLArticle], linkedby('authors')]
#     # larticles: Annotated[LLPLArticle,linkto]
#     created_at: datetime = types.readonly.datetime.tscreated.required
#     updated_at: datetime = types.readonly.datetime.tsupdated.required