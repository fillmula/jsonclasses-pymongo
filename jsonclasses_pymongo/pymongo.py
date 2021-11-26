"""
This module contains `jsonclass`, the decorator for JSON Classes.
"""
from typing import Union, Callable, TypeVar, overload, cast
from jsonclasses.jobject import JObject
from .pobject import PObject
from .pymongofy import pymongofy
from .pconf import PConf


T = TypeVar('T', bound=type[JObject])

@overload
def pymongo(cls: T) -> T | type[PObject]: ...


@overload
def pymongo(
    cls: None,
    collection_name: str | None = None,
    camelize_db_keys: bool | None = None,
    db_key_encoding_strategy: Callable[[str], str] | None = None,
    db_key_decoding_strategy: Callable[[str], str] | None = None,
) -> Callable[[T], T | type[PObject]]: ...


@overload
def pymongo(
    cls: T,
    collection_name: str | None = None,
    camelize_db_keys: bool | None = None,
    db_key_encoding_strategy: Callable[[str], str] | None = None,
    db_key_decoding_strategy: Callable[[str], str] | None = None,
) -> T | type[PObject]: ...


def pymongo(
    cls: T | None = None,
    collection_name: str | None = None,
    camelize_db_keys: bool | None = None,
    db_key_encoding_strategy: Callable[[str], str] | None = None,
    db_key_decoding_strategy: Callable[[str], str] | None = None,
) -> Union[Callable[[T], T | type[PObject]], T | type[PObject]]:
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
        conf = PConf(cls,
                     collection_name,
                     camelize_db_keys,
                     db_key_encoding_strategy,
                     db_key_decoding_strategy)
        cls.pconf = conf
        return cast(type[PObject], pymongofy(cls))
    else:
        def parametered_jsonclass(cls):
            return pymongo(
                cls,
                collection_name=collection_name,
                camelize_db_keys=camelize_db_keys)
        return parametered_jsonclass
