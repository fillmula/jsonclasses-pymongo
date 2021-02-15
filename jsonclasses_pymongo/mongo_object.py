from __future__ import annotations
from typing import Optional
from datetime import datetime
from jsonclasses import jsonclass, types
from bson.objectid import ObjectId
from .base_mongo_object import BaseMongoObject


@jsonclass(abstract=True)
class MongoObject(BaseMongoObject):
    """MongoObject is a concrete subclass for defining your business models
    with MongoDB. A `MongoObject` class represents a MongoDB collection.
    Standard fields are defined on this class including `id`, `created_at`,
    `updated_at` and `deleted_at`. If you want to define your own primary
    key and timestamp fields, use `BaseMongoObject` instead.
    """

    id: str = types.str.readonly.primary.default(lambda: str(ObjectId())) \
                   .required
    """The id string of the object. This field is readonly. A user must not set
    an object's id through web request bodies.
    """

    created_at: datetime = types.datetime.readonly.timestamp('created') \
                                .default(datetime.now).required
    """This field records when this object is created. The value of this field
    is managed internally thus cannot be updated externally with web request
    bodies.
    """

    updated_at: datetime = types.datetime.readonly.timestamp('updated') \
                                .default(datetime.now) \
                                .setonsave(lambda: datetime.now()).required
    """This field records when this object is last updated. The value of this
    field is managed internally thus cannot be updated externally with web
    request bodies.
    """

    deleted_at: Optional[datetime] = types.datetime.readonly \
                                          .timestamp('deleted')
    """This field records when this object is deleted. This is only used for
    soft deleted objects. The value of this field is managed internally thus
    cannot be updated externally with web request bodies.
    """
