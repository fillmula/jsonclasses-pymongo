from __future__ import annotations
from datetime import date, datetime
from math import ceil
from unittest import TestCase
from statistics import mean
from bson.objectid import ObjectId
from jsonclasses_pymongo import Connection
from tests.classes.simple_animal import SimpleAnimal
from tests.classes.simple_datetime import SimpleDatetime
from tests.classes.simple_score import SimpleScore
from tests.classes.simple_song import SimpleSong
from tests.classes.simple_artist import SimpleArtist
from tests.classes.linked_author import LinkedAuthor
from tests.classes.linked_post import LinkedPost
from tests.classes.simple_date import SimpleDate
from tests.classes.simple_persona import SimplePersona
from tests.classes.simple_sex import SimpleSex, Gender
from tests.classes.simple_str import SimpleString


class TestQuery(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        connection = Connection('simple')
        connection.set_url('mongodb://localhost:27017/simple')
        connection.connect()
        connection = Connection('linked')
        connection.set_url('mongodb://localhost:27017/linked')
        connection.connect()

    @classmethod
    def tearDownClass(cls) -> None:
        connection = Connection('simple')
        connection.disconnect()
        connection = Connection('linked')
        connection.disconnect()

    def setUp(self) -> None:
        collection = Connection.get_collection(SimpleSong)
        collection.delete_many({})
        collection = Connection.get_collection(SimpleArtist)
        collection.delete_many({})
        collection = Connection.get_collection(SimpleDate)
        collection.delete_many({})
        collection = Connection.get_collection(SimpleDatetime)
        collection.delete_many({})
        collection = Connection.get_collection(SimplePersona)
        collection.delete_many({})
        collection = Connection.get_collection(SimpleSex)
        collection.delete_many({})
        collection = Connection.get_collection(SimpleScore)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedAuthor)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedPost)
        collection.delete_many({})
        collection = Connection.get_collection(SimpleAnimal)
        collection.delete_many({})
        collection = Connection.get_collection(SimpleString)
        collection.delete_many({})

    def test_query_objects_from_database(self):
        song0 = SimpleSong(name='Long', year=2020, artist='Thao')
        song0.save()
        song1 = SimpleSong(name='Long', year=2020, artist='Thao')
        song1.save()
        songs = SimpleSong.find().exec()
        self.assertEqual(song0.name, songs[0].name)
        self.assertEqual(song0.year, songs[0].year)
        self.assertEqual(song0.artist, songs[0].artist)
        self.assertEqual(song0.id, songs[0].id)
        self.assertGreaterEqual(song0.created_at, songs[0].created_at)
        self.assertGreaterEqual(song0.updated_at, songs[0].updated_at)
        self.assertEqual(song1.name, songs[1].name)
        self.assertEqual(song1.year, songs[1].year)
        self.assertEqual(song1.artist, songs[1].artist)
        self.assertEqual(song1.id, songs[1].id)
        self.assertGreaterEqual(song1.created_at, songs[1].created_at)
        self.assertGreaterEqual(song1.updated_at, songs[1].updated_at)

    def test_query_object_from_database(self):
        song0 = SimpleSong(name='Long', year=2020, artist='Thao')
        song0.save()
        song1 = SimpleSong(name='Long', year=2020, artist='Thao')
        song1.save()
        song = SimpleSong.one().exec()
        self.assertEqual(song0.name, song.name)
        self.assertEqual(song0.year, song.year)
        self.assertEqual(song0.artist, song.artist)
        self.assertEqual(song0.id, song.id)
        self.assertGreaterEqual(song0.created_at, song.created_at)
        self.assertGreaterEqual(song0.updated_at, song.updated_at)

    def test_query_object_with_id(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        result = SimpleSong.id(song.id).exec()
        self.assertEqual(song.name, result.name)
        self.assertEqual(song.year, result.year)
        self.assertEqual(song.artist, result.artist)
        self.assertEqual(song.id, result.id)
        self.assertGreaterEqual(song.created_at, result.created_at)
        self.assertGreaterEqual(song.updated_at, result.updated_at)

    def test_query_object_with_int(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        result = SimpleSong.find(year=2020).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].year, 2020)

    def test_query_object_with_int_string(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        result = SimpleSong.find('year=2020').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].year, 2020)

    def test_query_object_with_int_object(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        result = SimpleSong.find(year={'_gt': 2010}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].year, 2020)
        result = SimpleSong.find(year={'_gt': 2030}).exec()
        self.assertEqual(len(result), 0)

    def test_query_object_with_int_object_string(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        result = SimpleSong.find('year[_gt]=2010').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].year, 2020)
        result = SimpleSong.find('year[_gt]=2030').exec()
        self.assertEqual(len(result), 0)

    def test_query_object_with_str(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        result = SimpleSong.find(name='Long').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Long')

    def test_query_object_with_str_str(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        result = SimpleSong.find('name=Long').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Long')

    def test_query_object_with_prefix_str_object(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_prefix': 'Lo'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Long')

    def test_query_object_with_prefix_str_object_str(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_prefix]=Lo').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Long')

    def test_query_object_with_contains_str_object(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_contains': 'on'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Long')

    def test_query_object_with_contains_str_object_str(self):
        song = SimpleSong(name='Long', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_contains]=on').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Long')

    def test_query_object_with_suffix_str_object(self):
        song = SimpleSong(name='Ben', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_suffix': 'en'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Ben')

    def test_query_object_with_suffix_str_object_str(self):
        song = SimpleSong(name='Ben', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_suffix]=en').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Ben')

    def test_query_object_with_match_str_object(self):
        song = SimpleSong(name='Ben', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_match': 'B'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Ben')

    def test_query_object_with_match_str_object_str(self):
        song = SimpleSong(name='Ben', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_match]=B').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Ben')

    def test_query_object_with_containsi_str_object(self):
        song = SimpleSong(name='Ben', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_containsi': 'b'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Ben')

    def test_query_object_with_containsi_str_object_str(self):
        song = SimpleSong(name='Ben', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_containsi]=b').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Ben')

    def test_query_object_with_prefixi_str_object(self):
        song = SimpleSong(name='Ben', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_prefixi': 'b'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Ben')

    def test_query_object_with_prefixi_str_object_str(self):
        song = SimpleSong(name='Ben', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_prefixi]=b').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Ben')

    def test_query_object_with_suffixi_str_object(self):
        song = SimpleSong(name='BenS', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_suffixi': 's'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'BenS')

    def test_query_object_with_suffixi_str_object_str(self):
        song = SimpleSong(name='BenS', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_suffixi]=s').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'BenS')

    def test_query_object_with_matchi_str_object(self):
        song = SimpleSong(name='Lucy', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_matchi': 'C'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Lucy')

    def test_query_object_with_matchi_str_object_str(self):
        song = SimpleSong(name='Lucy', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_matchi]=C').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Lucy')

    def test_query_object_with_equal_str_object(self):
        song = SimpleSong(name='Lucy', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_equal': 'Lieng'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Lieng')

    def test_query_object_with_equal_str_object_str(self):
        song = SimpleSong(name='Lucy', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_equal]=Lieng').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Lieng')

    def test_query_object_with_not_str_object(self):
        song = SimpleSong(name='Lucy', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_not': 'Lieng'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Lucy')

    def test_query_object_with_not_str_object_str(self):
        song = SimpleSong(name='Lucy', year=2020, artist='Thao')
        song.save()
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_not]=Lieng').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Lucy')

    def test_query_object_with_field_exists_str_object(self):
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find(name={'_field_exists': 'True'}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Lieng')

    def test_query_object_with_field_exists_str_object_str(self):
        song2 = SimpleSong(name='Lieng', year=2020, artist='Lieng')
        song2.save()
        result = SimpleSong.find('name[_field_exists]=True').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Lieng')

    def test_query_object_with_bool(self):
        animal = SimpleAnimal(name='tiger', can_fly=False)
        animal.save()
        animal2 = SimpleAnimal(name='bird', can_fly=True)
        animal2.save()
        result = SimpleAnimal.find(can_fly=False).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'tiger')

    def test_query_object_with_bool_str(self):
        animal = SimpleAnimal(name='tiger', can_fly=False)
        animal.save()
        animal2 = SimpleAnimal(name='bird', can_fly=True)
        animal2.save()
        result = SimpleAnimal.find(can_fly='false').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'tiger')

    def test_query_object_with_bool_object(self):
        animal = SimpleAnimal(name='tiger', can_fly=False)
        animal.save()
        animal2 = SimpleAnimal(name='bird', can_fly=True)
        animal2.save()
        result = SimpleAnimal.find(can_fly={'_eq': "False"}).exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'tiger')

    def test_query_object_with_bool_object_str(self):
        animal = SimpleAnimal(name='tiger', can_fly=False)
        animal.save()
        animal2 = SimpleAnimal(name='bird', can_fly=True)
        animal2.save()
        result = SimpleAnimal.find('canFly[_eq]=false').exec()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'tiger')

    def test_query_object_with_date(self):
        d = SimpleDate(represents=date(2010, 7, 7))
        d.save()
        results = SimpleDate.find(represents=date(2010, 7, 7)).exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].represents, d.represents)

    def test_query_object_with_date_string(self):
        d = SimpleDate(represents=date(2010, 7, 7))
        d.save()
        results = SimpleDate.find('represents=2010-07-07').exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].represents, d.represents)

    def test_query_object_with_date_object(self):
        d = SimpleDate(represents=date(2010, 7, 7))
        d.save()
        results = SimpleDate.find(represents={'_eq': '2010-07-07'}).exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].represents, d.represents)

    def test_query_object_with_date_object_string(self):
        d = SimpleDate(represents=date(2010, 7, 7))
        d.save()
        results = SimpleDate.find('represents[_eq]=2010-07-07').exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].represents, d.represents)

    def test_query_object_with_datetime(self):
        d = SimpleDatetime(represents=datetime(2021, 6, 6, 12, 30))
        d.save()
        results = SimpleDatetime.find(represents=datetime(2021, 6, 6, 12, 30)).exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].represents, d.represents)

    def test_query_object_with_datetime_string(self):
        d = SimpleDatetime(represents=datetime(2021, 6, 6, 12, 30, 0))
        d.save()
        results = SimpleDatetime.find('represents=2021-06-06 12:30:00').exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].represents, d.represents)

    def test_query_object_with_datetime_object(self):
        d = SimpleDatetime(represents=datetime(2021, 6, 6, 12, 30, 0))
        d.save()
        results = SimpleDatetime.find(represents={'_eq': '2021-06-06 12:30:00'}).exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].represents, d.represents)

    def test_query_object_with_date_object_string(self):
        d = SimpleDate(represents=datetime(2021, 6, 6, 12, 30, 0))
        d.save()
        results = SimpleDate.find('represents[_eq]=2021-06-06 12:30:00').exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].represents, d.represents)

    def test_query_dict_in_list(self):
        p = SimplePersona(items=[{'a': 1, 'b': 2}, {'c': 3}])
        p.save()
        results = SimplePersona.find().exec()

    def test_query_enum_with_enum(self):
        d = SimpleSex(gender='MALE')
        d.save()
        results = SimpleSex.find(gender=Gender.MALE).exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].gender, d.gender)

    def test_query_enum_with_enum_name(self):
        d = SimpleSex(gender='MALE')
        d.save()
        results = SimpleSex.find(gender='MALE').exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].gender, d.gender)

    def test_query_enum_with_lowercase_enum_name(self):
        d = SimpleSex(gender='MALE')
        d.save()
        results = SimpleSex.find(gender='male').exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].gender, d.gender)

    def test_query_enum_with_enum_value(self):
        d = SimpleSex(gender='MALE')
        d.save()
        results = SimpleSex.find(gender=1).exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].gender, d.gender)

    def test_query_enum_with_enum_name_str(self):
        d = SimpleSex(gender='MALE')
        d.save()
        results = SimpleSex.find('gender=MALE').exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].gender, d.gender)

    def test_query_enum_with_lowercase_enum_name_str(self):
        d = SimpleSex(gender='MALE')
        d.save()
        results = SimpleSex.find('gender=male').exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].gender, d.gender)

    def test_query_enum_with_enum_value_str(self):
        d = SimpleSex(gender='MALE')
        d.save()
        results = SimpleSex.find('gender=1').exec()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].gender, d.gender)

    def test_query_avg_with_all_list_of_number(self):
        SimpleScore(name="a", score=1.3).save()
        SimpleScore(name="b", score=2.2).save()
        SimpleScore(name="c", score=3.2).save()
        SimpleScore(name="d", score=4.4).save()
        results = SimpleScore.find().avg("score").exec()
        self.assertEqual(results, mean([1.3, 2.2, 3.2, 4.4]))

    def test_query_avg_with_filter_list_of_number(self):
        SimpleScore(name="Sa", score=4).save()
        SimpleScore(name="Sb", score=2.5).save()
        SimpleScore(name="Sc", score=33).save()
        SimpleScore(name="Sd", score=43).save()
        SimpleScore(name="d", score=423).save()
        SimpleScore(name="e", score=43).save()
        results = SimpleScore.find(**{'name': {'_prefix': 'S'}}).avg("score").exec()
        self.assertEqual(results, mean([4, 2.5, 33, 43]))

    def test_query_sum_with_all_list_of_number(self):
        SimpleScore(name="a", score=1.3).save()
        SimpleScore(name="b", score=2.2).save()
        SimpleScore(name="c", score=3.2).save()
        SimpleScore(name="d", score=4.4).save()
        results = SimpleScore.find().sum("score").exec()
        self.assertEqual(results, sum([1.3, 2.2, 3.2, 4.4]))

    def test_query_sum_with_filter_list_of_number(self):
        SimpleScore(name="Sa", score=4).save()
        SimpleScore(name="Sb", score=2.5).save()
        SimpleScore(name="Sc", score=33).save()
        SimpleScore(name="Sd", score=43).save()
        SimpleScore(name="d", score=423).save()
        SimpleScore(name="e", score=43).save()
        results = SimpleScore.find(**{'name': {'_prefix': 'S'}}).sum("score").exec()
        self.assertEqual(results, sum([4, 2.5, 33, 43]))

    def test_query_min_with_all_list_of_number(self):
        SimpleScore(name="a", score=1.3).save()
        SimpleScore(name="b", score=2.2).save()
        SimpleScore(name="c", score=3.2).save()
        SimpleScore(name="d", score=4.4).save()
        results = SimpleScore.find().min("score").exec()
        self.assertEqual(results, min(1.3, 2.2, 3.2, 4.4))

    def test_query_min_with_filter_list_of_number(self):
        SimpleScore(name="Sa", score=4).save()
        SimpleScore(name="Sb", score=2.5).save()
        SimpleScore(name="Sc", score=33).save()
        SimpleScore(name="Sd", score=43).save()
        SimpleScore(name="d", score=423).save()
        SimpleScore(name="e", score=43).save()
        results = SimpleScore.find(**{'name': {'_prefix': 'S'}}).min("score").exec()
        self.assertEqual(results, min(4, 2.5, 33, 43))

    def test_query_min_with_all_list_of_str(self):
        SimpleScore(name="a", score=1.3).save()
        SimpleScore(name="b", score=2.2).save()
        SimpleScore(name="c", score=3.2).save()
        SimpleScore(name="d", score=4.4).save()
        results = SimpleScore.find().min("name").exec()
        self.assertEqual(results, min('a', 'b', 'c', 'd'))

    def test_query_max_with_all_list_of_number(self):
        SimpleScore(name="a", score=1.3).save()
        SimpleScore(name="b", score=2.2).save()
        SimpleScore(name="c", score=3.2).save()
        SimpleScore(name="d", score=4.4).save()
        results = SimpleScore.find().max("score").exec()
        self.assertEqual(results, max(1.3, 2.2, 3.2, 4.4))

    def test_query_max_with_filter_list_of_number(self):
        SimpleScore(name="Sa", score=4).save()
        SimpleScore(name="Sb", score=2.5).save()
        SimpleScore(name="Sc", score=33).save()
        SimpleScore(name="Sd", score=43).save()
        SimpleScore(name="d", score=423).save()
        SimpleScore(name="e", score=43).save()
        results = SimpleScore.find(**{'name': {'_prefix': 'S'}}).max("score").exec()
        self.assertEqual(results, max(4, 2.5, 33, 43))

    def test_query_max_with_all_list_of_str(self):
        SimpleScore(name="a", score=1.3).save()
        SimpleScore(name="b", score=2.2).save()
        SimpleScore(name="c", score=3.2).save()
        SimpleScore(name="d", score=4.4).save()
        results = SimpleScore.find().max("name").exec()
        self.assertEqual(results, max('a', 'b', 'c', 'd'))

    def test_query_pages_with_all_list_objects(self):
        for i in range(100):
            SimpleScore(name=f's{i}', score=i+20).save()
        results = SimpleScore.find().pages().exec()
        self.assertEqual(results, ceil(100/30))

    def test_query_pages_with_filter_list_objects(self):
        for i in range(100):
            SimpleScore(name=f's{i}', score=i+20).save()
        results = SimpleScore.find(**{'_pageSize': 10}).pages().exec()
        self.assertEqual(results, ceil(100/10))
