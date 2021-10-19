from __future__ import annotations
from unittest import TestCase
from jsonclasses.excs import UniqueConstraintException
from jsonclasses_pymongo import Connection
from tests.classes.simple_person import SimplePerson
from tests.classes.simple_singer import SimpleSinger
from tests.classes.simple_album import SimpleAlbum


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
        collection = Connection.get_collection(SimpleAlbum)
        collection.delete_many({})

    def test_save_raises_if_violate_unique_rule(self):
        one = SimplePerson(name='Tsuan Tsiu')
        one.save()
        two = SimplePerson(name='Tsuan Tsiu')
        self.assertRaisesRegex(
            UniqueConstraintException,
            "value is not unique",
            two.save)

    def test_save_wont_raise_if_value_is_optional_and_is_null(self):
        one = SimpleSinger(name=None)
        one.save()
        two = SimpleSinger(name=None)
        two.save()

    def test_save_raises_if_all_values_violates_cunique_rule(self):
        one = SimpleAlbum(name='n', year=2021, note='n')
        one.save()
        two = SimpleAlbum(name='n', year=2021, note='n')
        self.assertRaisesRegex(UniqueConstraintException, "voilated unique compound index 'com'", two.save)

    def test_save_raises_if_part_of_values_violates_cunique_rule(self):
        one = SimpleAlbum(name='n', year=2021, note=None)
        one.save()
        two = SimpleAlbum(name='n', year=2021, note=None)
        self.assertRaisesRegex(UniqueConstraintException, "voilated unique compound index 'com'", two.save)

    def test_save_raises_if_one_value_violates_cunique_rule(self):
        one = SimpleAlbum(name='n')
        one.save()
        two = SimpleAlbum(name='n')
        self.assertRaisesRegex(UniqueConstraintException, "voilated unique compound index 'com'", two.save)

    def test_save_wont_raise_if_all_values_are_null(self):
        one = SimpleAlbum()
        one.save()
        two = SimpleAlbum()
        two.save()
