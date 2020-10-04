from __future__ import annotations
from typing import (List, Dict, Any, NamedTuple, Optional, TypeVar, Tuple,
                    cast, TYPE_CHECKING)
from jsonclasses import (fields, types, Config, FieldType, FieldStorage,
                         resolve_types, LookupMap, concat_keypath)
from datetime import datetime
from inflection import camelize
from bson.objectid import ObjectId
from .coder import Coder
from .utils import (ref_field_key, ref_field_keys, ref_db_field_key,
                    ref_db_field_keys)
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
            fk = cast(str, fd.foreign_key)
            item_types = item_types.linkedby(fk)
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
            if fd.field_storage == FieldStorage.FOREIGN_KEY:
                result.append(item_result)
            elif fd.field_storage == FieldStorage.LOCAL_KEY:
                result.append(item_result['_id'])
            else:
                result.append(item_result)
            write_commands.extend(item_commands)
        return EncodingResult(result=result, write_commands=write_commands)

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

    def encode_shape(
        self,
        value: Optional[Dict[str, Any]],
        owner: T,
        types: Any,
        parent: Optional[T] = None,
        parent_linkedby: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], List[WriteCommand]]:
        if value is None:
            return None, []
        config: Config = owner.__class__.config
        dest = {}
        write_commands = []
        for (key, item) in value.items():
            new_value, commands = self.encode_item(
                value=item,
                owner=owner,
                types=resolve_types(
                    types.field_description.shape_types[key]),
                parent=parent,
                parent_linkedby=parent_linkedby
            )
            dest[camelize(key, False)
                 if config.camelize_db_keys else key] = new_value
            write_commands.extend(commands)
        return dest, write_commands

    def encode_instance(
        self,
        value: Optional[T],
        owner: T,
        types: Optional[Any],
        parent: Optional[T] = None,
        parent_linkedby: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], List[WriteCommand]]:
        if value is None:
            return None, []
        do_not_write_self = False
        if types is not None:
            if types.field_description.field_storage == FieldStorage.EMBEDDED:
                do_not_write_self = True
        dest = {}
        write_commands = []
        for field in fields(value):
            if self.is_id_field(field):
                dest['_id'] = ObjectId(getattr(value, 'id'))
            elif self.is_foreign_key_reference_field(field):
                # not assign, but get write commands
                value_at_field = getattr(value, field.field_name)
                if value_at_field is not None:
                    _encoded, commands = self.encode_instance(
                        value=value_at_field,
                        owner=owner,
                        types=field.field_types,
                        parent=value,
                        parent_linkedby=(field.field_types
                                         .field_description.foreign_key)
                    )
                    write_commands.extend(commands)
            elif self.is_foreign_keys_reference_field(field):
                # not assign, but get a list of write commands
                value_at_field = getattr(value, field.field_name)
                if value_at_field is not None:
                    encoded, commands = self.encode_list(
                        value=value_at_field,
                        owner=owner,
                        types=field.field_types,
                        parent=value,
                        parent_linkedby=(field.field_types
                                         .field_description.foreign_key)
                    )
                    if self.is_join_table_field(field):
                        this_field_class = value.__class__
                        this_field_name = ref_db_field_key(
                            this_field_class.__name__, this_field_class)
                        other_field_class = self.other_field_class_for_list_instance_type(  # noqa: E501
                            field, this_field_class)
                        other_field_name = ref_db_field_key(
                            other_field_class.__name__,
                            other_field_class
                        )
                        join_table_name = self.join_table_name(
                            this_field_class,
                            field.field_name,
                            other_field_class,
                            cast(str,
                                 field.field_types.
                                 field_description.foreign_key)
                        )
                        join_table_collection = (this_field_class.db()
                                                 .get_collection(join_table_name))  # noqa: E501
                        this_field_id = ObjectId(value.id)
                        assert encoded is not None
                        for item in encoded:
                            write_commands.append(WriteCommand({
                                '_id': ObjectId(),
                                this_field_name: this_field_id,
                                other_field_name: ObjectId(item['_id'])
                            }, join_table_collection, {
                                this_field_name: this_field_id,
                                other_field_name: ObjectId(item['_id'])
                            }))
                    write_commands.extend(commands)
                elif parent_linkedby == field.field_name:
                    pass
            elif self.is_local_key_reference_field(field):
                # assign a local key, and get write commands
                value_at_field = getattr(value, field.field_name)
                if value_at_field is not None:
                    setattr(value, ref_field_key(
                        field.field_name), value_at_field.id)
                    encoded_i, commands = self.encode_instance(
                        value=value_at_field,
                        owner=owner,
                        types=field.field_types,
                        parent=value,
                        parent_linkedby=field.field_types.field_description.foreign_key  # noqa: E501
                    )
                    assert encoded_i is not None
                    dest[ref_db_field_key(
                        field.field_name, value.__class__)] = encoded_i['_id']
                    write_commands.extend(commands)
                elif parent_linkedby == field.field_name:
                    assert parent is not None
                    setattr(value, ref_field_key(field.field_name), parent.id)
                    dest[ref_db_field_key(field.field_name, value.__class__)] = ObjectId(  # noqa: E501
                        parent.id)
            elif self.is_local_keys_reference_field(field):
                # assign a list of local keys, and get write commands
                value_at_field = getattr(value, field.field_name)
                if value_at_field is not None:
                    setattr(value, ref_field_keys(field.field_name),
                            [v.id for v in value_at_field])
                    encoded, commands = self.encode_list(
                        value=value_at_field,
                        owner=owner,
                        types=field.field_types,
                        parent=value,
                        parent_linkedby=field.field_name
                    )
                    dest[ref_db_field_keys(
                        field.field_name, value.__class__)] = encoded
                    write_commands.extend(commands)
            else:
                item_value, new_write_commands = self.encode_item(
                    value=getattr(value, field.field_name),
                    owner=owner,
                    types=field.field_types,
                    parent=parent,
                    parent_linkedby=parent_linkedby
                )
                dest[field.db_field_name] = item_value
                write_commands.extend(new_write_commands)
        if not do_not_write_self:
            write_commands.append(WriteCommand(
                dest, value.__class__.collection()))
        return dest, write_commands

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
            lookup_map=LookupMap()
        ))[1]
