from __future__ import annotations
from typing import (List, Dict, Any, NamedTuple, TypeVar, Type, cast,
                    TYPE_CHECKING)
from jsonclasses import (fields, types, Field, FieldType, FieldStorage,
                         resolve_types, LookupMap, concat_keypath)
from datetime import datetime
from inflection import camelize
from bson.objectid import ObjectId
from .coder import Coder
from .utils import ref_db_field_key, ref_db_field_keys
from .context import EncodingContext
from .write_command import WriteCommand
if TYPE_CHECKING:
    from .mongo_object import MongoObject
    T = TypeVar('T', bound=MongoObject)


class EncodingResult(NamedTuple):
    """The result from encoding an item."""
    result: Any
    write_commands: List[WriteCommand]


class Encoder(Coder):
    """Write commands encoder."""

    def encode_list(self, context: EncodingContext) -> EncodingResult:
        if context.value is None:
            return EncodingResult(result=None, write_commands=[])
        value = cast(List[Any], context.value)
        fd = context.types.field_description
        item_types = resolve_types(fd.list_item_types)
        if fd.field_storage == FieldStorage.FOREIGN_KEY:
            item_types = item_types.linkedby(cast(str, fd.foreign_key))
        if fd.field_storage == FieldStorage.LOCAL_KEY:
            item_types = item_types.linkto
        result = []
        write_commands = []
        for index, item in enumerate(value):
            item_result, item_commands = self.encode_item(context.new(
                value=item,
                types=item_types,
                keypath_root=concat_keypath(context.keypath_root, index),
                keypath_owner=concat_keypath(context.keypath_owner, index),
                keypath_parent=str(index),
                parent=value))
            result.append(item_result)
            write_commands.extend(item_commands)
        return EncodingResult(result, write_commands)

    def encode_dict(self, context: EncodingContext) -> EncodingResult:
        if context.value is None:
            return EncodingResult(result=None, write_commands=[])
        value = cast(Dict[str, Any], context.value)
        fd = context.types.field_description
        item_types = resolve_types(fd.dict_item_types)
        camelized = context.owner.__class__.config.camelize_db_keys
        result = {}
        write_commands = []
        for key, item in value.items():
            item_result, item_commands = self.encode_item(context.new(
                value=item,
                types=item_types,
                keypath_root=concat_keypath(context.keypath_root, key),
                keypath_owner=concat_keypath(context.keypath_owner, key),
                keypath_parent=str(key),
                parent=value))
            result[camelize(key, False) if camelized else key] = item_result
            write_commands.extend(item_commands)
        return EncodingResult(result, write_commands)

    def encode_shape(self, context: EncodingContext) -> EncodingResult:
        if context.value is None:
            return EncodingResult(result=None, write_commands=[])
        value = cast(Dict[str, Any], context.value)
        fd = context.types.field_description
        shape_types = cast(Dict[str, Any], fd.shape_types)
        camelized = context.owner.__class__.config.camelize_db_keys
        result = {}
        write_commands = []
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
            write_commands.extend(item_commands)
        return EncodingResult(result, write_commands)

    def _join_command(self,
                      this_instance: MongoObject,
                      this_field: Field,
                      that_cls: Type[MongoObject],
                      that_id: ObjectId) -> WriteCommand:
        this_cls = this_instance.__class__
        this_cls_name = this_cls.__name__
        that_cls_name = that_cls.__name__
        this_field_name = ref_db_field_key(this_cls_name, this_cls)
        that_field_name = ref_db_field_key(that_cls_name, that_cls)
        join_table_name = self.join_table_name(
            this_cls,
            this_field.field_name,
            that_cls,
            cast(str, this_field.field_description.foreign_key))
        join_table_collection = this_cls.db().get_collection(join_table_name)
        this_pk = cast(str, this_instance.__class__.config.primary_key)
        this_id = ObjectId(getattr(this_instance, this_pk))
        matcher = {
            this_field_name: this_id,
            that_field_name: that_id
        }
        return WriteCommand(matcher, join_table_collection, matcher)

    def encode_instance(self,
                        context: EncodingContext,
                        root: bool = False) -> EncodingResult:
        from .mongo_object import MongoObject
        if context.value is None:
            return EncodingResult(result=None, write_commands=[])
        value = cast(MongoObject, context.value)
        cls = value.__class__
        cls_name = cls.__name__
        id = getattr(value, cast(str, value.__class__.config.primary_key))
        if context.lookup_map.fetch(cls_name, id) is not None:
            return EncodingResult({'_id': ObjectId(id)}, write_commands=[])
        context.lookup_map.put(cls_name, id, value)
        instance_fd = context.types.field_description
        write_instance = instance_fd.field_storage != FieldStorage.EMBEDDED
        if root:
            write_instance = True
        result = {}
        write_commands = []
        for field in fields(value):
            fname = field.field_name
            fvalue = getattr(value, fname)
            ftypes = field.field_types
            if self.is_id_field(field, value.__class__):
                result['_id'] = ObjectId(fvalue)
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
                write_commands.extend(item_commands)
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
                write_commands.extend(item_commands)
                if not self.is_join_table_field(field):
                    continue
                for list_item in item_result:
                    join_command = self._join_command(
                        value,
                        field,
                        self.list_instance_type(field, cls),
                        list_item['_id'])
                    write_commands.append(join_command)
            elif self.is_local_key_reference_field(field):
                if fvalue is None:
                    result[ref_db_field_key(fname, cls)] = None
                    continue
                item_result, item_commands = self.encode_instance(context.new(
                    value=fvalue,
                    types=ftypes,
                    keypath_root=concat_keypath(context.keypath_root, fname),
                    keypath_owner=fname,
                    owner=value,
                    keypath_parent=fname,
                    parent=value))
                result[ref_db_field_key(fname, cls)] = item_result['_id']
                write_commands.extend(item_commands)
            elif self.is_local_keys_reference_field(field):
                if fvalue is None:
                    result[ref_db_field_keys(fname, cls)] = None
                    continue
                item_result, item_commands = self.encode_list(context.new(
                    value=fvalue,
                    types=ftypes,
                    keypath_root=concat_keypath(context.keypath_root, fname),
                    keypath_owner=fname,
                    owner=value,
                    keypath_parent=fname,
                    parent=value))
                id_list = [result['_id'] for result in item_result]
                result[ref_db_field_keys(fname, cls)] = id_list
                write_commands.extend(item_commands)
            else:
                item_result, item_commands = self.encode_item(context.new(
                    value=fvalue,
                    types=ftypes,
                    keypath_root=concat_keypath(context.keypath_root, fname),
                    keypath_owner=concat_keypath(context.keypath_owner, fname),
                    owner=value,
                    keypath_parent=fname,
                    parent=value))
                result[field.db_field_name] = item_result
                write_commands.extend(item_commands)
        if write_instance:
            write_commands.append(
                WriteCommand(result, value.__class__.collection()))
        return EncodingResult(result, write_commands)

    def encode_item(self, context: EncodingContext) -> EncodingResult:
        if context.value is None:
            return EncodingResult(result=None, write_commands=[])
        field_type = context.types.field_description.field_type
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
                write_commands=[])
        else:
            return EncodingResult(context.value, [])

    # return save commands
    def encode_root(self, root: T) -> List[WriteCommand]:
        return self.encode_instance(EncodingContext(
            value=root,
            types=types.instanceof(root.__class__),
            keypath_root='',
            root=root,
            keypath_owner='',
            owner=root,
            keypath_parent='',
            parent=root,
            lookup_map=LookupMap()), root=True)[1]
