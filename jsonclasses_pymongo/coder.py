from __future__ import annotations
from typing import cast, TYPE_CHECKING
from jsonclasses.jfield import JField
from jsonclasses.fdef import FStore
from inflection import camelize
from .connection import Connection
if TYPE_CHECKING:
    from .pobject import PObject


class Coder():

    def list_instance_type(self, field: JField) -> type[PObject]:
        from .pobject import PObject
        fd = field.types.fdef
        item_types = fd.item_types
        item_fd = item_types.fdef
        return cast(type[PObject], item_fd.raw_inst_types)

    def join_table_name(self,
                        cls_a: type[PObject],
                        field_a: str,
                        cls_b: type[PObject],
                        field_b: str) -> str:
        connection = Connection.from_class(cls_a)
        cabase = connection.collection_from(cls_a).name
        cbbase = connection.collection_from(cls_b).name
        ca = cabase + camelize(field_a).lower()
        cb = cbbase + camelize(field_b).lower()
        return ca + cb if ca < cb else cb + ca
