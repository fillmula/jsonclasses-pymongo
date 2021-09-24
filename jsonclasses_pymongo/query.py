"""This module contains queries."""
from __future__ import annotations
from jsonclasses_pymongo.query_to_object import query_to_object
from jsonclasses_pymongo.query_reader import QueryReader
from typing import (Iterator, Union, TypeVar, Generator, Optional, Any,
                    Generic, NamedTuple, cast)
from datetime import date, datetime
from bson import ObjectId
from inflection import camelize
from pymongo.cursor import Cursor
from jsonclasses.fdef import FStore, FType
from jsonclasses.mgraph import MGraph
from jsonclasses.excs import ObjectNotFoundException
from .coder import Coder
from .decoder import Decoder
from .connection import Connection
from .pymongo_object import PymongoObject
from .utils import ref_db_field_key
T = TypeVar('T', bound=PymongoObject)
U = TypeVar('U', bound='BaseQuery')
V = TypeVar('V', bound='BaseListQuery')


class Subquery(NamedTuple):
    name: str
    query: Optional[BaseQuery]


class BaseQuery(Generic[T]):
    """Base query is the base class of queries.
    """

    def __init__(self: U, cls: type[T]) -> None:
        self._cls = cls
        self.subqueries: list[Subquery] = []

    def include(self: U, name: str, query: Optional[BaseQuery] = None) -> U:
        self.subqueries.append(Subquery(name, query))
        return self

    def _build_aggregate_pipeline(self: U) -> list[dict[str, Any]]:
        cls = cast(type[PymongoObject], self._cls)
        result: list[dict[str, Any]] = []
        for subquery in self.subqueries:
            fname = subquery.name
            field = cls.cdef.field_named(fname)
            if field.fdef.ftype == FType.LIST:
                it = field.fdef.item_types.fdef.inst_cls
            else:
                it = field.fdef.inst_cls
            if field.fdef.fstore == FStore.LOCAL_KEY:
                key = ref_db_field_key(fname, cls)
                if subquery.query is None:
                    result.append({
                        '$lookup': {
                            'from': it.pconf.collection_name,
                            'localField': key,
                            'foreignField': '_id',
                            'as': fname
                        }
                    })
                else:
                    subpipeline = subquery.query._build_aggregate_pipeline()
                    subpipeline.insert(0, {
                        '$match': {
                            '$expr': {
                                '$and': [{'$eq': ['$_id', '$$'+key]}]
                            }
                        }
                    })
                    result.append({
                        '$lookup': {
                            'from': it.pconf.collection_name,
                            'as': fname,
                            'let': {key: '$' + key},
                            'pipeline': subpipeline
                        }
                    })
                result.append({
                    '$unwind': '$' + fname
                })
            elif field.fdef.fstore == FStore.FOREIGN_KEY:
                if field.fdef.ftype == FType.INSTANCE:
                    fk = cast(str, field.fdef.foreign_key)
                    if subquery.query is None:
                        result.append({
                            '$lookup': {
                                'from': it.pconf.collection_name,
                                'localField': '_id',
                                'foreignField': ref_db_field_key(fk, it),
                                'as': fname
                            }
                        })
                    else:
                        fk = cast(str, field.fdef.foreign_key)
                        key = ref_db_field_key(fk, it)
                        subp = subquery.query._build_aggregate_pipeline()
                        subp.insert(0, {
                            '$match': {
                                '$expr': {
                                    '$and': [{'$eq': ['$'+key, '$$'+key]}]
                                }
                            }
                        })
                        result.append({
                            '$lookup': {
                                'from': it.pconf.collection_name,
                                'as': fname,
                                'let': {key: '$_id'},
                                'pipeline': subp
                            }
                        })
                    result.append({
                        '$unwind': '$' + fname
                    })
                elif field.fdef.ftype == FType.LIST:
                    if subquery.query is not None:
                        subpipeline = subquery.query \
                                                ._build_aggregate_pipeline()
                    else:
                        subpipeline = []
                    has_match = False
                    matcher = None
                    for item in subpipeline:
                        if item.get('$match'):
                            has_match = True
                            matcher = item.get('$match')
                            break
                    if field.fdef.use_join_table:
                        coder = Coder()
                        jt_name = coder.join_table_name(cls, field.name,
                                                        it, field.foreign_field.name)
                        this_key = ref_db_field_key(cls.__name__, cls)
                        that_key = ref_db_field_key(it.__name__, it)
                        pipeline: list[Any] = []
                        if matcher is None:
                            matcher = {}
                        if not matcher.get('$expr'):
                            matcher['$expr'] = {}
                        if not matcher['$expr'].get('$and'):
                            matcher['$expr']['$and'] = []
                        matcher['$expr']['$and'].append({
                            '$eq': ['$_id', '$$' + that_key]
                        })
                        if not has_match:
                            subpipeline.insert(0, {'$match': matcher})
                        outer_lookup = {'$lookup': {
                            'from': jt_name,
                            'as': field.name,
                            'let': {this_key: '$_id'},
                            'pipeline': pipeline
                        }}
                        match = {'$match': {
                            '$expr': {
                                '$and': [
                                    {'$eq': ['$'+this_key, '$$'+this_key]}
                                ]
                            }
                        }}
                        lookup = {'$lookup': {
                            'from': it.pconf.collection_name,
                            'as': field.name,
                            'let': {that_key: '$'+that_key},
                            'pipeline': subpipeline
                        }}
                        unwind = {
                            '$unwind': '$' + field.name
                        }
                        replace = {
                            '$replaceRoot': {'newRoot': '$'+field.name}
                        }
                        pipeline.append(match)
                        pipeline.append(lookup)
                        pipeline.append(unwind)
                        pipeline.append(replace)
                        result.append(outer_lookup)
                    else:
                        fk = cast(str, field.fdef.foreign_key)
                        key = ref_db_field_key(fk, it)
                        item = {
                            '$lookup': {
                                'from': it.pconf.collection_name,
                                'as': fname,
                                'let': {key: '$_id'},
                                'pipeline': subpipeline
                            }
                        }
                        if matcher is None:
                            matcher = {}
                        if not matcher.get('$expr'):
                            matcher['$expr'] = {}
                        if not matcher['$expr'].get('$and'):
                            matcher['$expr']['$and'] = []
                        matcher['$expr']['$and'].append({
                            '$eq': ['$' + key, '$$' + key]
                        })
                        if not has_match:
                            subpipeline.insert(0, {'$match': matcher})
                        result.append(item)
        return result


