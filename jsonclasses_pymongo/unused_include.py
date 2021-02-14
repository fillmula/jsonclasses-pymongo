# def _include(self, key_path: str):
#     field = next(field for field in fields(self)
#                  if field.field_name == key_path)
#     fd = field.field_types.field_description
#     if (fd.field_type == FieldType.INSTANCE and
#             fd.field_storage == FieldStorage.LOCAL_KEY):
#         ref_id = getattr(self, ref_field_key(field.field_name))
#         if ref_id is not None:
#             Cls = cast(Type[MongoObject], resolve_types(
#                     fd.instance_types,
#                     graph_sibling=self.__class__
#                 ).field_description.instance_types)
#             setattr(self, field.field_name, Cls.find_by_id(ref_id))
#     elif (fd.field_type == FieldType.INSTANCE and
#             fd.field_storage == FieldStorage.FOREIGN_KEY):
#         foreign_key_name = ref_db_field_key(cast(str, fd.foreign_key),
#                                             self.__class__)
#         Cls = cast(Type[MongoObject], resolve_types(
#             fd.instance_types,
#             graph_sibling=self.__class__).field_description.instance_types)
#         setattr(self, field.field_name, Cls.find_one(
#             {foreign_key_name: ObjectId(self.id)}))
#     elif (fd.field_type == FieldType.LIST and
#             fd.field_storage == FieldStorage.LOCAL_KEY):
#         ref_ids = getattr(self, ref_field_keys(field.field_name))
#         if ref_ids is not None:
#             item_types = resolve_types(
#                 fd.list_item_types, self.__class__)
#             Cls = cast(Type[MongoObject], resolve_types(
#                 item_types.field_description.instance_types,
#                 self.__class__))
#             setattr(self, field.field_name, Cls.find_many(
#                 {'_id': {'$in': [ObjectId(id) for id in ref_ids]}}))
#     elif (fd.field_type == FieldType.LIST and
#             fd.field_storage == FieldStorage.FOREIGN_KEY):
#         if fd.use_join_table:
#             decoder = Decoder()
#             self_class = self.__class__
#             other_class = decoder.list_instance_type(
#                 field, self.__class__)
#             join_table_name = decoder.join_table_name(
#                 self_class,
#                 field.field_name,
#                 other_class,
#                 cast(str, fd.foreign_key)
#             )
#             jt_collection = self_class.db().get_collection(join_table_name)
#             cursor = jt_collection.aggregate([
#                 {
#                     '$match': {
#                         ref_db_field_key(self_class.__name__, self_class):
#                             ObjectId(self.id)
#                     }
#                 },
#                 {
#                     '$lookup': {
#                         'from': other_class.collection().name,
#                         'localField': ref_db_field_key(
#                                 other_class.__name__,
#                                 other_class),
#                         'foreignField': '_id',
#                         'as': 'result'
#                     }
#                 },
#                 {
#                     '$project': {
#                         'result': {'$arrayElemAt': ['$result', 0]}
#                     }
#                 },
#                 {
#                     '$replaceRoot': {
#                         'newRoot': '$result'
#                     }
#                 }
#             ])
#             results = [decoder.decode_root(
#                 doc, other_class) for doc in cursor]
#             setattr(self, field.field_name, results)
#         else:
#             foreign_key_name = ref_db_field_key(
#                 cast(str, fd.foreign_key), self.__class__)
#             item_types = resolve_types(
#                 fd.list_item_types, self.__class__)
#             Cls = cast(Type[MongoObject], resolve_types(
#                 item_types.field_description.instance_types,
#                 self.__class__).field_description.instance_types)
#             setattr(self, field.field_name, Cls.find_many(
#                 {foreign_key_name: ObjectId(self.id)}))
#     else:
#         pass

# def include(self: T, *args: str) -> T:
#     for arg in args:
#         self._include(arg)
#     return self
