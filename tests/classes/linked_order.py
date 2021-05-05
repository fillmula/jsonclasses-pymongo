from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='linked')
class LinkedOrder(BaseObject):
    name: str
    user: LinkedBuyer = types.instanceof('LinkedBuyer').linkto


@pymongo
@jsonclass(class_graph='linked')
class LinkedBuyer(BaseObject):
    name: str
    orders: list[LinkedOrder] = types.listof('LinkedOrder').linkedby('user') \
                                     .cascade


@pymongo
@jsonclass(class_graph='linked')
class LinkedCOrder(BaseObject):
    name: str
    user: LinkedCBuyer = types.instanceof('LinkedCBuyer').linkto.cascade


@pymongo
@jsonclass(class_graph='linked')
class LinkedCBuyer(BaseObject):
    name: str
    orders: list[LinkedCOrder] = types.listof('LinkedCOrder').linkedby('user')\
                                      .cascade
