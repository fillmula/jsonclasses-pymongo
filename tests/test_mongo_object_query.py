import unittest
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import MongoObject

class TestMongoObjectQuery(unittest.TestCase):

  def test_find_returns_list(self):
    @jsonclass
    class TestUser(MongoObject):
      username: str = types.str.writeonce.unique.required
      password: str = types.str.writeonly.minlength(8).maxlength(16).transform(lambda p: p + '00xx').required
      nickname: str = types.str.maxlength(30).required
      gender: str = types.str.writeonce.one_of(['male', 'female'])
      email: str = types.str.unique.required
      phone_no: str
      wechat_open_id: str
    _user = TestUser()
