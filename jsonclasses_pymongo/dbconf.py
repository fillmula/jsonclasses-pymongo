from __future__ import annotations
from typing import Optional
from jsonclasses.config import Config
from inflection import pluralize


class DBConf:

    def __init__(self: DBConf,
                 cls: type,
                 config: Config,
                 collection_name: Optional[str],
                 camelize_db_keys: Optional[bool]) -> None:
        self._cls = cls
        self._config = config
        self._collection_name = (collection_name or
                                 pluralize(cls.__name__).lower())
        self._camelize_db_keys = (camelize_db_keys if camelize_db_keys is not
                                  None else True)

    @property
    def config(self: DBConf) -> Config:
        return self._config

    @property
    def collection_name(self: DBConf) -> str:
        return self._collection_name

    @property
    def camelize_db_keys(self: DBConf) -> bool:
        return self._camelize_db_keys
