from __future__ import annotations
from typing import Any, NamedTuple, TypeVar, Union, cast, TYPE_CHECKING
from jsonclasses import (get_fields, types, Field, FieldType, FieldStorage,
                         resolve_types, ObjectGraph, concat_keypath)
from datetime import datetime
from inflection import camelize
from bson.objectid import ObjectId
from .coder import Coder
from .utils import ref_db_field_key, ref_db_field_keys
from .context import EncodingContext
from .command import (Command, InsertOneCommand, UpdateOneCommand,
                      UpsertOneCommand, BatchCommand)
if TYPE_CHECKING:
    from .base_mongo_object import BaseMongoObject
    T = TypeVar('T', bound=BaseMongoObject)


class EncodingResult(NamedTuple):
    """The result from encoding an item."""
    result: Any
    commands: list[Command]


class Encoder(Coder):
    """Write commands encoder."""

    def encode_list(self, context: EncodingContext) -> EncodingResult:
        if context.value is None:
            return EncodingResult(result=None, commands=[])
        value = cast(list[Any], context.value)
        fd = context.types.fdesc
        item_types = resolve_types(fd.raw_item_types,
                                   graph_sibling=context.root.__class__)
        if fd.field_storage == FieldStorage.FOREIGN_KEY:
            item_types = item_types.linkedby(cast(str, fd.foreign_key))
        if fd.field_storage == FieldStorage.LOCAL_KEY:
            item_types = item_types.linkto
        result = []
        commands = []
        for index, item in enumerate(value):
            item_result, item_commands = self.encode_item(context.new(
                value=item,
                types=item_types,
                keypath_root=concat_keypath(context.keypath_root, index),
                keypath_owner=concat_keypath(context.keypath_owner, index),
                keypath_parent=str(index),
                parent=value))
            result.append(item_result)
            commands.extend(item_commands)
        return EncodingResult(result, commands)

    def encode_dict(self, context: EncodingContext) -> EncodingResult:
        if context.value is None:
            return EncodingResult(result=None, commands=[])
        value = cast(dict[str, Any], context.value)
        fd = context.types.fdesc
        item_types = resolve_types(fd.raw_item_types)
        camelized = context.owner.__class__.config.camelize_db_keys
        result = {}
        commands = []
        for key, item in value.items():
            item_result, item_commands = self.encode_item(context.new(
                value=item,
                types=item_types,
                keypath_root=concat_keypath(context.keypath_root, key),
                keypath_owner=concat_keypath(context.keypath_owner, key),
                keypath_parent=str(key),
                parent=value))
            result[camelize(key, False) if camelized else key] = item_result
            commands.extend(item_commands)
        return EncodingResult(result, commands)

    def encode_shape(self, context: EncodingContext) -> EncodingResult:
        if context.value is None:
            return EncodingResult(result=None, commands=[])
        value = cast(dict[str, Any], context.value)
        fd = context.types.fdesc
        shape_types = cast(dict[str, Any], fd.shape_types)
        camelized = context.owner.__class__.config.camelize_db_keys
        result = {}
        commands = []
        for key, item in value.items():
            item_types = resolve_types(shape_types[key])
            item_result, item_commands = self.encode_item(context.new(
                value=item,
                types=item_types,
                keypath_root=concat_keypath(context.keypath_root, key),
                keypath_owner=concat_keypath(context.keypath_owner, key),
                keypath_parent=str(key),
                parent=value))
            result[camelize(key, False) if camelized else key] = item_result
            commands.extend(item_commands)
        return EncodingResult(result, commands)

    def _join_command(self,
                      this_instance: BaseMongoObject,
                      this_field: Field,
                      that_cls: type[BaseMongoObject],
                      that_id: ObjectId) -> UpsertOneCommand:
        this_cls = this_instance.__class__
        this_cls_name = this_cls.__name__
        that_cls_name = that_cls.__name__
        this_field_name = ref_db_field_key(this_cls_name, this_cls)
        that_field_name = ref_db_field_key(that_cls_name, that_cls)
        join_table_name = self.join_table_name(
            this_cls,
            this_field.field_name,
            that_cls,
            cast(str, this_field.fdesc.foreign_key))
        collection = this_cls.db().get_collection(join_table_name)
        this_id = ObjectId(this_instance._id)
        matcher = {
            this_field_name: this_id,
            that_field_name: that_id
        }
        return UpsertOneCommand(collection=collection,
                                object=matcher,
                                matcher=matcher)

    def encode_instance(self,
                        context: EncodingContext,
                        root: bool = False) -> EncodingResult:
        from .base_mongo_object import BaseMongoObject
        if context.value is None:
            return EncodingResult(result=None, commands=[])
        value = cast(BaseMongoObject, context.value)
        cls = value.__class__
        id = cast(Union[str, int], value._id)
        if context.object_graph.getp(cls, id) is not None:
            return EncodingResult({'_id': ObjectId(id)}, commands=[])
        context.object_graph.put(value)
        instance_fd = context.types.fdesc
        write_instance = instance_fd.field_storage != FieldStorage.EMBEDDED
        if root:
            write_instance = True
        use_insert_command = False
        fields_need_update: set[str] = set()
        if value.is_new:
            use_insert_command = True
            fields_need_update = value.modified_fields
        result_set = {}
        matcher = {}
        commands = []
        result_addtoset = {}
        for field in get_fields(value):
            fname = field.field_name
            fvalue = getattr(value, fname)
            ftypes = field.field_types
            if self.is_id_field(field):
                if use_insert_command:
                    result_set['_id'] = ObjectId(fvalue)
                else:
                    matcher['_id'] = ObjectId(fvalue)
            elif self.is_foreign_key_reference_field(field):
                if fvalue is None:
                    continue
                _, item_commands = self.encode_instance(context.new(
                    value=fvalue,
                    types=ftypes,
                    keypath_root=concat_keypath(context.keypath_root, fname),
                    keypath_owner=fname,
                    owner=value,
                    keypath_parent=fname,
                    parent=value))
                commands.extend(item_commands)
            elif self.is_foreign_keys_reference_field(field):
                if fvalue is None:
                    continue
                item_result, item_commands = self.encode_list(context.new(
                    value=fvalue,
                    types=ftypes,
                    keypath_root=concat_keypath(context.keypath_root, fname),
                    keypath_owner=fname,
                    owner=value,
                    keypath_parent=fname,
                    parent=value))
                commands.extend(item_commands)
                if not self.is_join_table_field(field):
                    continue
                for list_item in item_result:
                    join_command = self._join_command(
                        value,
                        field,
                        self.list_instance_type(field, cls),
                        list_item['_id'])
                    commands.append(join_command)
            elif self.is_local_key_reference_field(field):
                if fvalue is None:
                    if use_insert_command or fname in fields_need_update:
                        result_set[ref_db_field_key(fname, cls)] = None
                    continue
                item_result, item_commands = self.encode_instance(context.new(
                    value=fvalue,
                    types=ftypes,
                    keypath_root=concat_keypath(context.keypath_root, fname),
                    keypath_owner=fname,
                    owner=value,
                    keypath_parent=fname,
                    parent=value))
                if use_insert_command or fname in fields_need_update:
                    fname_ref = ref_db_field_key(fname, cls)
                    result_set[fname_ref] = item_result['_id']
                commands.extend(item_commands)
            elif self.is_local_keys_reference_field(field):
                if fvalue is None:
                    if use_insert_command or fname in fields_need_update:
                        result_set[ref_db_field_keys(fname, cls)] = None
                    continue
                item_result, item_commands = self.encode_list(context.new(
                    value=fvalue,
                    types=ftypes,
                    keypath_root=concat_keypath(context.keypath_root, fname),
                    keypath_owner=fname,
                    owner=value,
                    keypath_parent=fname,
                    parent=value))
                if use_insert_command or fname in fields_need_update:
                    id_list = [result['_id'] for result in item_result]
                    fname_ref = ref_db_field_keys(fname, cls)
                    if use_insert_command:
                        result_set[fname_ref] = id_list
                    else:
                        result_addtoset[fname_ref] = {'$each': id_list}
                commands.extend(item_commands)
            else:
                item_result, item_commands = self.encode_item(context.new(
                    value=fvalue,
                    types=ftypes,
                    keypath_root=concat_keypath(context.keypath_root, fname),
                    keypath_owner=concat_keypath(context.keypath_owner, fname),
                    owner=value,
                    keypath_parent=fname,
                    parent=value))
                if use_insert_command or fname in fields_need_update:
                    result_set[field.db_field_name] = item_result
                commands.extend(item_commands)
        if write_instance:
            collection = value.__class__.collection()
            if use_insert_command:
                insert_command = InsertOneCommand(collection, result_set)
                commands.append(insert_command)
            else:
                update_command = UpdateOneCommand(
                    collection,
                    {'$set': result_set, '$addToSet': result_addtoset},
                    matcher)
                commands.append(update_command)
        return EncodingResult(result_set, commands)

    def encode_item(self, context: EncodingContext) -> EncodingResult:
        if context.value is None:
            return EncodingResult(result=None, commands=[])
        field_type = context.types.fdesc.field_type
        if field_type == FieldType.LIST:
            return self.encode_list(context)
        elif field_type == FieldType.DICT:
            return self.encode_dict(context)
        elif field_type == FieldType.SHAPE:
            return self.encode_shape(context)
        elif field_type == FieldType.INSTANCE:
            return self.encode_instance(context)
        elif field_type == FieldType.DATE:
            return EncodingResult(
                result=datetime.fromisoformat(context.value.isoformat()),
                commands=[])
        else:
            return EncodingResult(context.value, [])

    def encode_root(self, root: T) -> BatchCommand:
        commands = self.encode_instance(EncodingContext(
            value=root,
            types=types.instanceof(root.__class__),
            keypath_root='',
            root=root,
            keypath_owner='',
            owner=root,
            keypath_parent='',
            parent=root,
            object_graph=ObjectGraph()), root=True)[1]
        return BatchCommand(commands=commands)
