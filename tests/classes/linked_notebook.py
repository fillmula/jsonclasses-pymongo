from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='linked')
class LinkedNote(BaseObject):
    name: str
    notebook: LinkedNotebook = types.instanceof('LinkedNotebook').linkto


@pymongo
@jsonclass(class_graph='linked')
class LinkedNotebook(BaseObject):
    name: str
    notes: list[LinkedNote] = types.listof('LinkedNote').linkedby('notebook') \
                                   .deny


@pymongo
@jsonclass(class_graph='linked')
class LinkedRNote(BaseObject):
    name: str
    notebook: LinkedRNotebook = types.instanceof('LinkedRNotebook').linkto.deny


@pymongo
@jsonclass(class_graph='linked')
class LinkedRNotebook(BaseObject):
    name: str
    notes: list[LinkedRNote] = types.listof('LinkedRNote').linkedby('notebook')
