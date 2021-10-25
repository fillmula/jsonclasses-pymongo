from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='chained')
class ChainedProfile:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    user: ChainedUser = types.objof('ChainedUser').linkto
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='chained')
class ChainedUser:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    profile: ChainedProfile = types.objof('ChainedProfile').linkedby('user')
    address: ChainedAddress = types.objof('ChainedAddress').linkedby('user')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='chained')
class ChainedAddress:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    user: ChainedUser = types.objof('ChainedUser').linkto
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
