from __future__ import annotations
from typing import Any, NamedTuple, TypeVar, cast, TYPE_CHECKING
from datetime import datetime, timezone
from bson.objectid import ObjectId
from jsonclasses.jfield import JField
from jsonclasses.fdef import FStore, FType
from jsonclasses.keypath import concat_keypath
from jsonclasses.mgraph import MGraph
from jsonclasses.types import types
from .utils import (
    idval, dbid, ref_db_field_key, ref_db_field_keys,
    list_inst_type, join_table_name
)
from .context import EncodingContext
from .command import (Command, InsertOneCommand, UpdateOneCommand,
                      UpsertOneCommand, DeleteOneCommand, BatchCommand)
from .connection import Connection
if TYPE_CHECKING:
    from .pobject import PObject
    T = TypeVar('T', bound=PObject)


class EncodingResult(NamedTuple):
    """The result from encoding an item."""
    result: Any
    commands: list[Command]


class Encoder:
    """Write commands encoder."""

    def encode_list(self, context: EncodingContext) -> EncodingResult:
        if context.value is None:
            return EncodingResult(result=None, commands=[])
        value = cast(list[Any], context.value)
        fd = context.types.fdef
        item_types = fd.item_types
        if fd.fstore == FStore.FOREIGN_KEY:
            item_types = item_types.linkedby(cast(str, fd.foreign_key))
        if fd.fstore == FStore.LOCAL_KEY:
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
        item_types = context.types.fdef.item_types
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
            result[key] = item_result
            commands.extend(item_commands)
        return EncodingResult(result, commands)

    def _join_command(self,
                      this_instance: PObject,
                      this_field: JField,
                      that_cls: type[PObject],
                      that_id: str | ObjectId) -> UpsertOneCommand:
        this_cls = this_instance.__class__
        connection = Connection.from_class(this_instance.__class__)
        this_cls_name = this_cls.__name__
        that_cls_name = that_cls.__name__
        this_field_name = ref_db_field_key(this_cls_name, this_cls)
        that_field_name = ref_db_field_key(that_cls_name, that_cls)
        jt_name = join_table_name(this_field)
        collection = connection.collection(jt_name, [this_field_name, that_field_name])
        this_id = dbid(this_instance)
        matcher = {
            this_field_name: this_id,
            that_field_name: that_id
        }
        return UpsertOneCommand(collection=collection,
                                object={'$set': matcher},
                                matcher=matcher)

    def _unlink_command(self,
                        this_instance: PObject,
                        this_field: JField,
                        that_cls: type[PObject],
                        that_id: str | ObjectId) -> DeleteOneCommand:
        this_cls = this_instance.__class__
        connection = Connection.from_class(this_instance.__class__)
        this_cls_name = this_cls.__name__
        that_cls_name = that_cls.__name__
        this_field_name = ref_db_field_key(this_cls_name, this_cls)
        that_field_name = ref_db_field_key(that_cls_name, that_cls)
        jt_name = join_table_name(this_field)
        collection = connection.collection(jt_name, [this_field_name, that_field_name])
        this_id = dbid(this_instance)
        matcher = {
            this_field_name: this_id,
            that_field_name: that_id
        }
        return DeleteOneCommand(collection=collection, matcher=matcher)

    def encode_instance(self,
                        context: EncodingContext,
                        root: bool = False) -> EncodingResult:
        from .pobject import PObject
        if context.value is None:
            return EncodingResult(result=None, commands=[])
        value = cast(PObject, context.value)
        cls = value.__class__
        id = cast(str | int, value._id)
        previous_id = cast(str | int, value._previous_id)
        if context.mark_graph.getp(cls, id) is not None:
            return EncodingResult({'_id': dbid(value)}, commands=[])
        context.mark_graph.put(value)
        instance_fd = context.types.fdef
        write_instance = instance_fd.fstore != FStore.EMBEDDED
        if root:
            write_instance = True
        use_insert_command = False
        fields_need_update: set[str] = value.persisted_modified_fields
        if value.is_new:
            use_insert_command = True
        result_set = {}
        result_addtoset = {}
        result_unset = {}
        matcher = {}
        commands = []
        for field in value.__class__.cdef.fields:
            if field.fdef.fstore == FStore.TEMP:
                continue
            if field.fdef.fstore == FStore.CALCULATED:
                continue
            fname = field.name
            fvalue = getattr(value, fname)
            ftypes = field.types
            if field.is_primary:
                result_set['_id'] = idval(field, fvalue)
                if use_insert_command:
                    pass
                else:
                    matcher['_id'] = idval(field, previous_id)
            elif field.is_foreign_one_ref:
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
            elif field.is_foreign_many_ref:
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
                if not field.is_join_table_ref:
                    continue
                for list_item in item_result:
                    if list_item.get('_id'):
                        join_command = self._join_command(
                            value,
                            field,
                            list_inst_type(field),
                            list_item['_id'])
                        commands.append(join_command)
                if value.unlinked_objects.get(field.name) is not None:
                    for item in value.unlinked_objects[field.name]:
                        if item._id is not None:
                            unlink_command = self._unlink_command(
                                value,
                                field,
                                list_inst_type(field),
                                dbid(item))
                            commands.append(unlink_command)
                if value._link_keys.get(field.name) is not None:
                    for k in value._link_keys.get(field.name):
                        join_command = self._join_command(
                            value,
                            field,
                            list_inst_type(field),
                            ObjectId(k))
                        commands.append(join_command)
                if value._unlink_keys.get(field.name) is not None:
                    for k in value._unlink_keys.get(field.name):
                        unlink_command = self._unlink_command(
                            value,
                            field,
                            list_inst_type(field),
                            ObjectId(k))
                        commands.append(unlink_command)
            elif field.is_local_one_ref:
                if fvalue is None:
                    tsfm = value.__class__.cdef.jconf.ref_name_strategy
                    if getattr(value, tsfm(field)) is not None:
                        if use_insert_command or fname in fields_need_update:
                            foreignid = idval(field.foreign_cdef.primary_field, getattr(value, tsfm(field)))
                            result_set[ref_db_field_key(fname, cls)] = foreignid
                    else:
                        if use_insert_command:
                            pass
                        elif fname in fields_need_update:
                            result_unset[ref_db_field_key(fname, cls)] = None
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
                    setattr(value, field.ref_name,
                                   str(item_result['_id']))
                commands.extend(item_commands)
            elif field.is_local_many_ref:
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
                    tsfm = value.__class__.cdef.jconf.ref_name_strategy
                    field_id_name = tsfm(field)
                    id_list = [idval(field.foreign_cdef.primary_field, v) for v in getattr(value, field_id_name)]
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
                    efname = context.owner.__class__.pconf.to_db_key(fname)
                    if use_insert_command:
                        if item_result is not None:
                            result_set[efname] = item_result
                    else:
                        if item_result is None:
                            result_unset[efname] = None
                        else:
                            result_set[efname] = item_result
                commands.extend(item_commands)
        if write_instance:
            collection = Connection.get_collection(value.__class__)
            if use_insert_command:
                insert_command = InsertOneCommand(collection, result_set)
                commands.append(insert_command)
            else:
                updator = {}
                if len(result_set) > 0:
                    updator['$set'] = result_set
                if len(result_addtoset) > 0:
                    updator['$addToSet'] = result_addtoset
                if len(result_unset) > 0:
                    updator['$unset'] = result_unset
                if len(updator) > 0:
                    update_c = UpdateOneCommand(collection, updator, matcher)
                    commands.append(update_c)
        value._clear_temp_fields()
        setattr(value, '_is_new', False)
        setattr(value, '_is_modified', False)
        setattr(value, '_modified_fields', set())
        setattr(value, '_previous_values', {})
        return EncodingResult(result_set, commands)

    def encode_item(self, context: EncodingContext) -> EncodingResult:
        if context.value is None:
            return EncodingResult(result=None, commands=[])
        ftype = context.types.fdef.ftype
        if ftype == FType.LIST:
            return self.encode_list(context)
        elif ftype == FType.DICT:
            return self.encode_dict(context)
        elif ftype == FType.INSTANCE:
            return self.encode_instance(context)
        elif ftype == FType.DATE:
            return EncodingResult(
                result=datetime.fromisoformat(
                    context.value.isoformat(),
                ).replace(tzinfo=timezone.utc),
                commands=[])
        elif ftype == FType.ENUM:
            return EncodingResult(result=context.value.value, commands=[])
        else:
            return EncodingResult(context.value, [])

    def encode_root(self, root: T) -> BatchCommand:
        commands = self.encode_instance(EncodingContext(
            value=root,
            types=types.objof(root.__class__),
            keypath_root='',
            root=root,
            keypath_owner='',
            owner=root,
            keypath_parent='',
            parent=root,
            mark_graph=MGraph()), root=True)[1]
        return BatchCommand(commands=commands)
