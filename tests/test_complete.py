from __future__ import annotations
from unittest import TestCase
from jsonclasses_pymongo import Connection
from tests.classes.simple_record import SimpleRecord, SimpleORecord
from tests.classes.linked_record import LinkedRecord, LinkedContent


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
        collection = Connection.get_collection(SimpleRecord)
        collection.delete_many({})
        collection = Connection.get_collection(SimpleORecord)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedRecord)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedContent)
        collection.delete_many({})

    def test_complete_completes_self(self):
        SimpleRecord(name='n', desc='d', age=1, score=5.0).save()
        result = SimpleRecord.one().omit(['age', 'score']).exec()
        self.assertEqual(result.is_partial, True)
        result.complete()
        self.assertEqual(result.age, 1)
        self.assertEqual(result.score, 5.0)
        self.assertEqual(result.is_partial, False)
        self.assertEqual(result.is_modified, False)
        self.assertEqual(result.modified_fields, ())

    def test_complete_also_fetches_local_ref_keys(self):
        r = LinkedRecord(name='n', desc='d', age=1, score=2).save()
        LinkedContent(record=r, title='t', paper='p', count=3).save()
        result = LinkedContent.one({'_omit': ['recordId', 'title', 'paper', 'count']}).exec()
        self.assertIsNone(result.record_id)
        result.complete()
        self.assertIsNotNone(result.record_id)

    def test_complete_ignores_edited_fields(self):
        SimpleRecord(name='n', desc='d', age=1, score=5.0).save()
        result = SimpleRecord.one().omit(['age', 'score']).exec()
        result.age = 100
        result.complete()
        self.assertEqual(result.age, 100)
        self.assertEqual(result.is_partial, False)
        self.assertEqual(result.is_modified, True)
        self.assertEqual(result.modified_fields, ('age',))
