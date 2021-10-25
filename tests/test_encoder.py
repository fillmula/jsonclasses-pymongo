from __future__ import annotations
from jsonclasses_pymongo.connection import Connection
from unittest import TestCase
from typing import List, Dict, cast
from datetime import date, datetime
from bson import ObjectId
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo
from jsonclasses_pymongo.encoder import Encoder
from jsonclasses_pymongo.command import InsertOneCommand
from tests.classes.linked_account import LinkedAccount, LinkedBalance
from tests.classes.linked_author import LinkedAuthor
from tests.classes.linked_post import LinkedPost
from tests.classes.simple_calcuser import SimpleCalcUser


class TestEncoder(TestCase):

    def test_encode_str_into_str(self):
        @pymongo
        @jsonclass
        class SimpleEncodeStr:
            id: str = types.readonly.str.primary.mongoid.required
            val1: str
            val2: str
        simple_object = SimpleEncodeStr(val1='q', val2='e')
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'val1', 'val2']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['val1'], 'q')
        self.assertEqual(serialized['val2'], 'e')

    def test_encode_int_into_int(self):
        @pymongo
        @jsonclass
        class SimpleEncodeInt:
            id: str = types.readonly.str.primary.mongoid.required
            age: int
            length: int
        simple_object = SimpleEncodeInt(age=4, length=8)
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'age', 'length']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['age'], 4)
        self.assertEqual(serialized['length'], 8)

    def test_encode_float_into_float(self):
        @pymongo
        @jsonclass
        class SimpleEncodeFloat:
            id: str = types.readonly.str.primary.mongoid.required
            width: float
            length: float
        simple_object = SimpleEncodeFloat(width=4.5, length=8.5)
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'width', 'length']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['width'], 4.5)
        self.assertEqual(serialized['length'], 8.5)

    def test_encode_bool_into_bool(self):
        @pymongo
        @jsonclass
        class SimpleEncodeBool:
            id: str = types.readonly.str.primary.mongoid.required
            b1: bool
            b2: bool
        simple_object = SimpleEncodeBool(b1=True, b2=False)
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'b1', 'b2']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['b1'], True)
        self.assertEqual(serialized['b2'], False)

    def test_encode_date_into_datetime(self):
        @pymongo
        @jsonclass
        class SimpleEncodeDate:
            id: str = types.readonly.str.primary.mongoid.required
            d1: date = date(2012, 9, 15)
            d2: date = date(2020, 9, 14)
        simple_object = SimpleEncodeDate()
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'd1', 'd2']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['d1'], datetime(2012, 9, 15, 0, 0, 0))
        self.assertEqual(serialized['d2'], datetime(2020, 9, 14, 0, 0, 0))

    def test_encode_datetime_into_datetime(self):
        @pymongo
        @jsonclass
        class SimpleEncodeDatetime:
            id: str = types.readonly.str.primary.mongoid.required
            d1: date = datetime(2012, 9, 15, 0, 0, 0)
            d2: date = datetime(2020, 9, 14, 0, 0, 0)
        simple_object = SimpleEncodeDatetime()
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'd1', 'd2']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['d1'], datetime(2012, 9, 15, 0, 0, 0))
        self.assertEqual(serialized['d2'], datetime(2020, 9, 14, 0, 0, 0))

    def test_encode_embedded_list(self):
        @pymongo
        @jsonclass
        class SimpleEncodeScalarTypesList:
            id: str = types.readonly.str.primary.mongoid.required
            str_values: List[str]
            int_values: List[int]
            bool_values: List[bool]
        simple_object = SimpleEncodeScalarTypesList(str_values=['0', '1'],
                                                    int_values=[0, 1],
                                                    bool_values=[False, True])
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'strValues', 'intValues',
             'boolValues']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['strValues'], ['0', '1'])
        self.assertEqual(serialized['intValues'], [0, 1])
        self.assertEqual(serialized['boolValues'], [False, True])

    def test_encode_embedded_dict(self):
        @pymongo
        @jsonclass
        class SimpleEncodeScalarTypesDict:
            id: str = types.readonly.str.primary.mongoid.required
            str_values: Dict[str, str]
        simple_object = SimpleEncodeScalarTypesDict(
            str_values={'0': 'zero', '1': 'one'})
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'strValues']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['strValues'], {'0': 'zero', '1': 'one'})

    def test_encode_embedded_instance(self):
        @pymongo
        @jsonclass
        class SimpleEncodeEmbeddedInstanceAddress:
            id: str = types.readonly.str.primary.mongoid.required
            line1: str

        @pymongo
        @jsonclass
        class SimpleEncodeEmbeddedInstance:
            id: str = types.readonly.str.primary.mongoid.required
            address: SimpleEncodeEmbeddedInstanceAddress
        simple_object = SimpleEncodeEmbeddedInstance(
            address={'line1': 'Flam Road'})
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        self.assertEqual(len(commands), 1)
        command = commands[0]
        self.assertIs(command.collection,
                      Connection.get_collection(SimpleEncodeEmbeddedInstance))
        data = command.object
        address = data['address']
        self.assertIsInstance(address['_id'], ObjectId)
        self.assertEqual(address['line1'], 'Flam Road')

    def test_encode_foreign_key_instance(self):
        @pymongo
        @jsonclass
        class SimpleEncodeForeignKeyInstanceAddress:
            id: str = types.readonly.str.primary.mongoid.required
            line1: str
            owner: SimpleEncodeForeignKeyInstance = types.linkto.objof(
                'SimpleEncodeForeignKeyInstance')

        @pymongo
        @jsonclass
        class SimpleEncodeForeignKeyInstance:
            id: str = types.readonly.str.primary.mongoid.required
            address: SimpleEncodeForeignKeyInstanceAddress = types.objof(
                SimpleEncodeForeignKeyInstanceAddress).linkedby('owner')
        simple_object = SimpleEncodeForeignKeyInstance(
            address={'line1': 'Flam Road'})
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        self.assertEqual(len(commands), 2)
        address_data = commands[0].object
        owner_data = commands[1].object
        self.assertEqual(address_data['ownerId'], owner_data['_id'])

    def test_encode_local_key_instance(self):
        @pymongo
        @jsonclass
        class SimpleEncodeLocalKeyInstanceAddress:
            id: str = types.readonly.str.primary.mongoid.required
            line1: str
            owner: SimpleEncodeLocalKeyInstance = types.objof(
                'SimpleEncodeLocalKeyInstance').linkedby('address')

        @pymongo
        @jsonclass
        class SimpleEncodeLocalKeyInstance:
            id: str = types.readonly.str.primary.mongoid.required
            address: SimpleEncodeLocalKeyInstanceAddress = types.linkto.objof(SimpleEncodeLocalKeyInstanceAddress)
        simple_object = SimpleEncodeLocalKeyInstance(
            address={'line1': 'Flam Road'})
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        self.assertEqual(len(commands), 2)
        address_data = commands[0].object
        owner_data = commands[1].object
        self.assertEqual(owner_data['addressId'], address_data['_id'])

    def test_encode_embedded_instance_list(self):
        @pymongo
        @jsonclass
        class MediumEncodeEmbeddedInstanceAddress:
            id: str = types.readonly.str.primary.mongoid.required
            line1: str

        @pymongo
        @jsonclass
        class MediumEncodeEmbeddedInstance:
            id: str = types.readonly.str.primary.mongoid.required
            addresses: List[MediumEncodeEmbeddedInstanceAddress]
        medium_object = MediumEncodeEmbeddedInstance(
            addresses=[{'line1': 'Flam Road'}, {'line1': 'Plam Road'}])
        batch_command = Encoder().encode_root(medium_object)
        commands = batch_command.commands
        self.assertEqual(len(commands), 1)
        command = commands[0]
        self.assertIs(command.collection,
                      Connection.get_collection(MediumEncodeEmbeddedInstance))
        data = command.object
        addresses = data['addresses']
        self.assertEqual(len(addresses), 2)
        self.assertEqual(addresses[0]['line1'], 'Flam Road')
        self.assertEqual(addresses[1]['line1'], 'Plam Road')

    def test_encode_foreign_keys_instance_list(self):
        @pymongo
        @jsonclass
        class MediumEncodeForeignKeyInstanceAddress:
            id: str = types.readonly.str.primary.mongoid.required
            line1: str
            owner: MediumEncodeForeignKeyInstance = types.linkto.objof(
                'MediumEncodeForeignKeyInstance')

        @pymongo
        @jsonclass
        class MediumEncodeForeignKeyInstance:
            id: str = types.readonly.str.primary.mongoid.required
            addresses: List[MediumEncodeForeignKeyInstanceAddress] = types.listof(
                MediumEncodeForeignKeyInstanceAddress).linkedby('owner')
        simple_object = MediumEncodeForeignKeyInstance(
            addresses=[{'line1': 'Flam Road'}, {'line1': 'Klam Road'}])
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        self.assertEqual(len(commands), 3)
        address_0_data = commands[0].object
        address_1_data = commands[1].object
        owner_data = commands[2].object
        self.assertEqual(address_0_data['ownerId'], owner_data['_id'])
        self.assertEqual(address_1_data['ownerId'], owner_data['_id'])

    def test_encode_local_keys_instance_list(self):
        @pymongo
        @jsonclass
        class MediumEncodeLocalKeyInstanceAddress:
            id: str = types.readonly.str.primary.mongoid.required
            line1: str
            owner: MediumEncodeLocalKeyInstance = types.linkedby(
                'address').objof('SimpleEncodeLocalKeyInstance')

        @pymongo
        @jsonclass
        class MediumEncodeLocalKeyInstance:
            id: str = types.readonly.str.primary.mongoid.required
            addresses: List[MediumEncodeLocalKeyInstanceAddress] = types.listof(
                MediumEncodeLocalKeyInstanceAddress).linkto
        simple_object = MediumEncodeLocalKeyInstance(
            addresses=[{'line1': 'Flam Road'}, {'line1': 'Klam Road'}])
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        self.assertEqual(len(commands), 3)
        address_0_data = commands[0].object
        address_1_data = commands[1].object
        owner_data = commands[2].object
        self.assertEqual(owner_data['addressIds'], [
                         address_0_data['_id'], address_1_data['_id']])

    def test_encode_dict_keep_keys(self):
        @pymongo
        @jsonclass
        class MediumEncodeCamelizeDictKeys:
            id: str = types.readonly.str.primary.mongoid.required
            val: Dict[str, str] = types.dictof(types.str)
        simple_object = MediumEncodeCamelizeDictKeys(
            val={'keyOne': 'val_one', 'keyTwo': 'val_two'})
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        encoded_val = commands[0].object['val']
        self.assertEqual(
            encoded_val, {'keyOne': 'val_one', 'keyTwo': 'val_two'})

    def test_encoder_handle_many_to_many_with_linkedthru(self):
        @pymongo
        @jsonclass
        class DifficultEncodeLinkedThruA:
            id: str = types.readonly.str.primary.mongoid.required
            aval: str
            blinks: List[DifficultEncodeLinkedThruB] = types.listof(
                'DifficultEncodeLinkedThruB').linkedthru('alinks')

        @pymongo
        @jsonclass
        class DifficultEncodeLinkedThruB:
            id: str = types.readonly.str.primary.mongoid.required
            bval: str
            alinks: List[DifficultEncodeLinkedThruA] = types.listof(
                'DifficultEncodeLinkedThruA').linkedthru('blinks')
        instance_a = DifficultEncodeLinkedThruA(
            aval='A', blinks=[{'bval': 'B1'}, {'bval': 'B2'}])
        batch_command = Encoder().encode_root(instance_a)
        commands = batch_command.commands
        self.assertEqual(len(commands), 7)

    def test_encoder_ignores_calculated_fields(self):
        user = SimpleCalcUser(name='ABC', base_score=5)
        batch_command = Encoder().encode_root(user)
        self.assertEqual(len(batch_command.commands), 1)
        command = batch_command.commands[0]
        self.assertNotIn('firstName', command.object)
        self.assertNotIn('lastName', command.object)
        self.assertNotIn('score', command.object)
        self.assertIn('name', command.object)
        self.assertIn('baseScore', command.object)

    def test_encode_new_object_correctly_with_existing_objects_1f_1l(self):
        account = LinkedAccount(name='Account')
        balance = LinkedBalance(name='Balance')
        account.save()
        balance.account = account
        balance.save()

    def test_encode_new_object_correctly_with_existing_objects_1l_1f(self):
        account = LinkedAccount(name='Account')
        balance = LinkedBalance(name='Balance')
        balance.save()
        account.balance = balance
        account.save()

    def test_encode_new_object_correctly_with_existing_objects_1_many(self):
        author = LinkedAuthor(name='A')
        post = LinkedPost(title='P', content='P')
        author.save()
        post.author = author
        post.save()
