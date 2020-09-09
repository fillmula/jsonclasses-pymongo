import unittest
from dotenv import load_dotenv
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import MongoObject

class TestMongoObjectQuery(unittest.TestCase):

  def setUp(self):
    load_dotenv()

  def test_find_returns_list(self):
    @jsonclass
    class TestUser(MongoObject):
      username: str
      password: str
    TestUser(username='a', password='b').save()
    TestUser(username='c', password='d').save()
    result = TestUser.find()
