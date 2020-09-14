from __future__ import annotations
import unittest
from typing import List
from dotenv import load_dotenv
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import MongoObject

class TestMongoObjectSave(unittest.TestCase):

  def setUp(self):
    load_dotenv()

  def test_save_multiple_instances_to_db(self):
    @jsonclass
    class TestAuthor(MongoObject):
      name: str
      posts: List[TestPost] = types.listof('TestPost').linkedby('author')
    @jsonclass
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
    author.save()
    returned_author = TestAuthor.find_by_id(author.id)
    self.assertEqual(returned_author.name, author.name)
    returned_author_with_posts = TestAuthor.find_by_id(author.id).include('posts')
    self.assertEqual(len(returned_author_with_posts.posts), 2)
    returned_post_0 = TestPost.find_by_id(author.posts[0].id)
    self.assertEqual(returned_post_0.title, author.posts[0].title)
    returned_post_0_with_author = TestPost.find_by_id(author.posts[0].id).include('author')
    self.assertEqual(returned_post_0_with_author.author.name, author.name)
