from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class LinkedCourse:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    score: int | None = 1
    students: list[LinkedStudent] = types.nonnull.listof('LinkedStudent') \
                                         .linkedthru('courses')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class LinkedStudent:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    courses: list[LinkedCourse] = types.nonnull.listof('LinkedCourse') \
                                       .linkedthru('students')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
