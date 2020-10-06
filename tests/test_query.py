from __future__ import annotations
from unittest import IsolatedAsyncioTestCase
from typing import List, Optional
from jsonclasses import jsonclass, types, ObjectNotFoundException
from jsonclasses_pymongo import MongoObject


@jsonclass
class Find(MongoObject):
    username: Optional[str]
    password: Optional[str]


class TestMongoObjectQuery(IsolatedAsyncioTestCase):

    async def test_find_by_id_returns_object(self):
        object = Find(username='John').save()
        id = object.id
        result = await Find.find(id)
        self.assertEqual(result.username, 'John')
        self.assertEqual(result.password, None)

    async def test_find_by_id_raises_if_not_found(self):
        with self.assertRaisesRegex(
                ObjectNotFoundException,
                'Find\\(_id=1234567890abcd1234567890\\) not found\\.'):
            await Find.find('1234567890abcd1234567890')

    async def test_find_by_id_optional_returns_object(self):
        object = Find(username='John').save()
        id = object.id
        result = await Find.find(id).optional
        self.assertEqual(result.username, 'John')
        self.assertEqual(result.password, None)

    async def test_find_by_id_optional_returns_none_if_not_found(self):
        result = await Find.find('1234567890abcd1234567890').optional
        self.assertIs(result, None)

    async def test_find_without_arguments_returns_list(self):
        Find.delete()
        Find(username='a', password='b').save()
        Find(username='c', password='d').save()
        results = await Find.find()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].username, 'a')
        self.assertEqual(results[0].password, 'b')
        self.assertEqual(results[1].username, 'c')
        self.assertEqual(results[1].password, 'd')

    async def test_find_with_arguments_returns_filtered_list(self):
        Find.delete()
        Find(username='a', password='b').save()
        Find(username='c', password='d').save()
        results = await Find.find({'username': 'a'})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].username, 'a')
        self.assertEqual(results[0].password, 'b')

    async def test_order_asc_with_str(self):
        Find.delete()
        Find(username='a', password='b').save()
        Find(username='z', password='d').save()
        Find(username='q', password='d').save()
        Find(username='e', password='d').save()
        results = await Find.find().order('username')
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].username, 'a')
        self.assertEqual(results[1].username, 'e')
        self.assertEqual(results[2].username, 'q')
        self.assertEqual(results[3].username, 'z')

    async def test_order_desc_with_tuple(self):
        Find.delete()
        Find(username='a', password='b').save()
        Find(username='z', password='d').save()
        Find(username='q', password='d').save()
        Find(username='e', password='d').save()
        results = await Find.find().order(('username', -1))
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].username, 'z')
        self.assertEqual(results[1].username, 'q')
        self.assertEqual(results[2].username, 'e')
        self.assertEqual(results[3].username, 'a')

    async def test_order_asc_with_list_args(self):
        Find.delete()
        Find(username='a', password='b').save()
        Find(username='a', password='d').save()
        Find(username='a', password='z').save()
        Find(username='a', password='c').save()
        results = await Find.find().order([('username', 1), ('password', 1)])
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].password, 'b')
        self.assertEqual(results[1].password, 'c')
        self.assertEqual(results[2].password, 'd')
        self.assertEqual(results[3].password, 'z')

    async def test_project_only_fields(self):
        Find.delete()
        Find(username='a', password='o').save()
        Find(username='z', password='p').save()
        results = await Find.find().project(['username']).order('username')
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].password, None)
        self.assertEqual(results[0].username, 'a')
        self.assertEqual(results[1].password, None)
        self.assertEqual(results[1].username, 'z')

    async def test_skip_skips_results(self):
        Find.delete()
        Find(username='a', password='o').save()
        Find(username='z', password='p').save()
        results = await Find.find().order('username').skip(1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].username, 'z')
        self.assertEqual(results[0].password, 'p')

    async def test_limit_limits_results(self):
        Find.delete()
        Find(username='a', password='o').save()
        Find(username='b', password='o').save()
        Find(username='c', password='o').save()
        results = await Find.find().order('username').skip(1).limit(1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].username, 'b')
        self.assertEqual(results[0].password, 'o')

    async def test_find_one_returns_one_result(self):
        Find.delete()
        Find(username='a', password='o').save()
        Find(username='b', password='o').save()
        Find(username='c', password='o').save()
        result = await Find.find().order('username').one
        self.assertEqual(result.username, 'a')
        self.assertEqual(result.password, 'o')

    async def test_find_one_raises_if_no_results_found(self):
        Find.delete()
        Find(username='a', password='o').save()
        Find(username='b', password='o').save()
        Find(username='c', password='o').save()
        with self.assertRaisesRegex(
                ObjectNotFoundException,
                ("Find\\(filter={'username': 'z'}, sort=None, "
                 "projection=None, skipping=5\\) not found\\.")):
            await Find.find().where({'username': 'z'}).skip(5).one

    async def test_find_one_optional_returns_one_result(self):
        Find.delete()
        Find(username='a', password='o').save()
        Find(username='b', password='o').save()
        Find(username='c', password='o').save()
        result = await Find.find().order('username').one.optional
        self.assertEqual(result.username, 'a')
        self.assertEqual(result.password, 'o')

    async def test_find_one_optional_returns_none_if_no_results_found(self):
        Find.delete()
        Find(username='a', password='o').save()
        Find(username='b', password='o').save()
        Find(username='c', password='o').save()
        result = (await Find.find().where({'username': 'z'}).skip(5)
                  .one.optional)
        self.assertEqual(result, None)

    # def test_include_includes_many_to_many(self):
    #     @jsonclass
    #     class UestAuthor(MongoObject):
    #         name: str
    #         posts: List[UestPost] = types.listof(
    #             'UestPost').linkedthru('authors')

    #     @jsonclass
    #     class UestPost(MongoObject):
    #         title: str
    #         authors: List[UestAuthor] = types.listof(
    #             'UestAuthor').linkedthru('posts')
    #     author = UestAuthor(
    #         **{'name': 'Michael', 'posts': [{'title': 'PA'}, {'title': 'PB'}]})
    #     author.save()
    #     returned_author = UestAuthor.find_by_id(author.id).include('posts')
    #     self.assertEqual(len(returned_author.posts), 2)
    #     self.assertEqual(returned_author.posts[0].title, author.posts[0].title)
    #     self.assertEqual(returned_author.posts[1].title, author.posts[1].title)
