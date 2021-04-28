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
        for item in collection.find():
            print(item)
            # self.assertEqual(item['name'], 'Ti')
            # self.assertIsInstance(item['_id'], ObjectId)
            # self.assertIsInstance(item['updatedAt'], datetime)
            # self.assertIsInstance(item['createdAt'], datetime)
            # self.assertEqual(set(item.keys()),
            #                  {'_id', 'name', 'updatedAt',
            #                   'createdAt', 'deletedAt'})
        collection = Connection.get_collection(LinkedPost)
        self.assertEqual(collection.count_documents({}), 2)
        for item in collection.find():
            print(item)
            # self.assertEqual(item['name'], 'Kaosai')
            # self.assertEqual(item['gender'], 1)
            # self.assertIsInstance(item['_id'], ObjectId)
            # self.assertIsInstance(item['updatedAt'], datetime)
            # self.assertIsInstance(item['createdAt'], datetime)
            # self.assertEqual(set(item.keys()),
            #                  {'_id', 'name', 'gender', 'updatedAt',
            #                   'createdAt', 'deletedAt'})

# @jsonclass
# class Product(MongoObject):
#     name: str
#     customers: List[Customer] = types.listof('Customer').linkedthru('products')


# @jsonclass
# class Customer(MongoObject):
#     name: str
#     products: List[Product] = types.listof('Product').linkedthru('customers')


# class TestMongoObjectSave(IsolatedAsyncioTestCase):

#     async def test_save_multiple_instances_to_db(self):
#
#         @jsonclass
#

#         returned_author = await TestAuthor.find(author.id)
#         self.assertEqual(returned_author.name, author.name)
#         returned_author_with_posts = ((await TestAuthor.find(author.id))
#                                                     .include('posts'))
#         self.assertEqual(len(returned_author_with_posts.posts), 2)
#         returned_post_0 = await TestPost.find(author.posts[0].id)
#         self.assertEqual(returned_post_0.title, author.posts[0].title)
#         returned_post_0_with_author = await TestPost.find(
#             author.posts[0].id).include('author')
#         self.assertEqual(returned_post_0_with_author.author.name, author.name)
