"""This module defines `PymongoObject`, the protocol that @pymongo decorated
jsonclass object should confirm to.
"""
from __future__ import annotations
from typing import TypeVar, ClassVar, Any, Union, TYPE_CHECKING
from bson.objectid import ObjectId
from jsonclasses.jobject import JObject
if TYPE_CHECKING:
    from .pconf import PConf
    from .query import (BaseQuery, ListQuery, IDQuery, SingleQuery, ExistQuery,
                        IterateQuery)


T = TypeVar('T', bound='PymongoObject')


class PymongoObject(JObject):
    """The `PymongoObject` protocol defines methods that @pymongo decorated
    jsonclass object should confirm to.
    """

    pconf: ClassVar[PConf]
    """The configuration user passed to JSON class through the jsonclass
    decorator.
    """

    @classmethod
    def find(cls: type[T], *args, **kwargs: Any) -> ListQuery[T]:
        ...

    @classmethod
    def one(cls: type[T], *args, **kwargs: Any) -> SingleQuery[T]:
        ...

    @classmethod
    def id(cls: type[T], id: str | ObjectId, *args, **kwargs: Any) -> IDQuery[T]:
        ...

    @classmethod
    def linked(cls: type[T], *args, **kwargs: Any) -> BaseQuery[T]:
        ...

    @classmethod
    def exist(cls: type[T], **kwargs: Any) -> ExistQuery[T]:
        ...

    @classmethod
    def iterate(cls: type[T], **kwargs: Any) -> IterateQuery[T]:
        ...

    def _orm_delete(self: T, no_raise: bool = False) -> None:
        ...

    def _orm_restore(self: T) -> None:
        ...
