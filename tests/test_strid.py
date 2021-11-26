from __future__ import annotations
from datetime import datetime
from unittest import TestCase
from bson.objectid import ObjectId
from jsonclasses_pymongo.connection import Connection
from tests.classes.simple_song import SimpleSong
from tests.classes.simple_artist import SimpleArtist
from tests.classes.linked_author import LinkedAuthor
from tests.classes.linked_post import LinkedPost
from tests.classes.linked_profile_user import LinkedProfile, LinkedUser
from tests.classes.linked_favorite import LinkedCourse, LinkedStudent
from tests.classes.simple_record import SimpleRecord
from tests.classes.linked_album import LinkedAlbum, LinkedArtist
from tests.classes.linked_song import LinkedSinger, LinkedSong
from tests.classes.simple_strid import SimpleStrId


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

    def test_strid_can_be_saved(self):
        obj = SimpleStrId(id='myid', val='myval')
        obj.save()

    def test_strid_can_be_fetched(self):
        obj = SimpleStrId(id='myid', val='myval')
        obj.save()
        result = SimpleStrId.id('myid').exec()
        self.assertEqual(result.id, 'myid')

    def test_strid_can_be_updated(self):
        obj = SimpleStrId(id='myid', val='myval')
        obj.id = 'newid'
        obj.save()
        result = SimpleStrId.id('newid').exec()
        self.assertEqual(result.id, 'newid')
        result.id = '2id'
        result.save()
        results = SimpleStrId.find().exec()
        print(results)
