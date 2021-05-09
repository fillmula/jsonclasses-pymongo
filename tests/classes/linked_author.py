from __future__ import annotations
from typing import TYPE_CHECKING
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject
if TYPE_CHECKING:
    from .linked_post import LinkedPost


@pymongo
@jsonclass(class_graph='linked')
class LinkedAuthor(BaseObject):
    name: str
    posts: list[LinkedPost] = types.nonnull.listof('LinkedPost') \
                                   .linkedby('author')
