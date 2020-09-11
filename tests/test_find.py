import unittest
from dotenv import load_dotenv
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import MongoObject

class TestMongoObjectQuery(unittest.TestCase):

  def setUp(self):
    load_dotenv()

  # def test_find_returns_list(self):
  #   @jsonclass
  #   class TestUser(MongoObject):
  #     username: str
  #     password: str
  #   TestUser.delete()
  #   TestUser(username='a', password='b').save()
  #   TestUser(username='c', password='d').save()
  #   find_result = TestUser.find()
  #   self.assertEqual(len(find_result), 2)
  #   self.assertEqual(find_result[0].username, 'a')
  #   self.assertEqual(find_result[0].password, 'b')
  #   self.assertEqual(find_result[1].username, 'c')
  #   self.assertEqual(find_result[1].password, 'd')
