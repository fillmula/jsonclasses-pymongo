import unittest
from dotenv import load_dotenv
from jsonclasses import jsonclass
from jsonclasses_pymongo import MongoObject


class TestDatabaseConnection(unittest.TestCase):

    def setUp(self):
        load_dotenv()

    def test_two_classes_share_same_database(self):
        @jsonclass
        class Article(MongoObject):
            title: str
            content: str

        @jsonclass
        class Author(MongoObject):
            name: str
        _articles = Article.find()
        _authors = Author.find()
        self.assertEqual(Article.db(), Author.db())
