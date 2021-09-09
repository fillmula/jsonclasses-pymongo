from __future__ import annotations
from typing import Any, Optional, TypeVar, cast, TYPE_CHECKING
from datetime import date
from jsonclasses.types import Types
from jsonclasses.fdef import FStore, FType
from jsonclasses.mgraph import MGraph
from inflection import underscore, camelize
from .utils import (ref_field_key, ref_field_keys, ref_db_field_key,
                    ref_db_field_keys)
from .coder import Coder
from .pconf import PConf
if TYPE_CHECKING:
    from .pymongo_object import PymongoObject
    T = TypeVar('T', bound=PymongoObject)


class Decoder(Coder):

    def decode_list(self,
                    value: list[Any],
                    cls: type[T],
                    types: Types,
                    graph: MGraph) -> Optional[list[Any]]:
        if value is None:
            return None
        item_types = types.fdef.item_types
        new_cls = item_types.fdef.raw_inst_types
        return ([self.decode_item(value=item, cls=new_cls,
                                  types=item_types,
                                  graph=graph)
                for item in value])

    def decode_dict(self,
                    value: dict[str, Any],
                    cls: type[T],
                    types: Types,
                    graph: MGraph) -> Optional[dict[str, Any]]:
        if value is None:
            return None
        item_types = types.fdef.item_types
        return {k: self.decode_item(value=v, cls=cls, types=item_types, graph=graph) for k, v in value.items()}

    def decode_shape(self,
                     value: dict[str, Any],
                     cls: type[T],
                     types: Types,
                     graph: MGraph) -> dict[str, Any]:
        config: PConf = cls.pconf
        shape_types = cast(dict[str, Any], types.fdef.raw_shape_types)
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
                    graph: MGraph) -> Any:
        if value is None:
            return value
        if types.fdef.field_type == FType.DATE:
            return date.fromisoformat(value.isoformat()[:10])
        elif types.fdef.field_type == FType.ENUM:
            if isinstance(types.fdef.enum_class, str):
                enum_cls = cast(type, types.fdef.enum_class)
                return enum_cls(value)
            else:
                enum_cls = cast(type, types.fdef.enum_class)
                return enum_cls(value)
        elif types.fdef.field_type == FType.LIST:
            return self.decode_list(value=value, cls=cls, types=types,
                                    graph=graph)
        elif types.fdef.field_type == FType.DICT:
            return self.decode_dict(value=value, cls=cls, types=types,
                                    graph=graph)
        elif types.fdef.field_type == FType.SHAPE:
            return self.decode_shape(value=value, cls=cls, types=types,
                                     graph=graph)
        elif types.fdef.field_type == FType.INSTANCE:
            return self.decode_instance(value=value, cls=cls, types=types,
                                        graph=graph)
        else:
            return value

    def decode_instance(self,
                        value: dict[str, Any],
                        cls: type[T],
                        types: Types,
                        graph: MGraph) -> Any:
        inst_id = str(value.get('_id'))
        dest = graph.getp(cls, inst_id)
        exist = True
        if dest is None:
            dest = cls()
            exist = False
        for field in cls.cdef.fields:
            if cls.pconf.camelize_db_keys:
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
                        t = field.fdef.item_types
                        new_cls = t.fdef.raw_inst_types
                        setattr(dest, field.name,
                                self.decode_list(
                                    value[key], new_cls, field.types, graph))
                    else:
                        new_cls = field.fdef.inst_cls
                        setattr(dest, field.name,
                                self.decode_instance(
                                    cast(dict[str, Any], value.get(key)),
                                    new_cls, field.types, graph))
            elif self.is_local_key_reference_field(field):
                if value.get(key) is not None:
                    new_cls = field.fdef.inst_cls
                    inst = self.decode_item(
                        value=value.get(key), types=field.types, cls=new_cls,
                        graph=graph)
                    setattr(dest, field.name, inst)
                ref_id = value.get(ref_db_field_key(field.name, cls=cls))
                setattr(dest, ref_field_key(field.name), str(ref_id))
            elif self.is_local_keys_reference_field(field):
                if value.get(key) is not None:
                    new_cls = field.fdef.inst_cls
                    setattr(dest, field.name,
                            self.decode_list(
                                value[key], new_cls, field.types, graph))

                saved_keys = value.get(ref_db_field_keys(field.name, cls))
                setattr(dest, ref_field_keys(field.name),
                        [str(k) for k in saved_keys])
            elif self.is_instance_field(field):
                new_cls = field.fdef.inst_cls
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
                             graph: Optional[MGraph] = None) -> None:
        if graph is None:
            graph = MGraph()
        if graph.get(root) is not None:
            return
        graph.put(root)
        for field in root.__class__.cdef.fields:
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
                    graph: Optional[MGraph] = None) -> T:
        if graph is None:
            graph = MGraph()
        types = Types().instanceof(cls)
        decoded = self.decode_instance(root, cls, types, graph)
        self.apply_initial_status(decoded)
        return decoded

    def decode_root_list(self,
                         root_list: list[dict[str, Any]],
                         cls: type[T],
                         graph: Optional[MGraph] = None) -> list[T]:
        if graph is None:
            graph = MGraph()
        types = Types().instanceof(cls)
        results: list[T] = []
        for root in root_list:
            decoded = self.decode_instance(root, cls, types, graph)
            results.append(decoded)
        for result in results:
            self.apply_initial_status(result)
        return results
