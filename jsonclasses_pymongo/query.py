"""This module contains id query."""
from __future__ import annotations
from typing import (Union, TypeVar, Type, Generator, Optional, List, Dict, Any,
                    Tuple, overload, cast, TYPE_CHECKING)
from bson import ObjectId
from jsonclasses import ObjectNotFoundException
from .decoder import Decoder
if TYPE_CHECKING:
    from .mongo_object import MongoObject
    T = TypeVar('T', bound=MongoObject)


class BaseIDQuery():

    def __init__(self,
                 cls: Type[T],
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
    def softly(self) -> SoftIDQuery:
        return SoftIDQuery(cls=self.cls, id=self.id)


class SoftIDQuery(BaseIDQuery):

    def __await__(self) -> Generator[None, None, Optional[T]]:
        yield
        try:
            return self._fetch()
        except ObjectNotFoundException:
            return None


class ListQuery():

    def __init__(self,
                 cls: Type[T],
                 filter: Optional[Dict[str, Any]] = None) -> None:
        self.cls = cls
        self.filter = filter
        self.sort: Optional[List[Tuple[str, int]]] = None
        self.projection: Optional[Union[List[str], Dict[str, Any]]] = None
        self.skipping: Optional[int] = None
        self.limiting: Optional[int] = None

    def __call__(self, filter: Optional[Dict[str, Any]] = None) -> ListQuery:
        self.filter = filter
        return self

    def where(self, filter: Dict[str, Any]) -> ListQuery:
        self.filter = filter
        return self

    @overload
    def order(self, sort: str) -> ListQuery: ...

    @overload
    def order(self, sort: Tuple[str, int]) -> ListQuery: ...

    @overload
    def order(self, sort: List[Tuple[str, int]]) -> ListQuery: ...

    def order(self, sort: Any) -> ListQuery:
        if isinstance(sort, str):
            self.sort = [(sort, 1)]
        elif isinstance(sort, tuple):
            self.sort = [cast(Tuple[str, int], sort)]
        elif isinstance(sort, list):
            self.sort = sort
        else:
            self.sort = None
        return self

    @overload
    def project(self, projection: List[str]) -> ListQuery: ...

    @overload
    def project(self, projection: Dict[str, Any]) -> ListQuery: ...

    def project(self, projection: Any) -> ListQuery:
        self.projection = projection
        return self

    def skip(self, skipping: int) -> ListQuery:
        self.skipping = skipping
        return self

    def limit(self, limiting: int) -> ListQuery:
        self.limiting = limiting
        return self

    def _fetch(self) -> List[T]:
        kwargs: Dict[str, Any] = {}
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

    def __await__(self) -> Generator[None, None, List[T]]:
        yield
        return self._fetch()
