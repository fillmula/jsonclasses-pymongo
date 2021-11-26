from __future__ import annotations
from typing import Callable
from inflection import pluralize
from jsonclasses.keypath import camelize_key, underscore_key, identical_key


class PConf:

    def __init__(self: PConf,
                 cls: type,
                 collection_name: str | None,
                 camelize_db_keys: bool | None,
                 db_key_encoding_strategy: Callable[[str], str] | None,
                 db_key_decoding_strategy: Callable[[str], str] | None) -> None:
        self._cls = cls
        self._collection_name = (collection_name or pluralize(cls.__name__).lower())
        if db_key_encoding_strategy is None:
            self._db_key_encoding_strategy = camelize_key
        else:
            self._db_key_encoding_strategy = db_key_encoding_strategy
        if db_key_decoding_strategy is None:
            self._db_key_decoding_strategy = underscore_key
        else:
            self._db_key_decoding_strategy = db_key_decoding_strategy
        if camelize_db_keys == False:
            self._db_key_encoding_strategy = identical_key
            self._db_key_decoding_strategy = identical_key

    @property
    def collection_name(self: PConf) -> str:
        return self._collection_name

    @property
    def db_key_encoding_strategy(self: PConf) -> Callable[[str], str]:
        return self._db_key_encoding_strategy

    @property
    def db_key_decoding_strategy(self: PConf) -> Callable[[str], str]:
        return self._db_key_decoding_strategy

    def to_db_key(self: PConf, key: str) -> str:
        return self.db_key_encoding_strategy(key)

    def to_py_key(self: PConf, key: str) -> str:
        return self.db_key_decoding_strategy(key)
