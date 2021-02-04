from __future__ import annotations
from typing import Any, Optional, TypeVar, cast, TYPE_CHECKING
from datetime import date
from jsonclasses import (get_fields, Types, Config, FieldType, FieldStorage,
                         resolve_types)
from inflection import underscore, camelize
from .utils import (ref_field_key, ref_field_keys, ref_db_field_key,
                    ref_db_field_keys)
from .coder import Coder
if TYPE_CHECKING:
    from .base_mongo_object import BaseMongoObject
    T = TypeVar('T', bound=BaseMongoObject)


class Decoder(Coder):

    def decode_list(self,
                    value: list[Any],
                    cls: type[T],
                    types: Types) -> Optional[list[Any]]:
        if value is None:
            return None
        if types.fdesc.field_storage == FieldStorage.FOREIGN_KEY:
            return None
        elif types.fdesc.field_storage == FieldStorage.LOCAL_KEY:
            return [str(item) for item in value]
        else:
            item_types = resolve_types(types.fdesc.raw_item_types)
            return ([self.decode_item(value=item, cls=cls, types=item_types)
                    for item in value])

    def decode_dict(self,
                    value: dict[str, Any],
                    cls: type[T],
                    types: Types) -> Optional[dict[str, Any]]:
        if value is None:
            return None
        config: Config = cls.config
        if types.fdesc.field_storage == FieldStorage.FOREIGN_KEY:
            return None
        if types.fdesc.field_storage == FieldStorage.LOCAL_KEY:
            return ({underscore(k) if config.camelize_db_keys else k: str(v)
                    for k, v in value.items()})
        else:
            item_types = resolve_types(types.fdesc.raw_item_types)
            return ({underscore(k) if config.camelize_db_keys else k:
                    self.decode_item(value=v, cls=cls, types=item_types)
                    for k, v in value.items()})

    def decode_shape(self,
                     value: dict[str, Any],
                     cls: type[T],
                     types: Types) -> dict[str, Any]:
        config: Config = cls.config
        shape_types = cast(dict[str, Any], types.fdesc.shape_types)
        retval = {}
        for k, item_types in shape_types.items():
            retval[k] = self.decode_item(
                value=value[(camelize(k, False)
                             if config.camelize_db_keys else k)],
                cls=cls,
                types=item_types)
        return retval

    def decode_instance(self,
                        value: dict[str, Any],
                        cls: type[T],
                        types: Types) -> Any:
        from .base_mongo_object import BaseMongoObject
        if types.fdesc.field_storage == FieldStorage.FOREIGN_KEY:
            return None
        elif types.fdesc.field_storage == FieldStorage.LOCAL_KEY:
            return str(value)
        else:
            return self.decode_root(
                root=value,
                cls=cast(type[BaseMongoObject], resolve_types(
                    types.fdesc.instance_types,
                    graph_sibling=cls
                ).fdesc.instance_types)
            )

    def decode_item(self, value: Any, cls: type[T], types: Types) -> Any:
        if value is None:
            return value
        if types.fdesc.field_type == FieldType.DATE:
            return date.fromisoformat(value.isoformat()[:10])
        elif types.fdesc.field_type == FieldType.LIST:
            return self.decode_list(value=value, cls=cls, types=types)
        elif types.fdesc.field_type == FieldType.DICT:
            return self.decode_dict(value=value, cls=cls, types=types)
        elif types.fdesc.field_type == FieldType.SHAPE:
            return self.decode_shape(value=value, cls=cls, types=types)
        elif types.fdesc.field_type == FieldType.INSTANCE:
            return self.decode_instance(value=value, cls=cls, types=types)
        else:
            return value

    def decode_root(self,
                    root: dict[str, Any],
                    cls: type[T]) -> T:
        dest = cls()
        for field in get_fields(cls):
            if self.is_id_field(field):
                setattr(dest, 'id', str(root.get('_id')))
            elif self.is_foreign_key_storage(field):
                pass
            elif self.is_local_key_reference_field(field):
                setattr(
                    dest,
                    ref_field_key(field.field_name),
                    self.decode_item(
                        value=root.get(ref_db_field_key(
                            field.db_field_name, cls=cls)),
                        types=field.field_types,
                        cls=cls
                    )
                )
            elif self.is_local_keys_reference_field(field):
                setattr(
                    dest,
                    ref_field_keys(field.field_name),
                    self.decode_item(
                        value=root.get(ref_db_field_keys(
                            field.db_field_name, cls=cls)),
                        types=field.field_types,
                        cls=cls
                    )
                )
            else:
                setattr(
                    dest,
                    field.field_name,
                    self.decode_item(
                        value=root.get(field.db_field_name),
                        types=field.field_types,
                        cls=cls
                    )
                )
        setattr(dest, '_is_new', False)
        setattr(dest, '_is_modified', False)
        setattr(dest, '_modified_fields', set())
        return dest
