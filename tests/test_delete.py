from __future__ import annotations
from unittest import TestCase
from jsonclasses.exceptions import DeletionDeniedException
from jsonclasses_pymongo import Connection
from tests.classes.simple_song import SimpleSong
from tests.classes.simple_artist import SimpleArtist
from tests.classes.linked_author import LinkedAuthor
from tests.classes.linked_post import LinkedPost
from tests.classes.linked_profile_user import (LinkedProfile, LinkedUser,
                                               LinkedCProfile, LinkedDUser,
                                               LinkedDProfile, LinkedCUser)
from tests.classes.linked_favorite import LinkedCourse, LinkedStudent
from tests.classes.linked_order import (LinkedOrder, LinkedBuyer, LinkedCOrder,
                                        LinkedCBuyer)
from tests.classes.linked_account import LinkedAccount, LinkedBalance
from tests.classes.linked_bomb import LinkedSoldier, LinkedBomb
from tests.classes.linked_notebook import (LinkedNote, LinkedNotebook,
                                           LinkedRNote, LinkedRNotebook)
from tests.classes.linked_share import LinkedCompany, LinkedOwner


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
        collection = Connection.get_collection(LinkedOrder)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedBuyer)
        collection.delete_many({})
        collection.delete_many({})
        collection = Connection.get_collection(LinkedCOrder)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedCBuyer)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedAccount)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedBalance)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedBomb)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedSoldier)
        collection.delete_many({})
        collection = Connection('linked').collection('linkedbombssoldiers'
                                                     'linkedsoldiersbombs')
        collection.delete_many({})
        collection = Connection.get_collection(LinkedCProfile)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedDUser)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedDProfile)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedCUser)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedNote)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedNotebook)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedRNote)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedRNotebook)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedCompany)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedOwner)
        collection.delete_many({})
        collection = Connection('linked').collection('linkedcompaniesowners'
                                                     'linkedownerscompanies')
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
        account = LinkedAccount(name='A', balance=LinkedBalance(name='B'))
        account.save()
        collection = Connection.get_collection(LinkedAccount)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedBalance)
        self.assertEqual(collection.count_documents({}), 1)
        account.delete()
        collection = Connection.get_collection(LinkedAccount)
        self.assertEqual(collection.count_documents({}), 0)
        collection = Connection.get_collection(LinkedBalance)
        self.assertEqual(collection.count_documents({}), 0)

    def test_1l_1f_cascade_delete(self):
        balance = LinkedBalance(name='A', account=LinkedAccount(name='B'))
        balance.save()
        collection = Connection.get_collection(LinkedAccount)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedBalance)
        self.assertEqual(collection.count_documents({}), 1)
        balance.delete()
        collection = Connection.get_collection(LinkedAccount)
        self.assertEqual(collection.count_documents({}), 0)
        collection = Connection.get_collection(LinkedBalance)
        self.assertEqual(collection.count_documents({}), 0)

    def test_1_many_cascade_delete(self):
        buyer = LinkedBuyer(name='B')
        order1 = LinkedOrder(name='O1')
        order2 = LinkedOrder(name='O2')
        buyer.orders = [order1, order2]
        buyer.save()
        collection = Connection.get_collection(LinkedOrder)
        self.assertEqual(collection.count_documents({}), 2)
        buyer.delete()
        self.assertEqual(collection.count_documents({}), 0)

    def test_many_1_cascade_delete(self):
        buyer = LinkedCBuyer(name='B')
        order1 = LinkedCOrder(name='O1')
        order2 = LinkedCOrder(name='O2')
        buyer.orders = [order1, order2]
        buyer.save()
        collection = Connection.get_collection(LinkedCOrder)
        self.assertEqual(collection.count_documents({}), 2)
        order1.delete()
        self.assertEqual(collection.count_documents({}), 0)
        collection = Connection.get_collection(LinkedCBuyer)
        self.assertEqual(collection.count_documents({}), 0)

    def test_many_many_cascade_delete(self):
        soldier1 = LinkedSoldier(name='S1')
        soldier2 = LinkedSoldier(name='S2')
        bomb1 = LinkedBomb(name='B1')
        bomb2 = LinkedBomb(name='B2')
        soldier1.bombs = [bomb1, bomb2]
        soldier2.bombs = [bomb1, bomb2]
        soldier1.save()
        soldier2.save()
        collection = Connection.get_collection(LinkedSoldier)
        self.assertEqual(collection.count_documents({}), 2)
        collection = Connection.get_collection(LinkedBomb)
        self.assertEqual(collection.count_documents({}), 2)
        collection = Connection('linked').collection('linkedbombssoldiers'
                                                     'linkedsoldiersbombs')
        self.assertEqual(collection.count_documents({}), 4)
        soldier1.delete()
        collection = Connection.get_collection(LinkedSoldier)
        self.assertEqual(collection.count_documents({}), 0)
        collection = Connection.get_collection(LinkedBomb)
        self.assertEqual(collection.count_documents({}), 0)
        collection = Connection('linked').collection('linkedbombssoldiers'
                                                     'linkedsoldiersbombs')
        self.assertEqual(collection.count_documents({}), 0)

    def test_1l_1f_denies_deletion(self):
        user = LinkedDUser(name='crazy')
        profile = LinkedCProfile(name='six')
        user.profile = profile
        user.save()
        collection = Connection.get_collection(LinkedDUser)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedCProfile)
        self.assertEqual(collection.count_documents({}), 1)
        self.assertRaises(DeletionDeniedException, user.delete)
        collection = Connection.get_collection(LinkedDUser)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedCProfile)
        self.assertEqual(collection.count_documents({}), 1)

    def test_1l_1f_allows_deletion(self):
        user = LinkedDUser(name='crazy')
        user.save()
        collection = Connection.get_collection(LinkedDUser)
        self.assertEqual(collection.count_documents({}), 1)
        user.delete()
        collection = Connection.get_collection(LinkedDUser)
        self.assertEqual(collection.count_documents({}), 0)

    def test_1f_1l_denies_deletion(self):
        user = LinkedCUser(name='crazy')
        profile = LinkedDProfile(name='six')
        user.profile = profile
        user.save()
        collection = Connection.get_collection(LinkedCUser)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedDProfile)
        self.assertEqual(collection.count_documents({}), 1)
        self.assertRaises(DeletionDeniedException, profile.delete)
        collection = Connection.get_collection(LinkedCUser)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedDProfile)
        self.assertEqual(collection.count_documents({}), 1)

    def test1f_1l_allows_deletion(self):
        profile = LinkedDProfile(name='crazy')
        profile.save()
        collection = Connection.get_collection(LinkedDProfile)
        self.assertEqual(collection.count_documents({}), 1)
        profile.delete()
        collection = Connection.get_collection(LinkedDProfile)
        self.assertEqual(collection.count_documents({}), 0)

    def test_1_many_denies_deletion(self):
        notebook = LinkedNotebook(name='N',
                                  notes=[{'name': 'A'}, {'name': 'B'}])
        notebook.save()
        collection = Connection.get_collection(LinkedNotebook)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedNote)
        self.assertEqual(collection.count_documents({}), 2)
        self.assertRaises(DeletionDeniedException, notebook.delete)
        collection = Connection.get_collection(LinkedNotebook)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedNote)
        self.assertEqual(collection.count_documents({}), 2)

    def test_1_many_allows_deletion(self):
        notebook = LinkedNotebook(name='N', notes=[])
        notebook.save()
        collection = Connection.get_collection(LinkedNotebook)
        self.assertEqual(collection.count_documents({}), 1)
        notebook.delete()
        collection = Connection.get_collection(LinkedNotebook)
        self.assertEqual(collection.count_documents({}), 0)

    def test_many_1_denies_deletion(self):
        notebook = LinkedRNotebook(name='N',
                                  notes=[{'name': 'A'}, {'name': 'B'}])
        notebook.save()
        collection = Connection.get_collection(LinkedRNotebook)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedRNote)
        self.assertEqual(collection.count_documents({}), 2)
        self.assertRaises(DeletionDeniedException, notebook.notes[0].delete)
        collection = Connection.get_collection(LinkedRNotebook)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedRNote)
        self.assertEqual(collection.count_documents({}), 2)

    def test_many_1_allows_deletion(self):
        note = LinkedRNote(name='N')
        note.save()
        collection = Connection.get_collection(LinkedRNote)
        self.assertEqual(collection.count_documents({}), 1)
        note.delete()
        collection = Connection.get_collection(LinkedRNote)
        self.assertEqual(collection.count_documents({}), 0)

    def test_many_1_reverse_deny_has_nullify_effect(self):
        notebook = LinkedRNotebook(name='N',
                                   notes=[{'name': 'A'}, {'name': 'B'}])
        notebook.save()
        collection = Connection.get_collection(LinkedRNotebook)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedRNote)
        self.assertEqual(collection.count_documents({}), 2)
        notebook.delete()
        collection = Connection.get_collection(LinkedRNotebook)
        self.assertEqual(collection.count_documents({}), 0)
        collection = Connection.get_collection(LinkedRNote)
        self.assertEqual(collection.count_documents({}), 2)
        for item in collection.find({}):
            self.assertEqual(item['notebookId'], None)

    def test_many_many_denies_deletion(self):
        c1 = LinkedCompany(name='C1')
        c2 = LinkedCompany(name='C2')
        o1 = LinkedOwner(name='O1')
        o2 = LinkedOwner(name='O2')
        c1.owners = [o1, o2]
        c2.owners = [o1, o2]
        o1.save()
        collection = Connection.get_collection(LinkedCompany)
        self.assertEqual(collection.count_documents({}), 2)
        collection = Connection.get_collection(LinkedOwner)
        self.assertEqual(collection.count_documents({}), 2)
        collection = Connection('linked').collection('linkedcompaniesowners'
                                                     'linkedownerscompanies')
        self.assertEqual(collection.count_documents({}), 4)
        self.assertRaises(DeletionDeniedException, o1.delete)
        collection = Connection.get_collection(LinkedCompany)
        self.assertEqual(collection.count_documents({}), 2)
        collection = Connection.get_collection(LinkedOwner)
        self.assertEqual(collection.count_documents({}), 2)
        collection = Connection('linked').collection('linkedcompaniesowners'
                                                     'linkedownerscompanies')
        self.assertEqual(collection.count_documents({}), 4)

    def test_many_many_allows_deletion(self):
        owner = LinkedOwner(name='OK')
        owner.save()
        collection = Connection.get_collection(LinkedOwner)
        self.assertEqual(collection.count_documents({}), 1)
        owner.delete()
        collection = Connection.get_collection(LinkedOwner)
        self.assertEqual(collection.count_documents({}), 0)

    def test_many_many_cascade_deny_triggers_partial_deletion(self):
        c1 = LinkedCompany(name='C1')
        c2 = LinkedCompany(name='C2')
        o1 = LinkedOwner(name='O1')
        o2 = LinkedOwner(name='O2')
        c1.owners = [o1, o2]
        c2.owners = [o1, o2]
        c1.save()
        c1.delete()
        collection = Connection.get_collection(LinkedCompany)
        self.assertEqual(collection.count_documents({}), 1)
        collection = Connection.get_collection(LinkedOwner)
        self.assertEqual(collection.count_documents({}), 2)
        collection = Connection('linked').collection('linkedcompaniesowners'
                                                     'linkedownerscompanies')
        self.assertEqual(collection.count_documents({}), 2)
