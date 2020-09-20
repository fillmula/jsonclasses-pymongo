from __future__ import annotations
from typing import TypeVar, Type, TYPE_CHECKING
from jsonclasses import (Field, FieldType, FieldStorage,
                         collection_argument_type_to_types)
from inflection import camelize
if TYPE_CHECKING:
    from .mongo_object import MongoObject
    T = TypeVar('T', bound=MongoObject)


class Coder():

    def is_id_field(self, field: Field) -> bool:
        return field.field_name == 'id'

    def is_instance_field(self, field: Field) -> bool:
        return (field.field_types.field_description.field_type ==
                FieldType.INSTANCE)

    def is_list_field(self, field: Field) -> bool:
        return field.field_types.field_description.field_type == FieldType.LIST

    def is_foreign_key_storage(self, field: Field) -> bool:
        return (field.field_types.field_description.field_storage ==
                FieldStorage.FOREIGN_KEY)

    def is_local_key_storage(self, field: Field) -> bool:
        return (field.field_types.field_description.field_storage ==
                FieldStorage.LOCAL_KEY)

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
        return field.field_types.field_description.use_join_table is True

    def other_field_class_for_list_instance_type(
        self, field: Field, sibling: Type[T]
    ) -> Type[T]:
        item_types = collection_argument_type_to_types(
            field.field_types.field_description.list_item_types, sibling)
        return item_types.field_description.instance_types

    def join_table_name(
        self, cls_a: Type[T], field_a: str, cls_b: Type[T], field_b: str
    ) -> str:
        ca = cls_a.collection().name + camelize(field_a).lower()
        cb = cls_b.collection().name + camelize(field_b).lower()
        return ca + cb if ca < cb else cb + ca
