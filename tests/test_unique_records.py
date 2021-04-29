from __future__ import annotations
from typing import Optional
from unittest import TestCase
from jsonclasses.exceptions import UniqueConstraintException
from jsonclasses_pymongo import Connection
from tests.classes.simple_person import SimplePerson
from tests.classes.simple_singer import SimpleSinger


class TestUniqueRecord(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        connection = Connection('simple')
        connection.set_url('mongodb://localhost:27017/simple')
        connection.connect()

    @classmethod
    def tearDownClass(cls) -> None:
        connection = Connection('simple')
        connection.disconnect()

    def setUp(self) -> None:
        collection = Connection.get_collection(SimplePerson)
        collection.delete_many({})
        collection = Connection.get_collection(SimpleSinger)
        collection.delete_many({})

    def test_save_raises_if_violate_unique_rule(self):
        one = SimplePerson(name='Tsuan Tsiu')
        one.save()
        two = SimplePerson(name='Tsuan Tsiu')
        self.assertRaisesRegex(
            UniqueConstraintException,
            "Value 'Tsuan Tsiu' at 'name' is not unique.",
            two.save)

    def test_save_wont_raise_if_value_is_optional_and_is_null(self):
        one = SimpleSinger(name=None)
        one.save()
        two = SimpleSinger(name=None)
        two.save()
        one = SimplePerson(name='Tsuan Tsiu')
        one.save()
        two = SimplePerson(name='Tsuan Tsiu')
        self.assertRaisesRegex(
            UniqueConstraintException,
            "Value 'Tsuan Tsiu' at 'name' is not unique.",
            two.save)
