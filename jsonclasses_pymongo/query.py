"""This module contains id query."""
from __future__ import annotations
from typing import (Union, TypeVar, Generator, Optional, Any, Generic,
                    overload, cast, TYPE_CHECKING)
from bson import ObjectId
from jsonclasses.exceptions import ObjectNotFoundException
from inflection import camelize
from .decoder import Decoder
from .connection import Connection
T = TypeVar('T')


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

    def __await__(self) -> Generator[None, None, list[T]]:
        yield
        return self._exec()


class ListQuery(BaseQuery, Generic[T]):

    def __init__(self,
                 cls: type[T],
                 filter: Optional[dict[str, Any]] = None) -> None:
        super().__init__(cls=cls)
        if filter is not None and filter.get('id'):
            filter['_id'] = ObjectId(filter['id'])
            del filter['id']
        self.filter = self._update_cases(filter)

    def __call__(self, filter: Optional[dict[str, Any]] = None) -> ListQuery:
        self.filter = self._update_cases(filter)
        return self

    def _update_cases(self,
                      d: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        if not self.cls.dbconf.camelize_db_keys:
            return d
        if d is None:
            return None
        retval: dict[str, Any] = {}
        for key, value in d.items():
            retval[camelize(key, False)] = value
        return retval

    def exec(self) -> list[T]:
        return super()._exec()

    def where(self, filter: dict[str, Any]) -> ListQuery:
        self.filter = filter
        return self

    @overload
    def order(self, sort: str) -> ListQuery: ...

    @overload
    def order(self, sort: tuple[str, int]) -> ListQuery: ...

    @overload
    def order(self, sort: list[tuple[str, int]]) -> ListQuery: ...

    def order(self, sort: Any) -> ListQuery:
        if isinstance(sort, str):
            self.sort = [(sort, 1)]
        elif isinstance(sort, tuple):
            self.sort = [cast(tuple[str, int], sort)]
        elif isinstance(sort, list):
            self.sort = sort
        else:
            self.sort = None
        return self

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

    @property
    def first(self) -> SingleQuery[T]:
        return SingleQuery(self)


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

    @property
    def optional(self) -> OptionalSingleQuery[T]:
        return OptionalSingleQuery(self)


class OptionalSingleQuery(SingleQuery, Generic[T]):

    def exec(self) -> Optional[T]:
        results: list[T] = super()._exec()
        if len(results) < 1:
            return None
        return results[0]
