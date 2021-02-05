from __future__ import annotations
import unittest
from jsonclasses import jsonclass, types
from datetime import datetime
from jsonclasses_pymongo import MongoObject


class TestORMObject(unittest.TestCase):

    def test_mongo_object_has_created_at_on_initializing(self):
        o = MongoObject()
        self.assertTrue(type(o.created_at) is datetime)
        self.assertTrue(o.created_at < datetime.now())

    def test_mongo_object_has_updated_at_on_initializing(self):
        o = MongoObject()
        self.assertTrue(type(o.updated_at) is datetime)
        self.assertTrue(o.updated_at < datetime.now())

    def test_mongo_object_has_id_with_random_str_default_value(self):
        o = MongoObject()
        self.assertTrue(o.id is not None)

    def test_mongo_object_id_can_not_be_int(self):
        o = MongoObject()
        o.id = 5
        self.assertFalse(o.is_valid())

    def test_mongo_object_id_can_be_str(self):
        o = MongoObject()
        o.id = "sbd"
        self.assertTrue(o.is_valid())

    def test_mongo_object_id_can_not_be_none(self):
        o = MongoObject()
        o.id = None
        self.assertFalse(o.is_valid())

    def test_mongo_object_has_timestamps_in_nested_instances(self):
        @jsonclass(class_graph='test_persistable_json_01')
        class TestAuthor(MongoObject):
            name: str
            posts: list[TestPost] = types.listof('TestPost').linkedby('author')

        @jsonclass(class_graph='test_persistable_json_01')
        class TestPost(MongoObject):
            title: str
            content: str
            author: TestAuthor = types.linkto.instanceof(TestAuthor)

        input = {
            'name': 'John Lesque',
            'posts': [
                {
                    'title': 'Post One',
                    'content': 'Great Article on Python.'
                },
                {
                    'title': 'Post Two',
                    'content': 'Great Article on JSON Classes.'
                }
            ]
        }
        author = TestAuthor(**input)
        self.assertIs(type(author.created_at), datetime)
        self.assertIs(type(author.updated_at), datetime)
        self.assertIs(type(author.posts[0].created_at), datetime)
        self.assertIs(type(author.posts[0].updated_at), datetime)
        self.assertIs(type(author.posts[1].created_at), datetime)
        self.assertIs(type(author.posts[1].updated_at), datetime)
