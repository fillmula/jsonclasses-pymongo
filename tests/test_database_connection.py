from unittest import IsolatedAsyncioTestCase
from jsonclasses import jsonclass
from jsonclasses_pymongo import MongoObject


class TestDatabaseConnection(IsolatedAsyncioTestCase):

    async def test_two_classes_share_same_database(self):
        @jsonclass
        class Article(MongoObject):
            title: str
            content: str

        @jsonclass
        class Author(MongoObject):
            name: str
        await Article.find()
        await Author.find()
        self.assertEqual(Article.db(), Author.db())
