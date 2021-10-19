from __future__ import annotations
from unittest import TestCase
from tests.classes.preload import PLUser, PLArticle
from jsonclasses_pymongo import Connection
from jsonclasses_pymongo.preload import preload


class TestPreload(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        connection = Connection('preload')
        connection.set_url('mongodb://localhost:27017/preload')
        connection.connect()

    @classmethod
    def tearDownClass(cls) -> None:
        connection = Connection('preload')
        connection.disconnect()

    def setUp(self) -> None:
        collection = Connection.get_collection(PLUser)
        collection.delete_many({})
        collection = Connection.get_collection(PLArticle)
        collection.delete_many({})

    def test_preload_load_data_from_file(self):
        preload('tests/data/preload.json')
        users = PLUser.find().exec()
        articles = PLArticle.find().exec()
        self.assertEqual(len(users), 3)
        self.assertEqual(len(articles), 5)
        self.assertEqual(articles[0].author_id, users[0].id)
        self.assertEqual(articles[1].author_id, users[0].id)
        self.assertEqual(articles[2].author_id, users[1].id)
        self.assertEqual(articles[3].author_id, users[2].id)
        self.assertEqual(articles[4].author_id, users[2].id)

    def test_preload_wont_update_existing_objects(self):
        preload('tests/data/preload.json')
        preload('tests/data/rewrite.json')
        articles = PLArticle.find().exec()
        self.assertFalse(articles[0].name.endswith(' 2'))
        self.assertFalse(articles[1].name.endswith(' 2'))
        self.assertFalse(articles[2].name.endswith(' 2'))
        self.assertFalse(articles[4].name.endswith(' 2'))

    def test_preload_will_update_existing_objects_if_strategy_is_reseed(self):
        preload('tests/data/preload.json')
        preload('tests/data/rewrite.json')
        articles = PLArticle.find().exec()
        self.assertTrue(articles[3].name.endswith(' 2'))
