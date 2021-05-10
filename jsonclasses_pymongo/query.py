"""This module contains id query."""
from __future__ import annotations
from typing import (Iterator, Union, TypeVar, Generator, Optional, Any,
                    Generic, overload, cast)
from bson import ObjectId
from jsonclasses.exceptions import ObjectNotFoundException
from inflection import camelize
from pymongo.cursor import Cursor
from .decoder import Decoder
from .connection import Connection
from .pymongo_object import PymongoObject
T = TypeVar('T', bound=PymongoObject)



class IDQuery(Generic[T]):

    def __init__(self,
                 cls: type[T],
                 id: Union[str, ObjectId]) -> None:
        self.cls = cls
        self.id = ObjectId(id)

    def exec(self) -> T:
        collection = Connection.get_collection(self.cls)
        fetched_object = collection.find_one({'_id': self.id})
        if fetched_object is not None:
            return Decoder().decode_root(fetched_object, self.cls)
        raise ObjectNotFoundException(
            f'{self.cls.__name__}(_id={self.id}) not found.')

    def __await__(self) -> Generator[None, None, T]:
        yield
        return self.exec()

    @property
    def optional(self) -> OptionalIDQuery:
        return OptionalIDQuery(cls=self.cls, id=self.id)


class OptionalIDQuery(IDQuery):

    def exec(self) -> Optional[T]:
        try:
            return super().exec()
        except ObjectNotFoundException:
            return None


class BaseQuery(Generic[T]):

    def __init__(self, cls: type[T]) -> None:
        self.cls = cls
        self.filter: Optional[dict[str, Any]] = None
        self.sort: Optional[list[tuple[str, int]]] = None
        self.projection: Optional[Union[list[str], dict[str, Any]]] = None
        self.skipping: Optional[int] = None
        self.limiting: Optional[int] = None

    def _exec(self) -> list[T]:
        kwargs: dict[str, Any] = {}
        if self.filter is not None:
            kwargs['filter'] = self.filter
        if self.sort is not None:
            kwargs['sort'] = self.sort
        if self.projection is not None:
            kwargs['projection'] = self.projection
        if self.skipping is not None:
            kwargs['skip'] = self.skipping
        if self.limiting is not None:
            kwargs['limit'] = self.limiting
        cursor = Connection.get_collection(self.cls).find(**kwargs)
        results = [doc for doc in cursor]
        coder = Decoder()
        return list(map(lambda doc: coder.decode_root(doc, self.cls), results))


class ListQuery(BaseQuery, Generic[T]):

    def __init__(self,
                 cls: type[T],
                 filter: Optional[dict[str, Any]] = None) -> None:
        super().__init__(cls=cls)
        self.filter = _update_cases(filter, cls.dbconf.camelize_db_keys)

    def __call__(self, filter: Optional[dict[str, Any]] = None) -> ListQuery:
        self.filter = _update_cases(filter, self.cls.dbconf.camelize_db_keys)
        return self

    def exec(self) -> list[T]:
        return super()._exec()


    @overload
    def project(self, projection: list[str]) -> ListQuery: ...

    @overload
    def project(self, projection: dict[str, Any]) -> ListQuery: ...

    def project(self, projection: Any) -> ListQuery:
        self.projection = projection
        return self

    def skip(self, skipping: int) -> ListQuery:
        self.skipping = skipping
        return self

    def limit(self, limiting: int) -> ListQuery:
        self.limiting = limiting
        return self

    def __await__(self) -> Generator[None, None, list[T]]:
        yield
        return self._exec()


class SingleQuery(BaseQuery, Generic[T]):

    def __init__(self, query: BaseQuery) -> None:
        super().__init__(cls=query.cls)
        self.filter = query.filter
        self.sort = query.sort
        self.projection = query.projection
        self.skipping = query.skipping
        self.limiting = 1

    def exec(self) -> T:
        results: list[T] = super()._exec()
        if len(results) < 1:
            raise ObjectNotFoundException(
                f'{self.cls.__name__}(filter={self.filter}, '
                f'sort={self.sort}, projection={self.projection}, '
                f'skipping={self.skipping}) not found.')
        return results[0]

    def __await__(self) -> Generator[None, None, T]:
        yield
        return self.exec()

    @property
    def optional(self) -> OptionalSingleQuery[T]:
        return OptionalSingleQuery(self)


class OptionalSingleQuery(SingleQuery, Generic[T]):

    def exec(self) -> Optional[T]:
        results: list[T] = super()._exec()
        if len(results) < 1:
            return None
        return results[0]

    def __await__(self) -> Generator[None, None, Optional[T]]:
        yield
        return self.exec()


class ExistQuery(Generic[T]):

    def __init__(self,
                 cls: type[T],
                 filter: Optional[dict[str, Any]] = None) -> None:
        self.cls = cls
        self.filter = _update_cases(filter, cls.dbconf.camelize_db_keys)

    def exec(self) -> bool:
        result = Connection.get_collection(self.cls).count_documents(
                self.filter, limit=1)
        return False if result == 0 else True

    def __await__(self) -> Generator[None, None, bool]:
        yield
        return self.exec()


class QueryIterator(Generic[T]):

    def __init__(self, cls: type[T], cursor: Cursor):
        self.cls = cls
        self.cursor = cursor

    def __iter__(self):
        return self

    def __next__(self) -> T:
        value = self.cursor.__next__()
        return Decoder().decode_root(value, self.cls)


class IterateQuery(Generic[T]):

    def __init__(self,
                 cls: type[T],
                 filter: Optional[dict[str, Any]] = None) -> None:
        self.cls = cls
        self.filter = _update_cases(filter, cls.dbconf.camelize_db_keys)

    def exec(self) -> Iterator[T]:
        coll = Connection.from_class(self.cls).get_collection(self.cls)
        cursor = coll.find(self.filter)
        return QueryIterator(cls=self.cls, cursor=cursor)
