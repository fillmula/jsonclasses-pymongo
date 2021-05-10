from __future__ import annotations
from datetime import datetime
from unittest import TestCase
from bson.objectid import ObjectId
from jsonclasses_pymongo import Connection
from tests.classes.simple_song import SimpleSong
from tests.classes.simple_artist import SimpleArtist
from tests.classes.linked_author import LinkedAuthor
from tests.classes.linked_post import LinkedPost
from tests.classes.linked_profile_user import LinkedProfile, LinkedUser
from tests.classes.linked_favorite import LinkedCourse, LinkedStudent


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
        collection = Connection.get_collection(LinkedProfile)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedUser)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedStudent)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedCourse)
        collection.delete_many({})
        collection = Connection('linked').collection('linkedcoursesstudents'
                                                     'linkedstudentscourses')
        collection.delete_many({})

    def test_1_1_ref_lookup_example(self):
        user = LinkedUser(name='Teo Yeo')
        profile = LinkedProfile(name='Great City')
        user.profile = profile
        user.save()
        user = LinkedUser(name='Phou Neng')
        profile = LinkedProfile(name='Great City Tooa')
        user.profile = profile
        user.save()
        collection = Connection.get_collection(LinkedUser)
        cursor = collection.aggregate([
            {
                '$match': {
                    'name': 'Teo Yeo'
                }
            },
            {
                '$lookup': {
                    'from': "linkedprofiles",
                    'localField': "_id",
                    'foreignField': "userId",
                    'as': "profile"
                }
            },
            {
                '$unwind': '$profile'
            }
        ])
        for item in cursor:
            #print(item)
            pass


    def test_1_many_ref_lookup_example(self):
        author = LinkedAuthor(name='Kai Nang Piang Tshung')
        post1 = LinkedPost(title='P1', content='A')
        post2 = LinkedPost(title='P2', content='A')
        post3 = LinkedPost(title='P3', content='A')
        post4 = LinkedPost(title='B1', content='A')
        post5 = LinkedPost(title='B2', content='A')
        post6 = LinkedPost(title='B3', content='A')
        author.posts = [post1, post2, post3, post4, post5, post6]
        author.save()
        author = LinkedAuthor(name='Khui Tsia Koi Tsuang Kai Low Rider')
        post1 = LinkedPost(title='P1', content='B')
        post2 = LinkedPost(title='P2', content='B')
        post3 = LinkedPost(title='P3', content='B')
        post4 = LinkedPost(title='B1', content='B')
        post5 = LinkedPost(title='B2', content='B')
        post6 = LinkedPost(title='B3', content='B')
        author.posts = [post1, post2, post3, post4, post5, post6]
        author.save()

        collection = Connection.get_collection(LinkedAuthor)
        cursor = collection.aggregate([
            {
                '$lookup': {
                    'from': "linkedposts",
                    'as': "posts",
                    'let': {'authorId': '$_id'},
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$and': [
                                        {'$eq': ['$authorId', '$$authorId']}
                                    ]
                                },
                                'title': {'$regex': 'P'}
                            }
                        }
                    ]
                }
            }
        ])
        for item in cursor:
            #print(item)
            pass
