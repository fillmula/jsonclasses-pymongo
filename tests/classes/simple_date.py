from __future__ import annotations
from datetime import date
from jsonclasses import jsonclass
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='simple')
class SimpleDate(BaseObject):
    represents: date
