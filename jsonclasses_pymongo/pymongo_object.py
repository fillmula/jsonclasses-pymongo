"""This module defines `PymongoObject`, the protocol that @pymongo decorated
jsonclass object should confirm to.
"""
from __future__ import annotations
from typing import TypeVar, ClassVar, Any, Union
from bson.objectid import ObjectId
from jsonclasses.jsonclass_object import JSONClassObject
from .dbconf import DBConf
from .query import ListQuery, IDQuery, SingleQuery


T = TypeVar('T', bound='PymongoObject')


class PymongoObject(JSONClassObject):
    """The `PymongoObject` protocol defines methods that @pymongo decorated
    jsonclass object should confirm to.
    """

    dbconf: ClassVar[DBConf]
    """The configuration user passed to JSON class through the jsonclass
    decorator.
    """

    @classmethod
    def find(cls: type[T], **kwargs: Any) -> ListQuery[T]:
        ...

    @classmethod
    def one(cls: type[T], **kwargs: Any) -> SingleQuery[T]:
        ...

    @classmethod
    def id(cls: type[T], id: Union[str, ObjectId]) -> IDQuery[T]:
        ...

    @classmethod
    def delete_by_id(cls: type[T], id: Union[str, ObjectId]) -> None:
        ...

    @classmethod
    def delete_many(cls: type[T], *args, **kwargs) -> int:
        ...
