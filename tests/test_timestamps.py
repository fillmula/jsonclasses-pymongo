from __future__ import annotations
from typing import Optional
from unittest import TestCase
from jsonclasses import jsonclass, types
from datetime import datetime
from jsonclasses_pymongo import MongoObject, connector


@jsonclass
class MyMongoObject(MongoObject):
    name: Optional[str]


class TestMongoObject(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        connector.connect('mongodb://localhost:27017/jsonclasses')

    def test_mongo_object_has_created_at_on_initializing(self):
        o = MyMongoObject()
        self.assertTrue(type(o.created_at) is datetime)
        self.assertTrue(o.created_at < datetime.now())

    def test_mongo_object_has_updated_at_on_initializing(self):
        o = MyMongoObject()
        self.assertTrue(type(o.updated_at) is datetime)
        self.assertTrue(o.updated_at < datetime.now())

    def test_mongo_object_has_id_with_random_str_default_value(self):
        o = MyMongoObject()
        self.assertTrue(o.id is not None)

    def test_mongo_object_id_can_not_be_int(self):
        o = MyMongoObject()
        o.id = 5
        self.assertFalse(o.is_valid())

    def test_mongo_object_id_can_be_str(self):
        o = MyMongoObject()
        o.id = "sbd"
        self.assertTrue(o.is_valid())

    def test_mongo_object_id_can_not_be_none(self):
        o = MyMongoObject()
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
