from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedProfile:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    user: LinkedUser = types.objof('LinkedUser').linkto
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedUser:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    profile: LinkedProfile = types.objof('LinkedProfile').linkedby('user')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedDProfile:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    user: LinkedCUser = types.objof('LinkedCUser').linkto.deny
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedCUser:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    profile: LinkedDProfile = types.objof('LinkedDProfile') \
                                   .linkedby('user').cascade
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedCProfile:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    user: LinkedDUser = types.objof('LinkedDUser').linkto.cascade
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedDUser:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    profile: LinkedCProfile = types.objof('LinkedCProfile') \
                                   .linkedby('user').deny
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
