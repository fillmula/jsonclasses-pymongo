from __future__ import annotations
from typing import cast, TYPE_CHECKING
from jsonclasses import (Field, FieldType, FieldStorage, resolve_types)
from inflection import camelize
if TYPE_CHECKING:
    from .base_mongo_object import BaseMongoObject


class Coder():

    def is_id_field(self, field: Field) -> bool:
        return field.fdesc.primary

    def is_instance_field(self, field: Field) -> bool:
        return field.fdesc.field_type == FieldType.INSTANCE

    def is_list_field(self, field: Field) -> bool:
        return field.fdesc.field_type == FieldType.LIST

    def is_foreign_key_storage(self, field: Field) -> bool:
        field_storage = field.fdesc.field_storage
        return field_storage == FieldStorage.FOREIGN_KEY

    def is_local_key_storage(self, field: Field) -> bool:
        field_storage = field.fdesc.field_storage
        return field_storage == FieldStorage.LOCAL_KEY

    def is_foreign_key_reference_field(self, field: Field) -> bool:
        return (self.is_instance_field(field) and
                self.is_foreign_key_storage(field))

    def is_foreign_keys_reference_field(self, field: Field) -> bool:
        return (self.is_list_field(field) and
                self.is_foreign_key_storage(field))

    def is_local_key_reference_field(self, field: Field) -> bool:
        return (self.is_instance_field(field) and
                self.is_local_key_storage(field))

    def is_local_keys_reference_field(self, field: Field) -> bool:
        return self.is_list_field(field) and self.is_local_key_storage(field)

    def is_join_table_field(self, field: Field) -> bool:
        return field.field_types.fdesc.use_join_table is True

    def list_instance_type(self,
                           field: Field,
                           sibling: type[BaseMongoObject]
                           ) -> type[BaseMongoObject]:
        from .mongo_object import MongoObject
        fd = field.field_types.fdesc
        item_types = resolve_types(fd.raw_item_types, sibling)
        item_fd = item_types.fdesc
        return cast(type[MongoObject], item_fd.instance_types)

    def join_table_name(self,
                        cls_a: type[BaseMongoObject],
                        field_a: str,
                        cls_b: type[BaseMongoObject],
                        field_b: str) -> str:
        ca = cls_a.collection().name + camelize(field_a).lower()
        cb = cls_b.collection().name + camelize(field_b).lower()
        return ca + cb if ca < cb else cb + ca
