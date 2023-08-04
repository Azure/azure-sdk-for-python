from genson import SchemaBuilder
def generate_schema_with_genson(content):
    builder = SchemaBuilder()
    builder.add_object(content)
    return builder.to_schema()
def invalid_schema():
    pass

schema = generate_schema_with_genson(invalid_schema)
print(schema)