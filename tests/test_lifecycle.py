from __future__ import annotations
from unittest import IsolatedAsyncioTestCase
from jsonclasses import jsonclass
from jsonclasses_pymongo import MongoObject, connector


@jsonclass
class Cycle(MongoObject):
    name: str


class TestMongoObjectLifeCycle(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        connector.connect('mongodb://localhost:27017/jsonclasses')

    def test_new_on_create(self):
        cycle = Cycle()
        self.assertEqual(cycle.is_new, True)
        self.assertEqual(cycle.is_modified, False)
        self.assertEqual(cycle.modified_fields, set())
        cycle.name = '4'
        self.assertEqual(cycle.is_new, True)
        self.assertEqual(cycle.is_modified, False)
        self.assertEqual(cycle.modified_fields, set())

    def test_not_new_not_modified_after_save(self):
        cycle = Cycle(name='cycle')
        cycle.save()
        self.assertEqual(cycle.is_new, False)
        self.assertEqual(cycle.is_modified, False)
        self.assertEqual(cycle.modified_fields, set())

    def test_change_marks_modified_after_save(self):
        cycle = Cycle(name='cycle')
        cycle.save()
        cycle.name = 'alter'
        self.assertEqual(cycle.is_new, False)
        self.assertEqual(cycle.is_modified, True)
        self.assertEqual(cycle.modified_fields, {'name'})

    async def test_not_new_not_modified_after_fetch(self):
        cycle = Cycle(name='qq')
        cycle.save()
        cycle = await Cycle.find(name='qq').first
        self.assertEqual(cycle.is_new, False)
        self.assertEqual(cycle.is_modified, False)
        self.assertEqual(cycle.modified_fields, set())

    async def test_change_marks_modified_after_fetch(self):
        cycle = Cycle(name='qq')
        cycle.save()
        cycle = await Cycle.find(name='qq').first
        cycle.name = 'alter'
        self.assertEqual(cycle.is_new, False)
        self.assertEqual(cycle.is_modified, True)
        self.assertEqual(cycle.modified_fields, {'name'})
