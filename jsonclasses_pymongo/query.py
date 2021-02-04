"""This module contains id query."""
from __future__ import annotations
from typing import (Union, TypeVar, Generator, Optional, Any, overload, cast,
                    TYPE_CHECKING)
from bson import ObjectId
from jsonclasses import ObjectNotFoundException
from .decoder import Decoder
if TYPE_CHECKING:
    from .base_mongo_object import BaseMongoObject
    T = TypeVar('T', bound=BaseMongoObject)


class BaseIDQuery():

    def __init__(self,
                 cls: type[T],
                 id: Union[str, ObjectId]) -> None:
        self.cls = cls
        self.id = ObjectId(id)

    def _fetch(self) -> T:
        fetched_object = self.cls.collection().find_one({'_id': self.id})
        if fetched_object is not None:
            return Decoder().decode_root(fetched_object, self.cls)
        raise ObjectNotFoundException(
            f'{self.cls.__name__}(_id={self.id}) not found.')


class IDQuery(BaseIDQuery):

    def __await__(self) -> Generator[None, None, T]:
        yield
        return self._fetch()

    @property
    def optional(self) -> OptionalIDQuery:
        return OptionalIDQuery(cls=self.cls, id=self.id)


class OptionalIDQuery(BaseIDQuery):

    def __await__(self) -> Generator[None, None, Optional[T]]:
        yield
        try:
            return self._fetch()
        except ObjectNotFoundException:
            return None


class BaseQuery():

    def __init__(self, cls: type[T]) -> None:
        self.cls = cls
        self.filter: Optional[dict[str, Any]] = None
        self.sort: Optional[list[tuple[str, int]]] = None
        self.projection: Optional[Union[list[str], dict[str, Any]]] = None
        self.skipping: Optional[int] = None
        self.limiting: Optional[int] = None

    def _fetch(self) -> list[T]:
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
        cursor = self.cls.collection().find(**kwargs)
        results = [doc for doc in cursor]
        coder = Decoder()
        return list(map(lambda doc: coder.decode_root(doc, self.cls), results))


class ListQuery(BaseQuery):

    def __init__(self,
                 cls: type[T],
                 filter: Optional[dict[str, Any]] = None) -> None:
        super().__init__(cls=cls)
        self.filter = filter

    def __call__(self, filter: Optional[dict[str, Any]] = None) -> ListQuery:
        self.filter = filter
        return self

    def __await__(self) -> Generator[None, None, list[T]]:
        yield
        return self._fetch()

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
    def one(self) -> SingleQuery:
        return SingleQuery(self)


class SingleQuery(BaseQuery):

    def __init__(self, query: BaseQuery) -> None:
        super().__init__(cls=query.cls)
        self.filter = query.filter
        self.sort = query.sort
        self.projection = query.projection
        self.skipping = query.skipping
        self.limiting = 1

    def __await__(self) -> Generator[None, None, T]:
        yield
        results: list[T] = self._fetch()
        if len(results) < 1:
            raise ObjectNotFoundException(
                f'{self.cls.__name__}(filter={self.filter}, '
                f'sort={self.sort}, projection={self.projection}, '
                f'skipping={self.skipping}) not found.')
        return results[0]

    @property
    def optional(self) -> OptionalSingleQuery:
        return OptionalSingleQuery(self)


class OptionalSingleQuery(BaseQuery):

    def __init__(self, query: SingleQuery) -> None:
        super().__init__(cls=query.cls)
        self.filter = query.filter
        self.sort = query.sort
        self.projection = query.projection
        self.skipping = query.skipping
        self.limiting = 1

    def __await__(self) -> Generator[None, None, Optional[T]]:
        yield
        results: list[T] = self._fetch()
        if len(results) < 1:
            return None
        return results[0]
