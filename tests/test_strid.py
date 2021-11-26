from __future__ import annotations
from datetime import datetime
from unittest import TestCase
from jsonclasses_pymongo.connection import Connection
from tests.classes.simple_strid import SimpleStrId
from tests.classes.linked_strid import (
    LinkedStrIdAuthor, LinkedStrIdArticle, LinkedStrIdSong, LinkedStrIdSinger
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
        pass
