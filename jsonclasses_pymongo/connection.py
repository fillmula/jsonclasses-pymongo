from __future__ import annotations
from typing import Callable, ClassVar, Optional, TYPE_CHECKING, TypeVar
from os import getcwd, path
from pymongo.mongo_client import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from inflection import parameterize, camelize
if TYPE_CHECKING:
    from .pymongo_object import PymongoObject
    T = TypeVar('T', bound=PymongoObject, covariant=False)


ConnectedCallback = Callable[[Collection], None]


class Connection:
    _graph_map: dict[str, Connection] = {}
    _initialized_map: dict[str, bool] = {}

    def __new__(cls: type[Connection], graph_name: str) -> Connection:
        if not cls._graph_map.get(graph_name):
            cls._graph_map[graph_name] = super(Connection, cls).__new__(cls)
        return cls._graph_map[graph_name]

    def __init__(self: Connection, graph_name: str) -> None:
        if self.__class__._initialized_map.get(graph_name):
            return
        self._graph_name: str = graph_name
        self._url: Optional[str] = None
        self._client: Optional[MongoClient] = None
        self._database: Optional[Database] = None
        self._collections: dict[str, Collection] = {}
        self._connection_callbacks: dict[str, ConnectedCallback] = {}
        self._connected: bool = False
        self.__class__._initialized_map[graph_name] = True
        return None

    @property
    def graph_name(self: Connection) -> str:
        return self._graph_name

    @property
    def url(self: Connection) -> str:
        if self._url:
            return self._url
        return self._generate_default_url()

    def set_url(self: Connection, url: str) -> None:
        self._url = url

    def _generate_default_url(self: Connection) -> str:
        base = 'mongodb://localhost:27017/'
        cwd = getcwd()
        proj = camelize(parameterize(path.basename(cwd))).lower()
        self._url = base + proj
        return self._url

    @property
    def client(self: Connection) -> MongoClient:
        if self._client is not None:
            return self._client
        self.connect()
        return self._client

    @property
    def database(self: Connection) -> Database:
        if self._database is not None:
            return self._database
        self.connect()
        return self._database

    def connect(self: Connection) -> None:
        self._client = MongoClient(self.url)
        self._database = self._client.get_database()
        self._connected = True
        for name, callback in self._connection_callbacks.items():
            self._call_callback(name, callback)

    def disconnect(self: Connection) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._database = None
            self._collections = {}
            self._connected = False

    @property
    def connected(self: Collection) -> bool:
        return self._connected

    def collection(self: Connection, name: str) -> Collection:
        if self._collections.get(name):
            return self._collections[name]
        coll = self.database.get_collection(name)
        self._collections[name] = coll
        return coll

    def add_connected_callback(self: Connection,
                               name: str,
                               callback: ConnectedCallback) -> None:
        self._connection_callbacks[name] = callback
        if self._client:
            self._call_callback(name, callback)

    def _call_callback(self: Connection,
                       name: str,
                       callback: ConnectedCallback) -> None:
        callback(self.collection(name))

    def collection_from(self: Connection,
                        cls: type[T]) -> Collection:
        coll_name = cls.dbconf.collection_name
        return self.collection(coll_name)

    default: ClassVar[Connection]

    @classmethod
    def get_collection(cls: type[Connection],
                       pmcls: type[T]) -> Collection:
        graph = pmcls.definition.config.class_graph.name
        connection = Connection(graph)
        return connection.collection_from(pmcls)

    @classmethod
    def from_class(cls: type[Connection],
                   pmcls: type[T]) -> Connection:
        return Connection(pmcls.definition.config.class_graph.name)


Connection.default = Connection('default')
