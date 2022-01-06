from __future__ import annotations
from unittest import TestCase
from jsonclasses_pymongo.connection import Connection
from tests.classes.linked_account import LinkedAccount, LinkedBalance
from tests.classes.linked_song import LinkedSinger, LinkedSong
from tests.classes.linked_album import LinkedAlbum, LinkedArtist


class TestObjectInclude(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        connection = Connection('linked')
        connection.set_url('mongodb://localhost:27017/linked')
        connection.connect()

    @classmethod
    def tearDownClass(cls) -> None:
        connection = Connection('linked')
        connection.disconnect()

    def setUp(self) -> None:
        collection = Connection.get_collection(LinkedAccount)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedBalance)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedSong)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedSinger)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedAlbum)
        collection.delete_many({})
        collection = Connection.get_collection(LinkedArtist)
        collection.delete_many({})
        collection = Connection('linked').collection('linkedalbumsartists'
                                                     'linkedartistsalbums')
        collection.delete_many({})

    def test_include_fetches_and_sets_local_single_value(self):
        acc = LinkedAccount(name='acc')
        bal = LinkedBalance(name='bal')
        bal.save()
        acc.balance_id = bal.id
        acc.save()
        result = acc.include('balance')
        self.assertIs(result, acc)
        self.assertEqual(acc.balance.__class__.__name__, 'LinkedBalance')
        self.assertEqual(acc.balance.name, bal.name)

    def test_include_fetches_and_sets_foreign_single_value(self):
        acc = LinkedAccount(name='acc')
        bal = LinkedBalance(name='bal')
        bal.save()
        acc.balance_id = bal.id
        acc.save()
        result = bal.include('account')
        self.assertIs(result, bal)
        self.assertEqual(bal.account.__class__.__name__, 'LinkedAccount')
        self.assertEqual(bal.account.name, acc.name)

    def test_include_fetches_and_sets_local_list_value(self):
        singer1 = LinkedSinger(name='michael').save()
        singer2 = LinkedSinger(name='victor').save()
        song = LinkedSong(name='song', singer_ids=[singer1.id, singer2.id])
        song.save()
        result = song.include('singers')
        self.assertEqual(result, song)
        self.assertEqual(len(song.singers), 2)
        self.assertEqual(song.singers[0].name, 'michael')
        self.assertEqual(song.singers[1].name, 'victor')

    def test_include_fetches_and_sets_foreign_list_value(self):
        singer = LinkedSinger(name='michael').save()
        LinkedSong(name='fairy tale', singers=[singer]).save()
        LinkedSong(name='heaven', singers=[singer]).save()
        singer = LinkedSinger.one().exec()
        result = singer.include('songs')
        self.assertEqual(result, singer)
        self.assertEqual(len(singer.songs), 2)
        self.assertEqual(singer.songs[0].name, 'fairy tale')
        self.assertEqual(singer.songs[1].name, 'heaven')

    def test_include_fetches_and_sets_foreign_list_value_with_join_table(self):
        artist = LinkedArtist(name='a')
        album1 = LinkedAlbum(name='a1')
        album2 = LinkedAlbum(name='a2')
        artist.albums = [album1, album2]
        artist.save()
        artist = LinkedArtist.one().exec()
        result = artist.include('albums')
        self.assertEqual(result, artist)
        self.assertEqual(len(artist.albums), 2)
        self.assertEqual(artist.albums[0].name, 'a1')
        self.assertEqual(artist.albums[1].name, 'a2')