class BaseListQuery(BaseQuery[T]):
    """Base list query is the base class of list queries.
    """

    def __init__(self: V,
                 cls: type[T],
                 filter: Union[dict[str, Any], str, None] = None) -> None:
        super().__init__(cls)
        self._match: Optional[dict[str, Any]] = None
        self._sort: Optional[list[tuple[str, int]]] = None
        self._page_number: Optional[int] = None
        self._page_size: Optional[int] = None
        self._skip: Optional[int] = None
        self._limit: Optional[int] = None
        self._use_pick: bool = False
        self._pick: Optional[dict[str, Any]] = None
        self._use_omit: bool = False
        self._omit: Optional[dict[str, Any]] = None
        if filter is not None:
            if type(filter) is str:
                filter = query_to_object(filter)
            self._set_matcher(cast(dict, filter))

    def _set_matcher(self: V, matcher: dict[str, Any]) -> None:
        result = QueryReader(query=matcher, cls=self._cls).result()
        if result.get('_match') is not None:
            self._match = result['_match']
        if result.get('_sort') is not None:
            self._sort = result['_sort']
        if result.get('_page_number') is not None:
            self._page_number = result['_page_number']
        if result.get('_page_size') is not None:
            self._page_size = result['_page_size']
        if result.get('_skip') is not None:
            self._skip = result['_skip']
        if result.get('_limit') is not None:
            self._limit = result['_limit']

    def order(self: V, field: str, sort: Optional[int] = None) -> V:
        if self._sort is None:
            self._sort = []
        self._sort.append((field, sort or 1))
        return self

    def skip(self: V, n: int) -> V:
        self._skip = n
        return self

    def limit(self: V, n: int) -> V:
        self._limit = n
        return self

    def page_number(self: V, n: int) -> V:
        self._page_number = n
        if self._page_size is None:
            self._page_size = 30
        return self

    def page_no(self: V, n: int) -> V:
        return self.page_number(n)

    def page_size(self: V, n: int) -> V:
        self._page_size = n
        return self

    def _build_aggregate_pipeline(self: V) -> list[dict[str, Any]]:
        lookups = super()._build_aggregate_pipeline()
        result: list[dict[str, Any]] = []
        if self._match is not None:
            result.append({'$match': self._match})
        if self._sort is not None:
            result.append({'$sort': dict(self._sort)})
        if self._page_number is not None and self._page_size is not None:
            result.append({'$skip': (self._page_number - 1) * self._page_size})
        else:
            if self._skip is not None:
                result.append({'$skip': self._skip})
            if self._limit is not None:
                result.append({'$limit': self._limit})
        result.extend(lookups)
        return result

    def _exec(self: V) -> list[T]:
        pipeline = self._build_aggregate_pipeline()
        collection = Connection.get_collection(self._cls)
        cursor = collection.aggregate(pipeline)
        results = [result for result in cursor]
        return Decoder().decode_root_list(results, self._cls)


