from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='simple')
class SimpleScore:
    name: str
    score: float
