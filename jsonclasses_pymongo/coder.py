from __future__ import annotations
from typing import cast, TYPE_CHECKING
from jsonclasses.jsonclass_field import JSONClassField
from jsonclasses.field_definition import FieldType, FieldStorage
from jsonclasses.types_resolver import TypesResolver
from inflection import camelize
from .connection import Connection
if TYPE_CHECKING:
    from .pymongo_object import PymongoObject


class Coder():

    def is_id_field(self, field: JSONClassField) -> bool:
        return field.definition.primary

    def is_instance_field(self, field: JSONClassField) -> bool:
        return field.definition.field_type == FieldType.INSTANCE

    def is_list_field(self, field: JSONClassField) -> bool:
        return field.definition.field_type == FieldType.LIST

    def is_list_instance_field(self, field: JSONClassField,
                                     cls: type[PymongoObject]) -> bool:
        if not self.is_list_field(field):
            return False
        t = TypesResolver().resolve_types(field.definition.raw_item_types,
                                          cls.definition.config)
        if t.definition.instance_types is not None:
            return True
        return False


    def is_foreign_key_storage(self, field: JSONClassField) -> bool:
        field_storage = field.definition.field_storage
        return field_storage == FieldStorage.FOREIGN_KEY

    def is_local_key_storage(self, field: JSONClassField) -> bool:
        field_storage = field.definition.field_storage
        return field_storage == FieldStorage.LOCAL_KEY

    def is_foreign_key_reference_field(self, field: JSONClassField) -> bool:
        return (self.is_instance_field(field) and
                self.is_foreign_key_storage(field))

    def is_foreign_keys_reference_field(self, field: JSONClassField) -> bool:
        return (self.is_list_field(field) and
                self.is_foreign_key_storage(field))

    def is_local_key_reference_field(self, field: JSONClassField) -> bool:
        return (self.is_instance_field(field) and
                self.is_local_key_storage(field))

    def is_local_keys_reference_field(self, field: JSONClassField) -> bool:
        return self.is_list_field(field) and self.is_local_key_storage(field)

    def is_join_table_field(self, field: JSONClassField) -> bool:
        return field.types.definition.use_join_table is True

    def list_instance_type(self,
                           field: JSONClassField,
                           sibling: type[PymongoObject]
                           ) -> type[PymongoObject]:
        from .pymongo_object import PymongoObject
        fd = field.types.definition
        item_types = TypesResolver().resolve_types(fd.raw_item_types,
                                                   sibling.definition.config)
        item_fd = item_types.definition
        return cast(type[PymongoObject], item_fd.instance_types)

    def join_table_name(self,
                        cls_a: type[PymongoObject],
                        field_a: str,
                        cls_b: type[PymongoObject],
                        field_b: str) -> str:
        connection = Connection.from_class(cls_a)
        cabase = connection.collection_from(cls_a).name
        cbbase = connection.collection_from(cls_b).name
        ca = cabase + camelize(field_a).lower()
        cb = cbbase + camelize(field_b).lower()
        return ca + cb if ca < cb else cb + ca