class ListQuery(BaseListQuery[T]):
    """Query a list of objects.
    """

    def exec(self) -> list[T]:
        return self._exec()

    def __await__(self) -> Generator[None, None, list[T]]:
        yield
        return self.exec()


class SingleQuery(BaseListQuery[T]):
    """Queries only one object from the query.
    """

    def exec(self) -> T:
        self._limit = 1
        results = self._exec()
        if len(results) == 0:
            raise ObjectNotFoundException('object is not found')
        return results[0]

    def __await__(self) -> Generator[None, None, T]:
        yield
        return self.exec()

    @property
    def optional(self) -> OptionalSingleQuery:
        query = OptionalSingleQuery(cls=self._cls)
        query.subqueries = self.subqueries
        query._match = self._match
        query._sort = self._sort
        query._skip = self._skip
        query._limit = self._limit
        query._use_pick = self._use_pick
        query._pick = self._pick
        query._use_omit = self._use_omit
        query._omit = self._omit
        return query


class OptionalSingleQuery(BaseListQuery[T]):
    """Queries only one object from the query. Returns None if not found.
    """

    def exec(self) -> Optional[T]:
        self._limit = 1
        results = self._exec()
        if len(results) == 0:
            return None
        return results[0]

    def __await__(self) -> Generator[None, None, Optional[T]]:
        yield
        return self.exec()


class BaseIDQuery(BaseQuery[T]):
    """Query collection from object id.
    """

    def __init__(self: U, cls: type[T], id: Union[str, ObjectId]) -> None:
        super().__init__(cls)
        self._id = id

    def _build_aggregate_pipeline(self: BaseIDQuery) -> list[dict[str, Any]]:
        lookups = super()._build_aggregate_pipeline()
        result: list[dict[str, Any]] = []
        result.append({'$match': {'_id': ObjectId(self._id)}})
        result.extend(lookups)
        return result

    def _exec(self) -> Optional[T]:
        pipeline = self._build_aggregate_pipeline()
        collection = Connection.get_collection(self._cls)
        cursor = collection.aggregate(pipeline)
        results = [result for result in cursor]
        if len(results) == 0:
            return None
        return Decoder().decode_root(results[0], self._cls)


class IDQuery(BaseIDQuery[T]):
    """Query collection from object id. Raises ObjectNotFoundException if not
    found.
    """

    def exec(self) -> T:
        result = self._exec()
        if result is not None:
            return result
        raise ObjectNotFoundException(
            f'{self._cls.__name__}(_id={self._id}) not found.')

    def __await__(self) -> Generator[None, None, T]:
        yield
        return self.exec()

    @property
    def optional(self) -> OptionalIDQuery:
        new_query = OptionalIDQuery(cls=self._cls, id=self._id)
        new_query.subqueries = self.subqueries
        return new_query


class OptionalIDQuery(BaseIDQuery[T]):
    """Query collection from object id. Returns None if not found.
    """

    def exec(self) -> Optional[T]:
        return self._exec()

    def __await__(self) -> Generator[None, None, Optional[T]]:
        yield
        return self.exec()


class ExistQuery(BaseListQuery[T]):

    def exec(self) -> bool:
        collection = Connection.get_collection(self._cls)
        result = collection.count_documents(self._match or {}, limit=1)
        return False if result == 0 else True

    def __await__(self) -> Generator[None, None, bool]:
        yield
        return self.exec()


class QueryIterator(Generic[T]):

    def __init__(self, cls: type[T], cursor: Cursor):
        self.cls = cls
        self.cursor = cursor
        self.graph = MGraph()

    def __iter__(self):
        return self

    def __next__(self) -> T:
        value = self.cursor.__next__()
        return Decoder().decode_root(value, self.cls, self.graph)


class IterateQuery(BaseListQuery[T]):

    def exec(self) -> Iterator[T]:
        pipeline = self._build_aggregate_pipeline()
        collection = Connection.get_collection(self._cls)
        cursor = collection.aggregate(pipeline)
        return QueryIterator(cls=self._cls, cursor=cursor)

    def __await__(self) -> Generator[None, None, Iterator[T]]:
        yield
        return self.exec()
