from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo


@pymongo
@jsonclass(class_graph='linked')
class TodoListOwner:
    id: str = types.readonly.str.primary.mongoid.required
    todo_lists: list[TodoList] = types.listof('TodoList').linkedby('todo_list_owner')
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required


@pymongo
@jsonclass(class_graph='linked')
class TodoList:
    id: str = types.readonly.str.primary.mongoid.required
    name: str
    todo_list_owner: TodoListOwner = types.objof(TodoListOwner).linkto.required
    created_at: datetime = types.readonly.datetime.tscreated.required
    updated_at: datetime = types.readonly.datetime.tsupdated.required
