from __future__ import annotations
from unittest import TestCase
from tests.classes.preload import PLUser, PLArticle
from jsonclasses_pymongo.connection import Connection
from jsonclasses_pymongo.preload import preload
from tests.classes.links_preload import LJPLArticle, LJPLUser


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
        # collection = Connection.get_collection(LLPLUser)
        # collection.delete_many({})
        # collection = Connection.get_collection(LLPLArticle)
        # collection.delete_many({})
        collection = Connection.get_collection(LJPLUser)
        collection.delete_many({})
        collection = Connection.get_collection(LJPLArticle)
        collection.delete_many({})
        collection = Connection('preload').collection('ljplarticlesauthorsljplusersarticles')
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

    def test_preload_load_linked_data_from_file(self):
        preload('tests/data/links_preload.json')
        users = LJPLUser.find().exec()
        articles = LJPLArticle.find().exec()
        self.assertEqual(len(users), 3)
        self.assertEqual(len(articles), 2)


    def test_preload_load_empty_linked_data_from_file(self):
        preload('tests/data/links_preload.json')
        ben_user = LJPLUser.one(name="Peter Benson").include('articles').exec()
        self.assertEqual(ben_user.name,"Peter Benson")
        self.assertEqual(len(ben_user.articles),0)
        
    def test_preload_load_multi_linked_data_from_file(self):
        preload('tests/data/links_preload.json')
        articles = LJPLArticle.find().exec()
        chun_articles = LJPLUser.one(name="Chun Peterson").include('articles').exec()
        self.assertEqual(len(chun_articles.articles), 2)
        self.assertEqual(chun_articles.articles[0].id,articles[0].id)
        self.assertEqual(chun_articles.articles[1].id,articles[1].id)

    # def test_preload_load_local_linked_data_from_file(self):
    #     preload('tests/data/local_links_preload.json')
    #     users = LLPLUser.find().exec()
    #     articles = LLPLArticle.find().exec()
    #     self.assertEqual(len(users), 3)
    #     self.assertEqual(len(articles), 2)
    
