from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='linked')
class LinkedProfile(BaseObject):
    name: str
    user: LinkedUser = types.instanceof('LinkedUser').linkto


@pymongo
@jsonclass(class_graph='linked')
class LinkedUser(BaseObject):
    name: str
    profile: LinkedProfile = types.instanceof('LinkedProfile').linkedby('user')
