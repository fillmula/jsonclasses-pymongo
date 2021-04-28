"""
This module contains `jsonclass`, the decorator for JSON Classes.
"""
from typing import Optional, Union, Callable, overload, cast
from jsonclasses.jsonclass_object import JSONClassObject
from .pymongo_object import PymongoObject
from .pymongofy import pymongofy
from .dbconf import DBConf


@overload
def pymongo(cls: type) -> type: ...


@overload
def pymongo(
    cls: None,
    collection_name: Optional[str] = None,
    camelize_db_keys: Optional[bool] = None,
) -> Callable[[type], type[PymongoObject]]: ...


@overload
def pymongo(
    cls: type,
    collection_name: Optional[str] = None,
    camelize_db_keys: Optional[bool] = None,
) -> type[PymongoObject]: ...


def pymongo(
    cls: Optional[type[JSONClassObject]] = None,
    collection_name: Optional[str] = None,
    camelize_db_keys: Optional[bool] = None,
) -> Union[Callable[[type], type[PymongoObject]], type[PymongoObject]]:
    """The pymongo object class decorator. To declare a jsonclass class, use
    this syntax:

        @pymongo
        @jsonclass
        class MyObject:
            my_field_one: str
            my_field_two: bool
    """
    if cls is not None:
        if not isinstance(cls, type):
            raise ValueError('@pymongo should be used to decorate a class.')
        conf = DBConf(cls, cls.definition.config,
                      collection_name, camelize_db_keys)
        cls.dbconf = conf
        return cast(type[PymongoObject], pymongofy(cls))
    else:
        def parametered_jsonclass(cls):
            return pymongo(
                cls,
                collection_name=collection_name,
                camelize_db_keys=camelize_db_keys)
        return parametered_jsonclass
