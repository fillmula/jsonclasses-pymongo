from __future__ import annotations
from typing import Annotated
from jsonclasses import jsonclass, types, linkto, linkedby, linkedthru
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedStrIdArticle:
    id: str = types.str.primary.required
    val: str
    author: Annotated[LinkedStrIdAuthor, linkto]


@pymongo
@jsonclass(class_graph='linked')
class LinkedStrIdAuthor:
    id: str = types.str.primary.required
    val: str
    articles: Annotated[list[LinkedStrIdArticle], linkedby('author')]


@pymongo
@jsonclass(class_graph='linked')
class LinkedStrIdSong:
    id: str = types.str.primary.required
    singers: Annotated[list[LinkedStrIdSinger], linkto]


@pymongo
@jsonclass(class_graph='linked')
class LinkedStrIdSinger:
    id: str = types.str.primary.required
    songs: Annotated[list[LinkedStrIdSong], linkedby('singers')]


@pymongo
@jsonclass(class_graph='linked')
class LinkedStrIdProduct:
    id: str = types.str.primary.required
    users: Annotated[list[LinkedStrIdUser], linkedthru('products')]


@pymongo
@jsonclass(class_graph='linked')
class LinkedStrIdUser:
    id: str = types.str.primary.required
    products: Annotated[list[LinkedStrIdProduct], linkedthru('users')]
