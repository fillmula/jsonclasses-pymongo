from __future__ import annotations
from unittest import TestCase
from jsonclasses_pymongo.connection import Connection
from jsonclasses_pymongo.utils import join_table_name
from tests.classes.simple_strid import SimpleStrId
from tests.classes.linked_strid import (
    LinkedStrIdAuthor, LinkedStrIdArticle, LinkedStrIdSong, LinkedStrIdSinger,
    LinkedStrIdProduct, LinkedStrIdUser
)


class TestStrId(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        connection = Connection('simple')
        connection.set_url('mongodb://localhost:27017/simple')
        connection.connect()
        connection = Connection('linked')
        connection.set_url('mongodb://localhost:27017/linked')
        connection.connect()

    @classmethod
    def tearDownClass(cls) -> None:
        connection = Connection('simple')
        connection.disconnect()
        connection = Connection('linked')
        connection.disconnect()

    def setUp(self) -> None:
        collection = Connection.get_collection(SimpleStrId)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedStrIdAuthor)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedStrIdArticle)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedStrIdSinger)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedStrIdSong)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedStrIdUser)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedStrIdProduct)
        collection.delete_many({})
        collection = Connection('linked').collection(join_table_name(LinkedStrIdUser.cdef.field_named('products')))
        collection.delete_many({})

    def test_strid_can_be_saved(self):
        obj = SimpleStrId(id='myid', val='myval')
        obj.save()

    def test_strid_can_be_fetched(self):
        obj = SimpleStrId(id='myid', val='myval')
        obj.save()
        result = SimpleStrId.id('myid').exec()
        self.assertEqual(result.id, 'myid')

    def test_strid_can_be_saved_into_1l_reference_with_object(self):
        author = LinkedStrIdAuthor(id='authorid', val='123')
        article = LinkedStrIdArticle(id='articleid', val='123')
        article.author = author
        article.save()
        result = LinkedStrIdArticle.one().exec()
        self.assertEqual(result.author_id, 'authorid')

    def test_strid_can_be_saved_into_1l_reference_with_ref_id(self):
        author = LinkedStrIdAuthor(id='authorid', val='123')
        article = LinkedStrIdArticle(id='articleid', val='123')
        article.author_id = author.id
        article.save()
        result = LinkedStrIdArticle.one().exec()
        self.assertEqual(result.author_id, 'authorid')

    def test_strid_can_be_saved_into_manyl_reference_with_object(self):
        song = LinkedStrIdSong(id='song')
        singer1 = LinkedStrIdSinger(id='s1')
        singer2 = LinkedStrIdSinger(id='s2')
        song.singers = [singer1, singer2]
        song.save()
        song = LinkedStrIdSong.one().exec()
        self.assertEqual(song.singer_ids, ['s1', 's2'])

    def test_strid_can_be_saved_into_manyl_reference_with_ref_id(self):
        song = LinkedStrIdSong(id='song')
        singer1 = LinkedStrIdSinger(id='s1')
        singer2 = LinkedStrIdSinger(id='s2')
        song.singer_ids = [singer1.id, singer2.id]
        song.save()
        song = LinkedStrIdSong.one().exec()
        self.assertEqual(song.singer_ids, ['s1', 's2'])

    def test_strid_can_be_saved_into_many_many_join_table(self):
        user1 = LinkedStrIdUser(id='u1')
        user2 = LinkedStrIdUser(id='u2')
        prod1 = LinkedStrIdProduct(id='p1')
        prod2 = LinkedStrIdProduct(id='p2')
        user1.products = [prod1, prod2]
        user2.products = [prod1, prod2]
        user1.save()
        results = LinkedStrIdUser.find().include('products').exec()
        for result in results:
            for product in result.products:
                self.assertIn(product.id, ['p1', 'p2'])

    def test_strid_can_be_deleted(self):
        obj = SimpleStrId(id='myid', val='myval')
        obj.save()
        obj.delete()

    def test_strid_primary_id_can_be_queried(self):
        obj = SimpleStrId(id='myid', val='myval')
        obj.save()
        results = SimpleStrId.find(id='myid').exec()
        self.assertEqual(results[0].id, 'myid')

    def test_strid_local_id_can_be_queried(self):
        author = LinkedStrIdAuthor(id='authorid', val='123')
        article = LinkedStrIdArticle(id='articleid', val='123')
        article.author = author
        article.save()
        results = LinkedStrIdArticle.find(author_id='authorid').exec()
        self.assertEqual(results[0].author_id, 'authorid')

    def test_strid_local_ids_can_be_queried(self):
        song = LinkedStrIdSong(id='song')
        singer1 = LinkedStrIdSinger(id='s1')
        singer2 = LinkedStrIdSinger(id='s2')
        song.singers = [singer1, singer2]
        song.save()
        results = LinkedStrIdSong.find(singer_ids=['s1']).exec()
        self.assertEqual(results[0].singer_ids, ['s1', 's2'])
