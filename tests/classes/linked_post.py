from __future__ import annotations
from typing import TYPE_CHECKING
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject
if TYPE_CHECKING:
    from .linked_author import LinkedAuthor


@pymongo
@jsonclass(class_graph='linked')
class LinkedPost(BaseObject):
    title: str
    content: str
    author: LinkedAuthor = types.linkto.instanceof('LinkedAuthor')
