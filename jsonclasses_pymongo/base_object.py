from __future__ import annotations
from datetime import datetime
from jsonclasses import jsonclass, types


@jsonclass(abstract=True)
class BaseObject:
    """MongoObject is a abstract subclass for defining your business models
    with MongoDB. A `MongoObject` class represents a MongoDB collection.
    Standard fields are defined on this class including `id`, `created_at` and
    `updated_at`. This class is obsolete and will be removed in the future.
    """

    id: str = types.readonly.str.primary.mongoid.required
    """The id string of the object. This field is readonly. A user must not set
    an object's id through web request bodies.
    """

    created_at: datetime = types.readonly.datetime.tscreated.required
    """This field records when this object is created. The value of this field
    is managed internally thus cannot be updated externally with web request
    bodies.
    """

    updated_at: datetime = types.readonly.datetime.tsupdated.required
    """This field records when this object is last updated. The value of this
    field is managed internally thus cannot be updated externally with web
    request bodies.
    """
