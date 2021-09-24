from __future__ import annotations
from typing import cast, TYPE_CHECKING
from jsonclasses.jfield import JField
from jsonclasses.fdef import FType, FStore
from inflection import camelize
from .connection import Connection
if TYPE_CHECKING:
    from .pymongo_object import PymongoObject


class Coder():

    def is_id_field(self, field: JField) -> bool:
        return field.fdef.primary

    def is_instance_field(self, field: JField) -> bool:
        return field.fdef.ftype == FType.INSTANCE

    def is_list_field(self, field: JField) -> bool:
        return field.fdef.ftype == FType.LIST

    def is_list_instance_field(self, field: JField,
                                     cls: type[PymongoObject]) -> bool:
        if not self.is_list_field(field):
            return False
        t = field.fdef.item_types
        if t.fdef.raw_inst_types is not None:
            return True
        return False

    def is_foreign_key_storage(self, field: JField) -> bool:
        fstore = field.fdef.fstore
        return fstore == FStore.FOREIGN_KEY

    def is_local_key_storage(self, field: JField) -> bool:
        fstore = field.fdef.fstore
        return fstore == FStore.LOCAL_KEY

    def is_foreign_key_reference_field(self, field: JField) -> bool:
        return (self.is_instance_field(field) and
                self.is_foreign_key_storage(field))

    def is_foreign_keys_reference_field(self, field: JField) -> bool:
        return (self.is_list_field(field) and
                self.is_foreign_key_storage(field))

    def is_local_key_reference_field(self, field: JField) -> bool:
        return (self.is_instance_field(field) and
                self.is_local_key_storage(field))

    def is_local_keys_reference_field(self, field: JField) -> bool:
        return self.is_list_field(field) and self.is_local_key_storage(field)

    def is_join_table_field(self, field: JField) -> bool:
        return field.types.fdef.use_join_table is True

    def list_instance_type(self, field: JField) -> type[PymongoObject]:
        from .pymongo_object import PymongoObject
        fd = field.types.fdef
        item_types = fd.item_types
        item_fd = item_types.fdef
        return cast(type[PymongoObject], item_fd.raw_inst_types)

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
