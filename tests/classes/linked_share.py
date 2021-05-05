from __future__ import annotations
from jsonclasses import jsonclass, types
from jsonclasses_pymongo import pymongo, BaseObject


@pymongo
@jsonclass(class_graph='linked')
class LinkedCompany(BaseObject):
    name: str
    owners: list[LinkedOwner] = types.listof('LinkedOwner') \
                                     .linkedthru('companies').cascade


@pymongo
@jsonclass(class_graph='linked')
class LinkedOwner(BaseObject):
    name: str
    companies: list[LinkedCompany] = types.listof('LinkedCompany') \
                                          .linkedthru('owners').deny
