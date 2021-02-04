"""This module defines encoding and decoding context objects."""
from __future__ import annotations
from typing import NamedTuple, Any, Union, TYPE_CHECKING
from jsonclasses import Types, ObjectGraph
if TYPE_CHECKING:
    from .base_mongo_object import BaseMongoObject


class EncodingContext(NamedTuple):
    """Encoding context contains necessary information for encoding JSON Class
    objects into database writing commands.
    """
    value: Any
    types: Types
    keypath_root: str
    root: BaseMongoObject
    keypath_owner: str
    owner: BaseMongoObject
    keypath_parent: str
    parent: Union[list[Any], dict[str, Any], BaseMongoObject]
    object_graph: ObjectGraph

    def new(self, **kwargs):
        """Return a new encoding context by replacing provided values."""
        keys = kwargs.keys()
        return EncodingContext(
            value=kwargs['value'] if 'value' in keys else self.value,
            types=kwargs['types'] if 'types' in keys else self.types,
            keypath_root=(kwargs['keypath_root']
                          if 'keypath_root' in keys else self.keypath_root),
            root=kwargs['root'] if 'root' in keys else self.root,
            keypath_owner=(kwargs['keypath_owner']
                           if 'keypath_owner' in keys else self.keypath_owner),
            owner=kwargs['owner'] if 'owner' in keys else self.owner,
            keypath_parent=(kwargs['keypath_parent']
                            if 'keypath_parent' in keys
                            else self.keypath_parent),
            parent=kwargs['parent'] if 'parent' in keys else self.parent,
            object_graph=(kwargs['object_graph']
                          if 'object_graph' in keys else self.object_graph))
