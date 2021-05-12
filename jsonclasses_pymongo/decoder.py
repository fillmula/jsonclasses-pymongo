from __future__ import annotations
from typing import Any, Optional, TypeVar, cast, TYPE_CHECKING
from datetime import date
from jsonclasses.types import Types
from jsonclasses.field_definition import FieldStorage, FieldType
from jsonclasses.types_resolver import TypesResolver
from jsonclasses.mark_graph import MarkGraph
from inflection import underscore, camelize
from .utils import (ref_field_key, ref_field_keys, ref_db_field_key,
                    ref_db_field_keys)
from .coder import Coder
from .dbconf import DBConf
if TYPE_CHECKING:
    from .pymongo_object import PymongoObject
    T = TypeVar('T', bound=PymongoObject)


class Decoder(Coder):

    def decode_list(self,
                    value: list[Any],
                    cls: type[T],
                    types: Types,
                    graph: MarkGraph) -> Optional[list[Any]]:
        if value is None:
            return None
        item_types = TypesResolver().resolve_types(
            types.definition.raw_item_types, cls.definition.config)
        new_cls = item_types.definition.instance_types
        return ([self.decode_item(value=item, cls=new_cls,
                                  types=item_types,
                                  graph=graph)
                for item in value])

    def decode_dict(self,
                    value: dict[str, Any],
                    cls: type[T],
                    types: Types,
                    graph: MarkGraph) -> Optional[dict[str, Any]]:
        if value is None:
            return None
        config: DBConf = cls.dbconf
        if types.definition.field_storage == FieldStorage.FOREIGN_KEY:
            return None
        if types.definition.field_storage == FieldStorage.LOCAL_KEY:
            return ({underscore(k) if config.camelize_db_keys else k: str(v)
                    for k, v in value.items()})
        else:
            item_types = TypesResolver().resolve_types(
                types.definition.raw_item_types)
            return ({underscore(k) if config.camelize_db_keys else k:
                    self.decode_item(value=v, cls=cls, types=item_types,
                                     graph=graph)
                    for k, v in value.items()})

    def decode_shape(self,
                     value: dict[str, Any],
                     cls: type[T],
                     types: Types,
                     graph: MarkGraph) -> dict[str, Any]:
        config: DBConf = cls.dbconf
        shape_types = cast(dict[str, Any], types.definition.shape_types)
        retval = {}
        for k, item_types in shape_types.items():
            retval[k] = self.decode_item(
                value=value[(camelize(k, False)
                             if config.camelize_db_keys else k)],
                cls=cls,
                types=item_types,
                graph=graph)
        return retval

    def decode_item(self,
                    value: Any,
                    cls: type[T],
                    types: Types,
                    graph: MarkGraph) -> Any:
        if value is None:
            return value
        if types.definition.field_type == FieldType.DATE:
            return date.fromisoformat(value.isoformat()[:10])
        elif types.definition.field_type == FieldType.ENUM:
            if isinstance(types.definition.enum_class, str):
                t = TypesResolver().resolve_types(types.definition.enum_class,
                                                  cls.definition.config)
                enum_cls = cast(type, t.definition.enum_class)
                return enum_cls(value)
            else:
                enum_cls = cast(type, types.definition.enum_class)
                return enum_cls(value)
        elif types.definition.field_type == FieldType.LIST:
            return self.decode_list(value=value, cls=cls, types=types,
                                    graph=graph)
        elif types.definition.field_type == FieldType.DICT:
            return self.decode_dict(value=value, cls=cls, types=types,
                                    graph=graph)
        elif types.definition.field_type == FieldType.SHAPE:
            return self.decode_shape(value=value, cls=cls, types=types,
                                     graph=graph)
        elif types.definition.field_type == FieldType.INSTANCE:
            return self.decode_instance(value=value, cls=cls, types=types,
                                        graph=graph)
        else:
            return value

    def decode_instance(self,
                        value: dict[str, Any],
                        cls: type[T],
                        types: Types,
                        graph: MarkGraph) -> Any:
        inst_id = str(value.get('_id'))
        dest = graph.getp(cls, inst_id)
        exist = True
        if dest is None:
            dest = cls()
            exist = False
        for field in cls.definition.fields:
            if cls.dbconf.camelize_db_keys:
                key = camelize(field.name, False)
            else:
                key = field.name
            if self.is_id_field(field):
                if not exist:
                    setattr(dest, field.name, inst_id)
                    graph.put(dest)
            elif self.is_foreign_key_storage(field):
                if value.get(key) is not None:
                    if isinstance(value.get(key), list):
                        t = TypesResolver().resolve_types(
                            field.definition.raw_item_types,
                            cls.definition.config)
                        new_cls = t.definition.instance_types
                        setattr(dest, field.name,
                                self.decode_list(
                                    value[key], new_cls, field.types, graph))
                    else:
                        t = TypesResolver().resolve_types(
                            field.definition.instance_types,
                            cls.definition.config)
                        new_cls = t.definition.instance_types
                        setattr(dest, field.name,
                                self.decode_instance(
                                    cast(dict[str, Any], value.get(key)),
                                    new_cls, field.types, graph))
            elif self.is_local_key_reference_field(field):
                if value.get(key) is not None:
                    t = TypesResolver().resolve_types(
                        field.definition.instance_types,
                        cls.definition.config)
                    new_cls = t.definition.instance_types
                    inst = self.decode_item(
                        value=value.get(key), types=field.types, cls=new_cls,
                        graph=graph)
                    setattr(dest, field.name, inst)
                ref_id = value.get(ref_db_field_key(field.name, cls=cls))
                setattr(dest, ref_field_key(field.name), str(ref_id))
            elif self.is_local_keys_reference_field(field):
                if value.get(key) is not None:
                    t = TypesResolver().resolve_types(
                        field.definition.raw_item_types,
                        cls.definition.config)
                    new_cls = t.definition.instance_types
                    setattr(dest, field.name,
                            self.decode_list(
                                value[key], new_cls, field.types, graph))

                saved_keys = value.get(ref_db_field_keys(field.name, cls))
                setattr(dest, ref_field_keys(field.name),
                        [str(k) for k in saved_keys])
            elif self.is_instance_field(field):
                t = TypesResolver().resolve_types(
                    field.definition.instance_types,
                    cls.definition.config)
                new_cls = t.definition.instance_types
                setattr(dest, field.name, self.decode_item(
                    value=value.get(key), types=field.types, cls=new_cls,
                    graph=graph))
            else:
                if not exist:
                    setattr(
                        dest,
                        field.name,
                        self.decode_item(value=value.get(key),
                                         types=field.types,
                                         cls=cls, graph=graph))
        return dest

    def apply_initial_status(self, root: T,
                             graph: Optional[MarkGraph] = None) -> None:
        if graph is None:
            graph = MarkGraph()
        if graph.get(root) is not None:
            return
        graph.put(root)
        for field in root.__class__.definition.fields:
            if self.is_instance_field(field):
                if getattr(root, field.name) is not None:
                    self.apply_initial_status(getattr(root, field.name), graph)
            elif self.is_list_instance_field(field, root.__class__):
                if getattr(root, field.name) is not None:
                    for item in getattr(root, field.name):
                        self.apply_initial_status(item, graph)
        root._mark_unmodified()

    def decode_root(self,
                    root: dict[str, Any],
                    cls: type[T],
                    graph: Optional[MarkGraph] = None) -> T:
        if graph is None:
            graph = MarkGraph()
        types = Types().instanceof(cls)
        decoded = self.decode_instance(root, cls, types, graph)
        self.apply_initial_status(decoded)
        return decoded

    def decode_root_list(self,
                         root_list: list[dict[str, Any]],
                         cls: type[T],
                         graph: Optional[MarkGraph] = None) -> list[T]:
        if graph is None:
            graph = MarkGraph()
        types = Types().instanceof(cls)
        results: list[T] = []
        for root in root_list:
            decoded = self.decode_instance(root, cls, types, graph)
            results.append(decoded)
        for result in results:
            self.apply_initial_status(result)
        return results
