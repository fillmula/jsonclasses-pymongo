from __future__ import annotations
import unittest
from typing import List
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import MongoObject


@jsonclass
class Cycle(MongoObject):
    name: str


class TestMongoObjectLifeCycle(unittest.TestCase):

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

    def test_not_new_not_modified_after_fetch(self):
        cycle = Cycle(name='qq')
        cycle.save()
        cycle = Cycle.find_one({'name': 'qq'})
        self.assertEqual(cycle.is_new, False)
        self.assertEqual(cycle.is_modified, False)
        self.assertEqual(cycle.modified_fields, set())

    def test_change_marks_modified_after_fetch(self):
        cycle = Cycle(name='qq')
        cycle.save()
        cycle = Cycle.find_one({'name': 'qq'})
        cycle.name = 'alter'
        self.assertEqual(cycle.is_new, False)
        self.assertEqual(cycle.is_modified, True)
        self.assertEqual(cycle.modified_fields, {'name'})
