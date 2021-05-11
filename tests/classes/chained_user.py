from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='chained')
class ChainedProfile(BaseObject):
    name: str
    user: ChainedUser = types.instanceof('ChainedUser').linkto


@pymongo
@jsonclass(class_graph='chained')
class ChainedUser(BaseObject):
    name: str
    profile: ChainedProfile = types.instanceof('ChainedProfile').linkedby('user')
    address: ChainedAddress = types.instanceof('ChainedAddress').linkedby('user')


@pymongo
@jsonclass(class_graph='chained')
class ChainedAddress(BaseObject):
    name: str
    user: ChainedUser = types.instanceof('ChainedUser').linkto
