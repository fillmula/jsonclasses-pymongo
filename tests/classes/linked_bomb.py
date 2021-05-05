from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='linked')
class LinkedBomb(BaseObject):
    name: str
    soldiers: list[LinkedSoldier] = types.listof('LinkedSoldier') \
                                         .linkedthru('bombs').cascade


@pymongo
@jsonclass(class_graph='linked')
class LinkedSoldier(BaseObject):
    name: str
    bombs: list[LinkedBomb] = types.listof('LinkedBomb') \
                                   .linkedthru('soldiers').cascade
