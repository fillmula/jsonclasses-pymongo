"""This module defines the MongoDB connector class."""
from __future__ import annotations
from typing import Callable, Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from .exceptions import DatabaseNotConnectedException

ConnectionCallback = Callable[[Collection], None]


class _Connector:
    _instance: _Connector = None
    _initialized: bool = False

    def __new__(cls: type[_Connector]) -> _Connector:
        if cls._instance is None:
            cls._instance = super(_Connector, cls).__new__(cls)
        return cls._instance

    def __init__(self: _Connector) -> None:
        if self.__class__._initialized:
            return
        self._connection_callbacks: dict[str, ConnectionCallback] = {}
        self._collections: dict[str, Collection] = {}
        self._url: Optional[str] = None
        self._client: Optional[MongoClient] = None
        self._database: Optional[Database] = None
        self.__class__._initialized = True

    def connect(self: _Connector, url: str) -> None:
        """Connect to the database at url.
        """
        self._url = url
        self._client = MongoClient(self._url)
        self._database = self._client.get_database()
        for name, callback in self._connection_callbacks.items():
            self._call_callback(name, callback)

    def disconnect(self: _Connector) -> None:
        self._client.close()
        self._url = None
        self._client = None
        self._database = None
        self._collections = {}

    def _call_callback(self: _Connector,
                       name: str,
                       callback: ConnectionCallback) -> None:
        callback(self.collection(name))

    def collection(self: _Connector, name: str) -> Collection:
        """Return a cached collection by its name. If there isn't a collection
        with the name, a new collection object is created and cached.
        """
        if not self._client:
            raise DatabaseNotConnectedException("Cannot get database "
                                                "collection with name"
                                                f" '{name}'. Database is not "
                                                "yet connected.")
        if self._collections.get(name) is None:
            self._collections[name] = self._database.get_collection(name)
        return self._collections[name]

    def _add_callback(self: _Connector,
                      name: str,
                      callback: ConnectionCallback) -> None:
        self._connection_callbacks[name] = callback
        if self._client:
            self._call_callback(name, callback)


connector = _Connector()
