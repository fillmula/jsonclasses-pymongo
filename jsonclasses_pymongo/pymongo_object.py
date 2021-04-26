"""This module defines `PymongoObject`, the protocol that @pymongo decorated
jsonclass object should confirm to.
"""
from __future__ import annotations
from typing import TypeVar, ClassVar
from jsonclasses.jsonclass_object import JSONClassObject
from .dbconf import DBConf
from .query import (ListQuery, IDQuery, SingleQuery, OptionalIDQuery,
                    OptionalSingleQuery)


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
    def find(cls: type[T], ) -> ListQuery[T]:
        ...

    @classmethod
    def one(cls: type[T], ) -> SingleQuery[T]:
        ...
