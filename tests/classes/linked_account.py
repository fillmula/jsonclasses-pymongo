from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedAccount():
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    balance: LinkedBalance = types.instanceof('LinkedBalance').linkto.cascade
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedBalance():
    name: str
    account: LinkedAccount = types.instanceof('LinkedAccount') \
                                  .linkedby('balance').cascade
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
