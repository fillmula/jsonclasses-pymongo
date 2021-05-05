from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='linked')
class LinkedAccount(BaseObject):
    name: str
    balance: LinkedBalance = types.instanceof('LinkedBalance').linkto.cascade


@pymongo
@jsonclass(class_graph='linked')
class LinkedBalance(BaseObject):
    name: str
    account: LinkedAccount = types.instanceof('LinkedAccount') \
                                  .linkedby('balance').cascade
