from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedCompany:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    owners: list[LinkedOwner] = types.listof('LinkedOwner') \
                                     .linkedthru('companies').cascade
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedOwner:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    companies: list[LinkedCompany] = types.listof('LinkedCompany') \
                                          .linkedthru('owners').deny
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
