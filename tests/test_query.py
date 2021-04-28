from __future__ import annotations
from datetime import datetime
from unittest import TestCase
from bson.objectid import ObjectId
from jsonclasses_pymongo import Connection
from tests.classes.simple_song import SimpleSong
from tests.classes.simple_artist import SimpleArtist
from tests.classes.linked_author import LinkedAuthor
from tests.classes.linked_post import LinkedPost


class TestQuery(TestCase):

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
        collection = Connection.get_collection(SimpleSong)
        collection.delete_many({})
        collection = Connection.get_collection(SimpleArtist)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedAuthor)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedPost)
        collection.delete_many({})

    def test_query_objects_from_database(self):
        song0 = SimpleSong(name='Long', year=2020, artist='Thao')
        song0.save()
        song1 = SimpleSong(name='Long', year=2020, artist='Thao')
        song1.save()
        songs = SimpleSong.find().exec()
        self.assertEqual(song0.name, songs[0].name)
        self.assertEqual(song0.year, songs[0].year)
        self.assertEqual(song0.artist, songs[0].artist)
        self.assertEqual(song0.id, songs[0].id)
        self.assertGreaterEqual(song0.created_at, songs[0].created_at)
        self.assertGreaterEqual(song0.updated_at, songs[0].updated_at)
        self.assertEqual(song0.deleted_at, songs[0].deleted_at)
        self.assertEqual(song1.name, songs[1].name)
        self.assertEqual(song1.year, songs[1].year)
        self.assertEqual(song1.artist, songs[1].artist)
        self.assertEqual(song1.id, songs[1].id)
        self.assertGreaterEqual(song1.created_at, songs[1].created_at)
        self.assertGreaterEqual(song1.updated_at, songs[1].updated_at)
        self.assertEqual(song1.deleted_at, songs[1].deleted_at)

    def test_query_object_from_database(self):
        song0 = SimpleSong(name='Long', year=2020, artist='Thao')
        song0.save()
        song1 = SimpleSong(name='Long', year=2020, artist='Thao')
        song1.save()
        song = SimpleSong.one().exec()
        self.assertEqual(song0.name, song.name)
        self.assertEqual(song0.year, song.year)
        self.assertEqual(song0.artist, song.artist)
        self.assertEqual(song0.id, song.id)
        self.assertGreaterEqual(song0.created_at, song.created_at)
        self.assertGreaterEqual(song0.updated_at, song.updated_at)
        self.assertEqual(song0.deleted_at, song.deleted_at)

    def test_query_object_with_id(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        result = SimpleSong.id(str(song.id)).exec()
        self.assertEqual(song.name, result.name)
        self.assertEqual(song.year, result.year)
        self.assertEqual(song.artist, result.artist)
        self.assertEqual(song.id, result.id)
        self.assertGreaterEqual(song.created_at, result.created_at)
        self.assertGreaterEqual(song.updated_at, result.updated_at)
        self.assertEqual(song.deleted_at, result.deleted_at)
