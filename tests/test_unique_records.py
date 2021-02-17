from __future__ import annotations
from typing import Optional
from unittest import IsolatedAsyncioTestCase
from jsonclasses import jsonclass, types, UniqueConstraintException
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
        self.assertRaises(UniqueConstraintException, b.save)

    async def test_saving_record_do_not_raise_for_null(self):
        @jsonclass(class_graph='this_is_quite_unique_1')
        class SpecialClassTwo(MongoObject):
            nama: Optional[str] = types.str.unique

        SpecialClassTwo.delete()
        a = SpecialClassTwo(nama=None)
        b = SpecialClassTwo(nama=None)
        a.save()
        b.save()
