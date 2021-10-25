from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedOrder:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    user: LinkedBuyer = types.objof('LinkedBuyer').linkto
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedBuyer:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    orders: list[LinkedOrder] = types.listof('LinkedOrder').linkedby('user') \
                                     .cascade
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedCOrder:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    user: LinkedCBuyer = types.objof('LinkedCBuyer').linkto.cascade
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedCBuyer:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    orders: list[LinkedCOrder] = types.listof('LinkedCOrder').linkedby('user')\
                                      .cascade
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
