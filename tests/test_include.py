from __future__ import annotations
from unittest import TestCase
from jsonclasses_pymongo import Connection
from tests.classes.simple_song import SimpleSong
from tests.classes.simple_artist import SimpleArtist
from tests.classes.linked_author import LinkedAuthor
from tests.classes.linked_post import LinkedPost
from tests.classes.linked_profile_user import LinkedProfile, LinkedUser
from tests.classes.linked_favorite import LinkedCourse, LinkedStudent
from tests.classes.chained_user import (ChainedAddress, ChainedProfile,
                                        ChainedUser)


class TestSave(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        connection = Connection('simple')
        connection.set_url('mongodb://localhost:27017/simple')
        connection.connect()
        connection = Connection('linked')
        connection.set_url('mongodb://localhost:27017/linked')
        connection.connect()
        connection = Connection('chained')
        connection.set_url('mongodb://localhost:27017/chained')
        connection.connect()

    @classmethod
    def tearDownClass(cls) -> None:
        connection = Connection('simple')
        connection.disconnect()
        connection = Connection('linked')
        connection.disconnect()
        connection = Connection('chained')
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
        collection = Connection.get_collection(ChainedUser)
        collection.delete_many({})
        collection = Connection.get_collection(ChainedProfile)
        collection.delete_many({})
        collection = Connection.get_collection(ChainedAddress)
        collection.delete_many({})

    def test_1f_1l_ref_lookup_fetches_linked_object(self):
        user = LinkedUser(name='Teo Yeo')
        profile = LinkedProfile(name='Great City')
        user.profile = profile
        user.save()
        user = LinkedUser.id(user.id).include('profile').exec()
        self.assertEqual(user.profile.id, profile.id)
        self.assertEqual(user.profile.name, profile.name)

    def test_1l_1f_ref_lookup_fetches_linked_object(self):
        user = LinkedUser(name='Teo Yeo')
        profile = LinkedProfile(name='Great City')
        user.profile = profile
        user.save()
        profile = LinkedProfile.id(profile.id).include('user').exec()
        self.assertEqual(profile.user.id, user.id)
        self.assertEqual(profile.user.name, user.name)

    def test_1f_1l_find_lookup_fetches_linked_object(self):
        user1 = LinkedUser(name='Phou Neng')
        profile1 = LinkedProfile(name='Great City, Too')
        user1.profile = profile1
        user1.save()
        user2 = LinkedUser(name='Teo Yeo')
        profile2 = LinkedProfile(name='Great City')
        user2.profile = profile2
        user2.save()
        results = LinkedUser.find().include('profile').exec()
        self.assertEqual(results[0].id, user1.id)
        self.assertEqual(results[0].profile.id, profile1.id)
        self.assertEqual(results[1].id, user2.id)
        self.assertEqual(results[1].profile.id, profile2.id)

    def test_1l_1f_find_lookup_fetches_linked_object(self):
        user1 = LinkedUser(name='Phou Neng')
        profile1 = LinkedProfile(name='Great City, Too')
        user1.profile = profile1
        user1.save()
        user2 = LinkedUser(name='Teo Yeo')
        profile2 = LinkedProfile(name='Great City')
        user2.profile = profile2
        user2.save()
        results = LinkedProfile.find().include('user').exec()
        self.assertEqual(results[0].id, profile1.id)
        self.assertEqual(results[0].user.id, user1.id)
        self.assertEqual(results[1].id, profile2.id)
        self.assertEqual(results[1].user.id, user2.id)

    def test_1_many_ref_lookup_fetches_linked_objects(self):
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
        results = LinkedAuthor.find() \
                              .include('posts',
                                       LinkedPost.find(title={'$regex': 'B'}))\
                              .exec()
        self.assertEqual(len(results), 2)
        self.assertEqual(len(results[0].posts), 3)
        self.assertEqual(len(results[1].posts), 3)
        self.assertEqual(results[0].posts[0].title, 'B1')
        self.assertEqual(results[0].posts[1].title, 'B2')
        self.assertEqual(results[0].posts[2].title, 'B3')
        self.assertEqual(results[1].posts[0].title, 'B1')
        self.assertEqual(results[1].posts[1].title, 'B2')
        self.assertEqual(results[1].posts[2].title, 'B3')

    def test_many_1_ref_lookup_fetches_linked_object(self):
        author = LinkedAuthor(name='A1')
        post1 = LinkedPost(title='P1', content='A')
        post2 = LinkedPost(title='P2', content='A')
        post3 = LinkedPost(title='P3', content='A')
        post4 = LinkedPost(title='B1', content='A')
        post5 = LinkedPost(title='B2', content='A')
        post6 = LinkedPost(title='B3', content='A')
        author.posts = [post1, post2, post3, post4, post5, post6]
        author.save()
        author = LinkedAuthor(name='A2')
        post1 = LinkedPost(title='P1', content='B')
        post2 = LinkedPost(title='P2', content='B')
        post3 = LinkedPost(title='P3', content='B')
        post4 = LinkedPost(title='B1', content='B')
        post5 = LinkedPost(title='B2', content='B')
        post6 = LinkedPost(title='B3', content='B')
        author.posts = [post1, post2, post3, post4, post5, post6]
        author.save()
        results = LinkedPost.find(title='P1').include('author').exec()
        self.assertEqual(results[0].author.name, 'A1')
        self.assertEqual(results[1].author.name, 'A2')

    def test_many_many_ref_lookup_fetches_linked_objects(self):
        student1 = LinkedStudent(name='S1')
        student2 = LinkedStudent(name='S2')
        course1 = LinkedCourse(name='C1')
        course2 = LinkedCourse(name='C2')
        student1.courses = [course1, course2]
        student2.courses = [course1, course2]
        student1.save()
        students = LinkedStudent.find().include('courses').exec()
        self.assertEqual(len(students), 2)
        self.assertEqual(len(students[0].courses), 2)
        self.assertEqual(len(students[1].courses), 2)
        self.assertEqual(students[0].id, student2.id)
        self.assertEqual(students[1].id, student1.id)
        self.assertEqual(students[0].courses[0].id, course2.id)
        self.assertEqual(students[0].courses[1].id, course1.id)
        self.assertEqual(students[1].courses[0].id, course2.id)
        self.assertEqual(students[1].courses[1].id, course1.id)

    def test_many_many_ref_lookup_can_be_filtered(self):
        student1 = LinkedStudent(name='S1')
        student2 = LinkedStudent(name='S2')
        course1 = LinkedCourse(name='C1')
        course2 = LinkedCourse(name='C2')
        student1.courses = [course1, course2]
        student2.courses = [course1, course2]
        student1.save()
        students = LinkedStudent.find().include('courses', LinkedCourse.find(name='C1')).exec()
        self.assertEqual(len(students), 2)
        self.assertEqual(len(students[0].courses), 1)
        self.assertEqual(len(students[1].courses), 1)
        self.assertEqual(students[0].courses[0].name, course1.name)
        self.assertEqual(students[1].courses[0].name, course1.name)

    def test_1_1_ref_can_be_chained(self):
        u = ChainedUser(name='U', address={'name': 'A'}, profile={'name': 'P'})
        u.save()
        p = ChainedProfile.id(u.profile.id).include(
            'user', ChainedUser.linked().include('address')).exec()
        self.assertEqual(p.id, u.profile.id)
        self.assertEqual(p.user.id, u.id)
        self.assertEqual(p.user.address.id, u.address.id)

    def test_1_many_ref_uses_unique_objects(self):
        post1 = LinkedPost(title='P1', content='A')
        post2 = LinkedPost(title='P2', content='A')
        author = LinkedAuthor(name='A1', posts=[post1, post2])
        author.save()
        posts = LinkedPost.find().include('author').exec()
        p1 = posts[0]
        p2 = posts[1]
        self.assertIs(p1.author, p2.author)
        p1.author.name = 'New Name'
        p1.save()
        self.assertEqual(p2.author.name, 'New Name')

    def test_many_many_ref_uses_unique_objects(self):
        student1 = LinkedStudent(name='S1')
        student2 = LinkedStudent(name='S2')
        course1 = LinkedCourse(name='C1')
        course2 = LinkedCourse(name='C2')
        student1.courses = [course1, course2]
        student2.courses = [course1, course2]
        student1.save()
        students = LinkedStudent.find().include('courses', LinkedCourse.find(name='C1')).exec()
        s1 = students[0]
        s2 = students[1]
        self.assertIs(s1.courses[0], s2.courses[0])

    def test_fetched_objects_are_unmodified_1f_1l(self):
        user = LinkedUser(name='Bo Hang')
        profile = LinkedProfile(name='Ko Leng')
        user.profile = profile
        user.save()
        profile = LinkedProfile.id(profile.id).include('user').exec()
        self.assertEqual(profile.is_new, False)
        self.assertEqual(profile.is_modified, False)
        self.assertEqual(profile.modified_fields, ())
        self.assertEqual(profile.user.is_new, False)
        self.assertEqual(profile.user.is_modified, False)
        self.assertEqual(profile.user.modified_fields, ())

    def test_fetched_objects_are_unmodified_1l_1f(self):
        user = LinkedUser(name='Bo Hang')
        profile = LinkedProfile(name='Ko Leng')
        user.profile = profile
        user.save()
        user = LinkedUser.id(user.id).include('profile').exec()
        self.assertEqual(user.is_new, False)
        self.assertEqual(user.is_modified, False)
        self.assertEqual(user.modified_fields, ())
        self.assertEqual(user.profile.is_new, False)
        self.assertEqual(user.profile.is_modified, False)
        self.assertEqual(user.profile.modified_fields, ())

    def test_fetched_objects_are_unmodified_1_many(self):
        author = LinkedAuthor(name='Me')
        post1 = LinkedPost(title='P1', content='A')
        post2 = LinkedPost(title='P2', content='A')
        author.posts = [post1, post2]
        author.save()
        authors = LinkedAuthor.find().include('posts').exec()
        a = authors[0]
        p1 = a.posts[0]
        p2 = a.posts[1]
        self.assertEqual(a.is_new, False)
        self.assertEqual(a.is_modified, False)
        self.assertEqual(a.modified_fields, ())
        self.assertEqual(p1.is_new, False)
        self.assertEqual(p1.is_modified, False)
        self.assertEqual(p1.modified_fields, ())
        self.assertEqual(p2.is_new, False)
        self.assertEqual(p2.is_modified, False)
        self.assertEqual(p2.modified_fields, ())

    def test_fetched_objects_are_unmodified_many_1(self):
        author = LinkedAuthor(name='Me')
        post1 = LinkedPost(title='P1', content='A')
        post2 = LinkedPost(title='P2', content='A')
        author.posts = [post1, post2]
        author.save()
        posts = LinkedPost.find().include('author').exec()
        self.assertEqual(posts[0].is_new, False)
        self.assertEqual(posts[0].is_modified, False)
        self.assertEqual(posts[0].modified_fields, ())
        self.assertEqual(posts[1].is_new, False)
        self.assertEqual(posts[1].is_modified, False)
        self.assertEqual(posts[1].modified_fields, ())
        self.assertEqual(posts[0].author.is_new, False)
        self.assertEqual(posts[0].author.is_modified, False)
        self.assertEqual(posts[0].author.modified_fields, ())
        self.assertEqual(posts[0].author, posts[1].author)

    def test_fetched_objects_are_unmodified_many_many(self):
        student1 = LinkedStudent(name='S1')
        student2 = LinkedStudent(name='S2')
        course1 = LinkedCourse(name='C1')
        course2 = LinkedCourse(name='C2')
        student1.courses = [course1, course2]
        student2.courses = [course1, course2]
        student1.save()
        students = LinkedStudent.find().include('courses').exec()
        self.assertEqual(students[0].is_new, False)
        self.assertEqual(students[0].is_modified, False)
        self.assertEqual(students[0].modified_fields, ())
        self.assertEqual(students[1].is_new, False)
        self.assertEqual(students[1].is_modified, False)
        self.assertEqual(students[1].modified_fields, ())
        self.assertEqual(students[0].courses[0].is_new, False)
        self.assertEqual(students[0].courses[0].is_modified, False)
        self.assertEqual(students[0].courses[0].modified_fields, ())
        self.assertEqual(students[0].courses[1].is_new, False)
        self.assertEqual(students[0].courses[1].is_modified, False)
        self.assertEqual(students[0].courses[1].modified_fields, ())
        self.assertEqual(students[1].courses[0].is_new, False)
        self.assertEqual(students[1].courses[0].is_modified, False)
        self.assertEqual(students[1].courses[0].modified_fields, ())
        self.assertEqual(students[1].courses[1].is_new, False)
        self.assertEqual(students[1].courses[1].is_modified, False)
        self.assertEqual(students[1].courses[1].modified_fields, ())
