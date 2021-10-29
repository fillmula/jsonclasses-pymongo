from __future__ import annotations
from typing import TYPE_CHECKING
from jsonclasses.pkgutils import check_and_install_packages
if TYPE_CHECKING:
    from .pymongo_object import PymongoObject


def ref_key(key: str, cls: type[PymongoObject]) -> tuple[str, str]:
    check_and_install_inflection()
    from inflection import camelize
    field_name = key + '_id'
    if cls.pconf.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return (field_name, db_field_name)


def ref_field_key(key: str) -> str:
    return key + '_id'


def ref_db_field_key(key: str, cls: type[PymongoObject]) -> str:
    check_and_install_inflection()
    from inflection import camelize
    field_name = ref_field_key(key)
    if cls.pconf.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return db_field_name


def ref_field_keys(key: str) -> str:
    check_and_install_inflection()
    from inflection import singularize
    return singularize(key) + '_ids'


def ref_db_field_keys(key: str, cls: type[PymongoObject]) -> str:
    check_and_install_inflection()
    from inflection import camelize
    field_name = ref_field_keys(key)
    if cls.pconf.camelize_db_keys:
        db_field_name = camelize(field_name, False)
    else:
        db_field_name = field_name
    return db_field_name


def check_and_install_inflection():
    packages = {'inflection': ('inflection', '>=0.5.1,<1.0.0')}
    check_and_install_packages(packages)
