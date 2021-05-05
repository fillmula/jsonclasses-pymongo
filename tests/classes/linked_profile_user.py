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


@pymongo
@jsonclass(class_graph='linked')
class LinkedDProfile(BaseObject):
    name: str
    user: LinkedCUser = types.instanceof('LinkedCUser').linkto.deny


@pymongo
@jsonclass(class_graph='linked')
class LinkedCUser(BaseObject):
    name: str
    profile: LinkedDProfile = types.instanceof('LinkedDProfile') \
                                   .linkedby('user').cascade


@pymongo
@jsonclass(class_graph='linked')
class LinkedCProfile(BaseObject):
    name: str
    user: LinkedDUser = types.instanceof('LinkedDUser').linkto.cascade


@pymongo
@jsonclass(class_graph='linked')
class LinkedDUser(BaseObject):
    name: str
    profile: LinkedCProfile = types.instanceof('LinkedCProfile') \
                                   .linkedby('user').deny
