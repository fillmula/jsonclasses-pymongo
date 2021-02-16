from __future__ import annotations
from unittest import IsolatedAsyncioTestCase
from jsonclasses import jsonclass, types, UniqueFieldException
from jsonclasses_pymongo import MongoObject, connector


class TestUniqueRecordSave(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        connector.connect('mongodb://localhost:27017/jsonclasses')

    async def test_saving_record_raises_if_voilate_unique_rule(self):
        @jsonclass(class_graph='this_is_quite_unique_1')
        class SpecialClass(MongoObject):
            name: str = types.str.unique.required

        SpecialClass.delete()
        a = SpecialClass(name='special')
        b = SpecialClass(name='special')
        a.save()
        self.assertRaises(UniqueFieldException, b.save)
