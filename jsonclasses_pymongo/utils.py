from os import getenv
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database

__database_url: str = getenv('DATABASE_URL') or 'mongodb://localhost:27017/jsonclasses-pymongo-demo'
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
