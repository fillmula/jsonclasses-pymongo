from __future__ import annotations
from unittest import TestCase

from jsonclasses_pymongo import Connection
from tests.classes.simple_song import SimpleSong
from tests.classes.simple_artist import SimpleArtist
from tests.classes.linked_author import LinkedAuthor
from tests.classes.linked_post import LinkedPost
from tests.classes.linked_profile_user import LinkedProfile, LinkedUser
from tests.classes.linked_favorite import LinkedCourse, LinkedStudent


class TestDelete(TestCase):

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
        collection = Connection.get_collection(LinkedUser)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedProfile)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedStudent)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedCourse)
        collection.delete_many({})
        collection = Connection('linked').collection('linkedcoursesstudents'
                                                     'linkedstudentscourses')
        collection.delete_many({})

    def test_object_can_be_removed_from_database(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        collection = Connection.get_collection(SimpleSong)
        self.assertEqual(collection.count_documents({}), 1)
        song.delete()
        self.assertEqual(collection.count_documents({}), 0)
        self.assertEqual(song.is_deleted, True)

    def test_1l_1f_list_can_be_nullified(self):
        author = LinkedAuthor(name='A', posts=[
            LinkedPost(title='P1', content='C1'),
            LinkedPost(title='P2', content='C2')])
        author.save()
        collection = Connection.get_collection(LinkedAuthor)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedPost)
        self.assertEqual(collection.count_documents({}), 2)
        author.delete()
        for obj in collection.find():
            self.assertEqual(obj['authorId'], None)

    def test_1l_1f_instance_can_be_nullified(self):
        user = LinkedUser(name='crazy')
        profile = LinkedProfile(name='six')
        user.profile = profile
        user.save()
        collection = Connection.get_collection(LinkedUser)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedProfile)
        self.assertEqual(collection.count_documents({}), 1)
        user.delete()
        for obj in collection.find():
            self.assertEqual(obj['userId'], None)

    def test_many_many_can_be_nullified(self):
        course1 = LinkedCourse(name='C1')
        course2 = LinkedCourse(name='C2')
        student1 = LinkedStudent(name='S1')
        student2 = LinkedStudent(name='S2')
        course1.students = [student1, student2]
        course2.students = [student1, student2]
        course1.save() # this triggers save also for course2
        collname = 'linkedcoursesstudentslinkedstudentscourses'
        collection = Connection('linked').collection(collname)
        self.assertEqual(collection.count_documents({}), 4)
        course1.delete()
        self.assertEqual(collection.count_documents({}), 2)

    def test_1f_1l_cascade_delete(self):
        pass

    def test_1l_1f_cascade_delete(self):
        pass

    def test_1_many_cascade_delete(self):
        pass

    def test_many_1_cascade_delete(self):
        pass

    def test_many_many_cascade_delete(self):
        pass

    # def test_1f_1l_can_be_nullified(self):
    #     post = LinkedPost(title='P', content='C')
    #     author = LinkedAuthor(name='A')
    #     post.author = author
    #     post.save()
    #     collection = Connection.get_collection(LinkedPost)
    #     self.assertEqual(collection.count_documents({}), 1)
    #     collection = Connection.get_collection(LinkedAuthor)
    #     self.assertEqual(collection.count_documents({}), 1)
    #     post.delete()
