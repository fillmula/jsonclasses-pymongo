from __future__ import annotations
import unittest
from typing import List
from dotenv import load_dotenv
from datetime import date, datetime
from bson import ObjectId
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import MongoObject
from jsonclasses_pymongo.encoder import Encoder

class TestEncoder(unittest.TestCase):

  def test_encode_str_into_str(self):
    @jsonclass
    class SimpleEncodeStr(MongoObject):
      val1: str
      val2: str
    simple_object = SimpleEncodeStr(val1='q', val2='e')
    serialized = Encoder().encode_root(simple_object)[0][0]
    self.assertEqual(set(serialized.keys()), set(['_id', 'createdAt', 'updatedAt', 'val1', 'val2']))
    self.assertIsInstance(serialized['_id'], ObjectId)
    self.assertEqual(serialized['val1'], 'q')
    self.assertEqual(serialized['val2'], 'e')

  def test_encode_int_into_int(self):
    @jsonclass
    class SimpleEncodeInt(MongoObject):
      age: int
      length: int
    simple_object = SimpleEncodeInt(age=4, length=8)
    serialized = Encoder().encode_root(simple_object)[0][0]
    self.assertEqual(set(serialized.keys()), set(['_id', 'createdAt', 'updatedAt', 'age', 'length']))
    self.assertIsInstance(serialized['_id'], ObjectId)
    self.assertEqual(serialized['age'], 4)
    self.assertEqual(serialized['length'], 8)

  def test_encode_float_into_float(self):
    @jsonclass
    class SimpleEncodeFloat(MongoObject):
      width: float
      length: float
    simple_object = SimpleEncodeFloat(width=4.5, length=8.5)
    serialized = Encoder().encode_root(simple_object)[0][0]
    self.assertEqual(set(serialized.keys()), set(['_id', 'createdAt', 'updatedAt', 'width', 'length']))
    self.assertIsInstance(serialized['_id'], ObjectId)
    self.assertEqual(serialized['width'], 4.5)
    self.assertEqual(serialized['length'], 8.5)

  def test_encode_bool_into_bool(self):
    @jsonclass
    class SimpleEncodeBool(MongoObject):
      b1: bool
      b2: bool
    simple_object = SimpleEncodeBool(b1=True, b2=False)
    serialized = Encoder().encode_root(simple_object)[0][0]
    self.assertEqual(set(serialized.keys()), set(['_id', 'createdAt', 'updatedAt', 'b1', 'b2']))
    self.assertIsInstance(serialized['_id'], ObjectId)
    self.assertEqual(serialized['b1'], True)
    self.assertEqual(serialized['b2'], False)

  def test_encode_date_into_datetime(self):
    @jsonclass
    class SimpleEncodeDate(MongoObject):
      d1: date = date(2012, 9, 15)
      d2: date = date(2020, 9, 14)
    simple_object = SimpleEncodeDate()
    serialized = Encoder().encode_root(simple_object)[0][0]
    self.assertEqual(set(serialized.keys()), set(['_id', 'createdAt', 'updatedAt', 'd1', 'd2']))
    self.assertIsInstance(serialized['_id'], ObjectId)
    self.assertEqual(serialized['d1'], datetime(2012, 9, 15, 0, 0, 0))
    self.assertEqual(serialized['d2'], datetime(2020, 9, 14, 0, 0, 0))

  def test_encode_datetime_into_datetime(self):
    @jsonclass
    class SimpleEncodeDatetime(MongoObject):
      d1: date = datetime(2012, 9, 15, 0, 0, 0)
      d2: date = datetime(2020, 9, 14, 0, 0, 0)
    simple_object = SimpleEncodeDatetime()
    serialized = Encoder().encode_root(simple_object)[0][0]
    self.assertEqual(set(serialized.keys()), set(['_id', 'createdAt', 'updatedAt', 'd1', 'd2']))
    self.assertIsInstance(serialized['_id'], ObjectId)
    self.assertEqual(serialized['d1'], datetime(2012, 9, 15, 0, 0, 0))
    self.assertEqual(serialized['d2'], datetime(2020, 9, 14, 0, 0, 0))
