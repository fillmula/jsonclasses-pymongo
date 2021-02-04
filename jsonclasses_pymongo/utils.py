from __future__ import annotations
from os import getenv
from typing import Optional, TYPE_CHECKING
from pymongo import MongoClient
from pymongo.database import Database
from inflection import camelize
if TYPE_CHECKING:
    from .base_mongo_object import BaseMongoObject

__database_url: str = getenv(
    'DATABASE_URL') or 'mongodb://localhost:27017/jsonclassespymongodemo'
__mongo_client: Optional[MongoClient] = None
__database: Optional[Database] = None


def database_url() -> str:
    return __database_url


def default_client() -> MongoClient:
    global __mongo_client
    if __mongo_client is None:
        __mongo_client = MongoClient(database_url())
    return __mongo_client


def default_db() -> Database:
    global __database
    if __database is None:
        __database = default_client().get_database()
    return __database


def ref_key(key: str, cls: type[BaseMongoObject]) -> tuple[str, str]:
    field_name = key + '_id'
    if cls.config.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return (field_name, db_field_name)


def ref_field_key(key: str) -> str:
    return key + '_id'


def ref_db_field_key(key: str, cls: type[BaseMongoObject]) -> str:
    field_name = ref_field_key(key)
    if cls.config.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return db_field_name


def ref_field_keys(key: str) -> str:
    return key + '_ids'


def ref_db_field_keys(key: str, cls: type[BaseMongoObject]) -> str:
    field_name = ref_field_keys(key)
    if cls.config.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return db_field_name
