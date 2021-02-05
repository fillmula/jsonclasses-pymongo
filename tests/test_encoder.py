from __future__ import annotations
from unittest import TestCase
from typing import List, Dict, cast
from datetime import date, datetime
from bson import ObjectId
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import MongoObject
from jsonclasses_pymongo.encoder import Encoder
from jsonclasses_pymongo.command import InsertOneCommand


class TestEncoder(TestCase):

    def test_encode_str_into_str(self):
        @jsonclass
        class SimpleEncodeStr(MongoObject):
            val1: str
            val2: str
        simple_object = SimpleEncodeStr(val1='q', val2='e')
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'createdAt', 'updatedAt', 'val1', 'val2', 'deletedAt']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['val1'], 'q')
        self.assertEqual(serialized['val2'], 'e')

    def test_encode_int_into_int(self):
        @jsonclass
        class SimpleEncodeInt(MongoObject):
            age: int
            length: int
        simple_object = SimpleEncodeInt(age=4, length=8)
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'createdAt', 'updatedAt', 'age', 'length', 'deletedAt']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['age'], 4)
        self.assertEqual(serialized['length'], 8)

    def test_encode_float_into_float(self):
        @jsonclass
        class SimpleEncodeFloat(MongoObject):
            width: float
            length: float
        simple_object = SimpleEncodeFloat(width=4.5, length=8.5)
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'createdAt', 'updatedAt', 'width', 'length', 'deletedAt']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['width'], 4.5)
        self.assertEqual(serialized['length'], 8.5)

    def test_encode_bool_into_bool(self):
        @jsonclass
        class SimpleEncodeBool(MongoObject):
            b1: bool
            b2: bool
        simple_object = SimpleEncodeBool(b1=True, b2=False)
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'createdAt', 'updatedAt', 'b1', 'b2', 'deletedAt']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['b1'], True)
        self.assertEqual(serialized['b2'], False)

    def test_encode_date_into_datetime(self):
        @jsonclass
        class SimpleEncodeDate(MongoObject):
            d1: date = date(2012, 9, 15)
            d2: date = date(2020, 9, 14)
        simple_object = SimpleEncodeDate()
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'createdAt', 'updatedAt', 'd1', 'd2', 'deletedAt']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['d1'], datetime(2012, 9, 15, 0, 0, 0))
        self.assertEqual(serialized['d2'], datetime(2020, 9, 14, 0, 0, 0))

    def test_encode_datetime_into_datetime(self):
        @jsonclass
        class SimpleEncodeDatetime(MongoObject):
            d1: date = datetime(2012, 9, 15, 0, 0, 0)
            d2: date = datetime(2020, 9, 14, 0, 0, 0)
        simple_object = SimpleEncodeDatetime()
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'createdAt', 'updatedAt', 'd1', 'd2', 'deletedAt']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['d1'], datetime(2012, 9, 15, 0, 0, 0))
        self.assertEqual(serialized['d2'], datetime(2020, 9, 14, 0, 0, 0))

    def test_encode_embedded_list(self):
        @jsonclass
        class SimpleEncodeScalarTypesList(MongoObject):
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
            ['_id', 'createdAt', 'updatedAt', 'strValues', 'intValues',
             'boolValues', 'deletedAt']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['strValues'], ['0', '1'])
        self.assertEqual(serialized['intValues'], [0, 1])
        self.assertEqual(serialized['boolValues'], [False, True])

    def test_encode_embedded_dict(self):
        @jsonclass
        class SimpleEncodeScalarTypesDict(MongoObject):
            str_values: Dict[str, str]
        simple_object = SimpleEncodeScalarTypesDict(
            str_values={'0': 'zero', '1': 'one'})
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'createdAt', 'updatedAt', 'strValues', 'deletedAt']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['strValues'], {'0': 'zero', '1': 'one'})

    def test_encode_embedded_shape(self):
        @jsonclass
        class SimpleEncodeScalarTypesShape(MongoObject):
            vals: Dict[str, str] = types.shape({
                '0': str,
                '1': int
            })
        simple_object = SimpleEncodeScalarTypesShape(
            vals={'0': 'zero', '1': 1})
        batch_command = Encoder().encode_root(simple_object)
        insert_command = cast(InsertOneCommand, batch_command.commands[0])
        serialized = insert_command.object
        self.assertEqual(set(serialized.keys()), set(
            ['_id', 'createdAt', 'updatedAt', 'vals', 'deletedAt']))
        self.assertIsInstance(serialized['_id'], ObjectId)
        self.assertEqual(serialized['vals'], {'0': 'zero', '1': 1})

    def test_encode_embedded_instance(self):
        @jsonclass
        class SimpleEncodeEmbeddedInstanceAddress(MongoObject):
            line1: str

        @jsonclass
        class SimpleEncodeEmbeddedInstance(MongoObject):
            address: SimpleEncodeEmbeddedInstanceAddress
        simple_object = SimpleEncodeEmbeddedInstance(
            address={'line1': 'Flam Road'})
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        self.assertEqual(len(commands), 1)
        command = commands[0]
        self.assertIs(command.collection,
                      SimpleEncodeEmbeddedInstance.collection())
        data = command.object
        address = data['address']
        self.assertIsInstance(address['_id'], ObjectId)
        self.assertEqual(address['line1'], 'Flam Road')

    def test_encode_foreign_key_instance(self):
        @jsonclass
        class SimpleEncodeForeignKeyInstanceAddress(MongoObject):
            line1: str
            owner: SimpleEncodeForeignKeyInstance = types.linkto.instanceof(
                'SimpleEncodeForeignKeyInstance')

        @jsonclass
        class SimpleEncodeForeignKeyInstance(MongoObject):
            address: SimpleEncodeForeignKeyInstanceAddress = types.instanceof(
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
        @jsonclass
        class SimpleEncodeLocalKeyInstanceAddress(MongoObject):
            line1: str
            owner: SimpleEncodeLocalKeyInstance = types.instanceof(
                'SimpleEncodeLocalKeyInstance').linkedby('address')

        @jsonclass
        class SimpleEncodeLocalKeyInstance(MongoObject):
            address: SimpleEncodeLocalKeyInstanceAddress = types.linkto.instanceof(SimpleEncodeLocalKeyInstanceAddress)
        simple_object = SimpleEncodeLocalKeyInstance(
            address={'line1': 'Flam Road'})
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        self.assertEqual(len(commands), 2)
        address_data = commands[0].object
        owner_data = commands[1].object
        self.assertEqual(owner_data['addressId'], address_data['_id'])

    def test_encode_embedded_instance_list(self):
        @jsonclass
        class MediumEncodeEmbeddedInstanceAddress(MongoObject):
            line1: str

        @jsonclass
        class MediumEncodeEmbeddedInstance(MongoObject):
            addresses: List[MediumEncodeEmbeddedInstanceAddress]
        medium_object = MediumEncodeEmbeddedInstance(
            addresses=[{'line1': 'Flam Road'}, {'line1': 'Plam Road'}])
        batch_command = Encoder().encode_root(medium_object)
        commands = batch_command.commands
        self.assertEqual(len(commands), 1)
        command = commands[0]
        self.assertIs(command.collection,
                      MediumEncodeEmbeddedInstance.collection())
        data = command.object
        addresses = data['addresses']
        self.assertEqual(len(addresses), 2)
        self.assertEqual(addresses[0]['line1'], 'Flam Road')
        self.assertEqual(addresses[1]['line1'], 'Plam Road')

    def test_encode_foreign_keys_instance_list(self):
        @jsonclass
        class MediumEncodeForeignKeyInstanceAddress(MongoObject):
            line1: str
            owner: MediumEncodeForeignKeyInstance = types.linkto.instanceof(
                'MediumEncodeForeignKeyInstance')

        @jsonclass
        class MediumEncodeForeignKeyInstance(MongoObject):
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
        @jsonclass
        class MediumEncodeLocalKeyInstanceAddress(MongoObject):
            line1: str
            owner: MediumEncodeLocalKeyInstance = types.linkedby(
                'address').instanceof('SimpleEncodeLocalKeyInstance')

        @jsonclass
        class MediumEncodeLocalKeyInstance(MongoObject):
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
        self.assertEqual(owner_data['addressesIds'], [
                         address_0_data['_id'], address_1_data['_id']])

    def test_encode_dict_camelize_keys(self):
        @jsonclass
        class MediumEncodeCamelizeDictKeys(MongoObject):
            val: Dict[str, str] = types.dictof(types.str)
        simple_object = MediumEncodeCamelizeDictKeys(
            val={'key_one': 'val_one', 'key_two': 'val_two'})
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        encoded_val = commands[0].object['val']
        self.assertEqual(
            encoded_val, {'keyOne': 'val_one', 'keyTwo': 'val_two'})

    def test_encode_dict_do_not_camelize_keys(self):
        @jsonclass(camelize_db_keys=False)
        class MediumEncodeDoNotCamelizeDictKeys(MongoObject):
            val: Dict[str, str] = types.dictof(types.str)
        simple_object = MediumEncodeDoNotCamelizeDictKeys(
            val={'key_one': 'val_one', 'key_two': 'val_two'})
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        encoded_val = commands[0].object['val']
        self.assertEqual(
            encoded_val, {'key_one': 'val_one', 'key_two': 'val_two'})

    def test_encode_shape_camelize_keys(self):
        @jsonclass
        class MediumEncodeCamelizeShapeKeys(MongoObject):
            val: Dict[str, str] = types.shape({
                'key_one': types.str,
                'key_two': types.str
            })
        simple_object = MediumEncodeCamelizeShapeKeys(
            val={'key_one': 'val_one', 'key_two': 'val_two'})
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        encoded_val = commands[0].object['val']
        self.assertEqual(
            encoded_val, {'keyOne': 'val_one', 'keyTwo': 'val_two'})

    def test_encode_shape_do_not_camelize_keys(self):
        @jsonclass(camelize_db_keys=False)
        class MediumEncodeDoNotCamelizeShapeKeys(MongoObject):
            val: Dict[str, str] = types.shape({
                'key_one': types.str,
                'key_two': types.str
            })
        simple_object = MediumEncodeDoNotCamelizeShapeKeys(
            val={'key_one': 'val_one', 'key_two': 'val_two'})
        batch_command = Encoder().encode_root(simple_object)
        commands = batch_command.commands
        encoded_val = commands[0].object['val']
        self.assertEqual(
            encoded_val, {'key_one': 'val_one', 'key_two': 'val_two'})

    def test_encoder_handle_many_to_many_with_linkedthru(self):
        @jsonclass
        class DifficultEncodeLinkedThruA(MongoObject):
            aval: str
            blinks: List[DifficultEncodeLinkedThruB] = types.listof(
                'DifficultEncodeLinkedThruB').linkedthru('alinks')

        @jsonclass
        class DifficultEncodeLinkedThruB(MongoObject):
            bval: str
            alinks: List[DifficultEncodeLinkedThruA] = types.listof(
                'DifficultEncodeLinkedThruA').linkedthru('blinks')
        instance_a = DifficultEncodeLinkedThruA(
            aval='A', blinks=[{'bval': 'B1'}, {'bval': 'B2'}])
        batch_command = Encoder().encode_root(instance_a)
        commands = batch_command.commands
        self.assertEqual(len(commands), 7)
