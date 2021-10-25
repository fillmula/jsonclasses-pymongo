from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedNote:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    notebook: LinkedNotebook = types.objof('LinkedNotebook').linkto
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required

@pymongo
@jsonclass(class_graph='linked')
class LinkedNotebook:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    notes: list[LinkedNote] = types.listof('LinkedNote').linkedby('notebook') \
                                   .deny
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedRNote:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    notebook: LinkedRNotebook = types.objof('LinkedRNotebook').linkto.deny
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedRNotebook:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    notes: list[LinkedRNote] = types.listof('LinkedRNote').linkedby('notebook')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
