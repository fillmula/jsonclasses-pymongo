from unittest import TestCase
from jsonclasses_pymongo import connector


class TestDatabaseConnection(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        connector.connect('mongodb://localhost:27017/jsonclasses')

    def test_two_classes_share_same_database(self):
        self.assertIsNotNone(connector._database)
