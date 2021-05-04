from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='linked')
class LinkedCourse(BaseObject):
    name: str
    students: list[LinkedStudent] = types.listof('LinkedStudent') \
                                         .linkedthru('courses')


@pymongo
@jsonclass(class_graph='linked')
class LinkedStudent(BaseObject):
    name: str
    courses: list[LinkedCourse] = types.listof('LinkedCourse') \
                                       .linkedthru('students')
