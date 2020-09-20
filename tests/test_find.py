from __future__ import annotations
import unittest
from typing import List
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
        TestUser.delete()
        TestUser(username='a', password='b').save()
        TestUser(username='c', password='d').save()
        find_result = TestUser.find()
        self.assertEqual(len(find_result), 2)
        self.assertEqual(find_result[0].username, 'a')
        self.assertEqual(find_result[0].password, 'b')
        self.assertEqual(find_result[1].username, 'c')
        self.assertEqual(find_result[1].password, 'd')

    def test_include_includes_many_to_many(self):
        @jsonclass
        class UestAuthor(MongoObject):
            name: str
            posts: List[UestPost] = types.listof(
                'UestPost').linkedthru('authors')

        @jsonclass
        class UestPost(MongoObject):
            title: str
            authors: List[UestAuthor] = types.listof(
                'UestAuthor').linkedthru('posts')
        author = UestAuthor(
            **{'name': 'Michael', 'posts': [{'title': 'PA'}, {'title': 'PB'}]})
        author.save()
        returned_author = UestAuthor.find_by_id(author.id).include('posts')
        self.assertEqual(len(returned_author.posts), 2)
        self.assertEqual(returned_author.posts[0].title, author.posts[0].title)
        self.assertEqual(returned_author.posts[1].title, author.posts[1].title)
