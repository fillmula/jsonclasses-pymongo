from __future__ import annotations
from typing import List, Dict, Any, Optional, TypeVar, Tuple, TYPE_CHECKING
from datetime import datetime
from jsonclasses import (fields, Types, Config, FieldType, FieldStorage,
                         collection_argument_type_to_types)
from inflection import camelize
from bson.objectid import ObjectId
from .coder import Coder
from .utils import (ref_field_key, ref_field_keys, ref_db_field_key,
                    ref_db_field_keys)
from .write_command import WriteCommand

if TYPE_CHECKING:
    from .mongo_object import MongoObject
    T = TypeVar('T', bound=MongoObject)


class Encoder(Coder):

    def encode_list(
        self,
        value: Optional[List[Any]],
        owner: T,
        types: Any,
        parent: Optional[T] = None,
        parent_linkedby: Optional[str] = None
    ) -> Tuple[Optional[List[Any]], List[WriteCommand]]:
        if value is None:
            return None, []
        item_types = collection_argument_type_to_types(
            types.field_description.list_item_types)
        if types.field_description.field_storage == FieldStorage.FOREIGN_KEY:
            item_types = item_types.linkedby(
                types.field_description.foreign_key)
        elif types.field_description.field_storage == FieldStorage.LOCAL_KEY:
            item_types = item_types.linkto
        else:
            pass
        dest = []
        write_commands = []
        for item in value:
            new_value, commands = self.encode_item(
                value=item,
                owner=owner,
                types=item_types,
                parent=parent,
                parent_linkedby=parent_linkedby
            )
            if (types.field_description.field_storage ==
                    FieldStorage.FOREIGN_KEY):
                dest.append(new_value)
            elif (types.field_description.field_storage ==
                    FieldStorage.LOCAL_KEY):
                dest.append(new_value['_id'])
            else:
                dest.append(new_value)
            write_commands.extend(commands)
        return dest, write_commands

    def encode_dict(
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
        item_types = collection_argument_type_to_types(
            types.field_description.dict_item_types)
        dest = {}
        write_commands = []
        for (key, item) in value.items():
            new_value, commands = self.encode_item(
                value=item,
                owner=owner,
                types=item_types,
                parent=parent,
                parent_linkedby=parent_linkedby
            )
            dest[camelize(key, False)
                 if config.camelize_db_keys else key] = new_value
            write_commands.extend(commands)
        return dest, write_commands

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
                types=collection_argument_type_to_types(
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
                            field.field_types.field_description.foreign_key
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

    def encode_item(
        self,
        value: Any,
        owner: T,
        types: Types,
        parent: Optional[T] = None,
        parent_linkedby: Optional[str] = None
    ) -> Tuple[Any, List[WriteCommand]]:
        if value is None:
            return (value, [])
        if types.field_description.field_type == FieldType.DATE:
            return datetime.fromisoformat(value.isoformat()), []
        elif types.field_description.field_type == FieldType.LIST:
            return self.encode_list(value=value,
                                    owner=owner,
                                    types=types,
                                    parent=parent,
                                    parent_linkedby=parent_linkedby)
        elif types.field_description.field_type == FieldType.DICT:
            return self.encode_dict(value=value,
                                    owner=owner,
                                    types=types,
                                    parent=parent,
                                    parent_linkedby=parent_linkedby)
        elif types.field_description.field_type == FieldType.SHAPE:
            return self.encode_shape(value=value,
                                     owner=owner,
                                     types=types,
                                     parent=parent,
                                     parent_linkedby=parent_linkedby)
        elif types.field_description.field_type == FieldType.INSTANCE:
            return self.encode_instance(value=value,
                                        owner=owner,
                                        parent=parent,
                                        types=types,
                                        parent_linkedby=parent_linkedby)
        else:
            return value, []

    # return save commands
    def encode_root(self, root: T) -> List[WriteCommand]:
        return self.encode_instance(value=root,
                                    owner=root,
                                    types=None,
                                    parent=None,
                                    parent_linkedby=None)[1]
