from __future__ import annotations
from datetime import datetime
from unittest import TestCase
from bson.objectid import ObjectId
from jsonclasses_pymongo import Connection
from tests.classes.simple_song import SimpleSong
from tests.classes.simple_artist import SimpleArtist
from tests.classes.linked_author import LinkedAuthor
from tests.classes.linked_post import LinkedPost


class TestSave(TestCase):

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

    def test_object_is_saved_into_database(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        collection = Connection.get_collection(SimpleSong)
        self.assertEqual(collection.count_documents({}), 1)
        for item in collection.find():
            self.assertEqual(item['name'], 'Long')
            self.assertEqual(item['year'], 2020)
            self.assertEqual(item['artist'], 'Thao')
            self.assertIsInstance(item['_id'], ObjectId)
            self.assertIsInstance(item['updatedAt'], datetime)
            self.assertIsInstance(item['createdAt'], datetime)
            self.assertEqual(set(item.keys()),
                             {'_id', 'name', 'year', 'artist', 'updatedAt',
                              'createdAt', 'deletedAt'})

    def test_object_with_enum_is_saved_into_database(self):
        artist = SimpleArtist(name='Kaosai', gender='MALE')
        artist.save()
        collection = Connection.get_collection(SimpleArtist)
        self.assertEqual(collection.count_documents({}), 1)
        for item in collection.find():
            self.assertEqual(item['name'], 'Kaosai')
            self.assertEqual(item['gender'], 1)
            self.assertIsInstance(item['_id'], ObjectId)
            self.assertIsInstance(item['updatedAt'], datetime)
            self.assertIsInstance(item['createdAt'], datetime)
            self.assertEqual(set(item.keys()),
                             {'_id', 'name', 'gender', 'updatedAt',
                              'createdAt', 'deletedAt'})

    def test_linked_objects_are_saved_at_the_same_time(self):
        input = {
            'name': 'Ti',
            'posts': [
                {
                    'title': 'Bo Lo Iong',
                    'content': 'Pieng Iu'
                },
                {
                    'title': 'Bo Lo Iong',
                    'content': 'Pieng Iu'
                }
            ]
        }
        author = LinkedAuthor(**input)
        author.save()
        collection = Connection.get_collection(LinkedAuthor)
        self.assertEqual(collection.count_documents({}), 1)
        oid = ObjectId()
        for item in collection.find():
            self.assertEqual(item['name'], 'Ti')
            self.assertIsInstance(item['_id'], ObjectId)
            oid = item['_id']
            self.assertIsInstance(item['updatedAt'], datetime)
            self.assertIsInstance(item['createdAt'], datetime)
            self.assertEqual(set(item.keys()),
                             {'_id', 'name', 'updatedAt',
                              'createdAt', 'deletedAt'})
        collection = Connection.get_collection(LinkedPost)
        self.assertEqual(collection.count_documents({}), 2)
        for item in collection.find():
            self.assertEqual(item['title'], 'Bo Lo Iong')
            self.assertEqual(item['content'], 'Pieng Iu')
            self.assertEqual(item['authorId'], oid)
            self.assertIsInstance(item['_id'], ObjectId)
            self.assertIsInstance(item['updatedAt'], datetime)
            self.assertIsInstance(item['createdAt'], datetime)
            self.assertEqual(set(item.keys()),
                             {'_id', 'title', 'content', 'authorId',
                              'updatedAt', 'createdAt', 'deletedAt'})

    def test_object_is_not_new_after_saved(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        self.assertEqual(song.is_new, True)
        self.assertEqual(song.is_modified, False)
        self.assertEqual(song.modified_fields, ())
        song.save()
        self.assertEqual(song.is_new, False)
        self.assertEqual(song.is_modified, False)
        self.assertEqual(song.modified_fields, ())
        song.name = 'Lao'
        self.assertEqual(song.is_new, False)
        self.assertEqual(song.is_modified, True)
        self.assertEqual(song.modified_fields, ('name',))

    def test_update_can_update_database(self):
        song = SimpleSong(name='Tsong Khang', year=2020, artist='Tsao')
        song.save()
        collection = Connection.get_collection(SimpleSong)
        self.assertEqual(collection.count_documents({}), 1)
        song.name = 'Lao'
        song.save()
        self.assertEqual(collection.count_documents({}), 1)
        for item in collection.find():
            self.assertEqual(item['name'], 'Lao')
            self.assertEqual(item['year'], 2020)
            self.assertEqual(item['artist'], 'Tsao')
            self.assertIsInstance(item['_id'], ObjectId)
            self.assertIsInstance(item['updatedAt'], datetime)
            self.assertIsInstance(item['createdAt'], datetime)
            self.assertEqual(set(item.keys()),
                             {'_id', 'name', 'year', 'artist', 'updatedAt',
                              'createdAt', 'deletedAt'})

    def test_linked_object_is_not_new_after_saved(self):
        input = {
            'name': 'Ti',
            'posts': [
                {
                    'title': 'Bo Lo Iong',
                    'content': 'Pieng Iu'
                },
                {
                    'title': 'Bo Lo Iong',
                    'content': 'Pieng Iu'
                }
            ]
        }
        author = LinkedAuthor(**input)
        self.assertEqual(author.is_new, True)
        self.assertEqual(author.posts[0].is_new, True)
        self.assertEqual(author.posts[1].is_new, True)
        author.save()
        self.assertEqual(author.is_new, False)
        self.assertEqual(author.posts[0].is_new, False)
        self.assertEqual(author.posts[1].is_new, False)

# @jsonclass
# class Product(MongoObject):
#     name: str
#     customers: List[Customer] = types.listof('Customer').linkedthru('products')


# @jsonclass
# class Customer(MongoObject):
#     name: str
#     products: List[Product] = types.listof('Product').linkedthru('customers')
