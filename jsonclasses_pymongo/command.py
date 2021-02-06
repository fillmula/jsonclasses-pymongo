from __future__ import annotations
from typing import Any
from pymongo.collection import Collection


class Command:

    def execute(self) -> None:
        raise NotImplementedError(
            'Please use concrete subclasses of Command.')

    def __repr__(self) -> str:
        return '<Command()>'


class InsertOneCommand(Command):

    def __init__(self, collection: Collection, object: dict[str, Any]) -> None:
        self.collection = collection
        self.object = object

    def execute(self) -> None:
        self.collection.insert_one(self.object)

    def __repr__(self) -> str:
        return (f'<InsertOneCommand(collection={self.collection.name}, '
                f'object={self.object})>')


class UpdateOneCommand(Command):

    def __init__(self,
                 collection: Collection,
                 object: dict[str, Any],
                 matcher: dict[str, Any]) -> None:
        self.collection = collection
        self.object = object
        self.matcher = matcher
        self.upsert = False

    def execute(self) -> None:
        self.collection.update_one(
            filter=self.matcher,
            update=self.object,
            upsert=self.upsert)

    def __repr__(self) -> str:
        return (f'<UpdateOneCommand(collection={self.collection.name}, '
                f'object={self.object}), matcher={self.matcher}>')


class UpsertOneCommand(UpdateOneCommand):

    def __init__(self,
                 collection: Collection,
                 object: dict[str, Any],
                 matcher: dict[str, Any]) -> None:
        super().__init__(collection=collection, object=object, matcher=matcher)
        self.upsert = True

    def __repr__(self) -> str:
        return (f'<UpsertOneCommand(collection={self.collection.name}, '
                f'object={self.object}), matcher={self.matcher}>')


class DeleteOneCommand(Command):

    def __init__(self,
                 collection: Collection,
                 matcher: dict[str, Any]) -> None:
        self.collection = collection
        self.matcher = matcher

    def execute(self) -> None:
        self.collection.delete_one(filter=self.matcher)

    def __repr__(self) -> str:
        return (f'<UpsertOneCommand(collection={self.collection.name}, '
                f'matcher={self.matcher}>')


class BatchCommand(Command):

    def __init__(self, commands: list[Command]) -> None:
        self.commands = commands

    def execute(self) -> None:
        for command in self.commands:
            command.execute()
