from jsonclasses import Field, FieldType, FieldStorage

class Coder():

  def is_id_field(self, field: Field) -> bool:
    return field.field_name == 'id'

  def is_instance_field(self, field: Field) -> bool:
    return field.field_types.field_description.field_type == FieldType.INSTANCE

  def is_list_field(self, field: Field) -> bool:
    return field.field_types.field_description.field_type == FieldType.LIST

  def is_local_key_storage(self, field: Field) -> bool:
    return field.field_types.field_description.field_storage == FieldStorage.LOCAL_KEY

  def is_foreign_key_storage(self, field: Field) -> bool:
    return field.field_types.field_description.field_storage == FieldStorage.FOREIGN_KEY

  def is_local_key_reference_field(self, field: Field) -> bool:
    return self.is_instance_field(field) and self.is_local_key_storage(field)

  def is_local_keys_reference_field(self, field: Field) -> bool:
    return self.is_list_field(field) and self.is_local_key_storage(field)
