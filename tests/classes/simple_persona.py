from __future__ import annotations
from typing import Optional
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='simple')
class SimplePersona(BaseObject):
    items: list[dict[str, int]] = types.nonnull.listof(dict[str, int])
