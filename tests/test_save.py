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
        collection.delete_many({})
        collection = Connection.get_collection(LinkedStudent)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedCourse)
        collection.delete_many({})
        collection = Connection('linked').collection('linkedcoursesstudents'
                                                     'linkedstudentscourses')
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

    def test_set_local_key_to_none_is_saved(self):
        post = LinkedPost(title='P1', content='P2')
        author = LinkedAuthor(name='A1')
        post.author = author
        post.save()
        post.author_id = None
        post.save()
        collection = Connection.get_collection(LinkedPost)
        for item in collection.find({}):
            self.assertEqual(item['authorId'], None)

    def test_set_local_key_to_id_is_saved(self):
        post = LinkedPost(title='P1', content='P2')
        author = LinkedAuthor(name='A1')
        post.save()
        author.save()
        post.author_id = author.id
        post.save()
        collection = Connection.get_collection(LinkedPost)
        for item in collection.find({}):
            self.assertEqual(item['authorId'], ObjectId(author.id))

    def test_alter_local_key_is_saved(self):
        post = LinkedPost(title='P1', content='P2')
        a1 = LinkedAuthor(name='A1')
        post.author = a1
        post.save()
        a2 = LinkedAuthor(name='A2')
        post.author_id = a2.id
        post.save()
        collection = Connection.get_collection(LinkedPost)
        for item in collection.find({}):
            self.assertEqual(item['authorId'], ObjectId(a2.id))

    def test_local_key_from_param_is_saved(self):
        a1 = LinkedAuthor(name='A1')
        a1.save()
        post = LinkedPost(title='P1', content='P2', authorId=a1.id)
        post.save()
        collection = Connection.get_collection(LinkedPost)
        for item in collection.find({}):
            self.assertEqual(item['authorId'], ObjectId(a1.id))

    def test_local_key_from_set_is_altered_and_saved(self):
        a1 = LinkedAuthor(name='A1')
        a1.save()
        post = LinkedPost(title='P1', content='P2', authorId=a1.id)
        post.save()
        collection = Connection.get_collection(LinkedPost)
        for item in collection.find({}):
            self.assertEqual(item['authorId'], ObjectId(a1.id))
        a2 = LinkedAuthor(name='A2')
        post.set(authorId=a2.id)
        post.save()
        for item in collection.find({}):
            self.assertEqual(item['authorId'], ObjectId(a2.id))

    def test_1l_1f_object_unlink_is_saved(self):
        profile = LinkedProfile(name='p')
        user = LinkedUser(name='u')
        profile.user = user
        profile.save()
        profile.user = None
        profile.save()
        self.assertEqual(profile.is_new, False)
        self.assertEqual(profile.is_modified, False)
        self.assertEqual(profile.modified_fields, ())
        self.assertEqual(user.is_new, False)
        self.assertEqual(user.is_modified, False)
        self.assertEqual(user.modified_fields, ())
        collection = Connection.get_collection(LinkedProfile)
        for item in collection.find({}):
            self.assertEqual(item['userId'], None)

    def test_1f_1l_object_unlink_is_saved(self):
        user = LinkedUser(name='u')
        profile = LinkedProfile(name='p')
        user.profile = profile
        user.save()
        user.profile = None
        user.save()
        self.assertEqual(profile.is_new, False)
        self.assertEqual(profile.is_modified, False)
        self.assertEqual(profile.modified_fields, ())
        self.assertEqual(user.is_new, False)
        self.assertEqual(user.is_modified, False)
        self.assertEqual(user.modified_fields, ())
        collection = Connection.get_collection(LinkedProfile)
        for item in collection.find({}):
            self.assertEqual(item['userId'], None)

    def test_1_many_unlink_is_saved(self):
        author = LinkedAuthor(name='A')
        post = LinkedPost(title='T', content='C')
        author.posts.append(post)
        author.save()
        author.posts.remove(post)
        author.save()
        self.assertEqual(author.is_new, False)
        self.assertEqual(author.is_modified, False)
        self.assertEqual(author.modified_fields, ())
        self.assertEqual(post.is_new, False)
        self.assertEqual(post.is_modified, False)
        self.assertEqual(post.modified_fields, ())
        collection = Connection.get_collection(LinkedPost)
        for item in collection.find({}):
            self.assertEqual(item['authorId'], None)

    def test_many_1_unlink_is_saved(self):
        author = LinkedAuthor(name='A')
        post = LinkedPost(title='T', content='C')
        post.author = author
        post.save()
        post.author_id = None
        post.save()
        self.assertEqual(author.is_new, False)
        self.assertEqual(author.is_modified, False)
        self.assertEqual(author.modified_fields, ())
        self.assertEqual(post.is_new, False)
        self.assertEqual(post.is_modified, False)
        self.assertEqual(post.modified_fields, ())
        collection = Connection.get_collection(LinkedPost)
        for item in collection.find({}):
            self.assertEqual(item['authorId'], None)

    def test_many_many_unlink_is_saved(self):
        course1 = LinkedCourse(name='C1')
        course2 = LinkedCourse(name='C2')
        student1 = LinkedStudent(name='S1')
        student2 = LinkedStudent(name='S2')
        course1.students = [student1, student2]
        course2.students = [student1, student2]
        course1.save()
        course1.students.remove(student1)
        course1.save()
        collname = 'linkedcoursesstudentslinkedstudentscourses'
        collection = Connection('linked').collection(collname)
        self.assertEqual(collection.count_documents({}), 3)
