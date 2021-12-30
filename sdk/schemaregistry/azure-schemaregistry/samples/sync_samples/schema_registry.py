# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""
FILE: schema_registry.py
DESCRIPTION:
    This sample demonstrates authenticating the SchemaRegistryClient and basic usage, including:
        - registering a schema
        - getting a schema by its ID
        - getting schema id.
USAGE:
    python schema_registry.py
    Set the environment variables with your own values before running the sample:
    1) SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE - The schema registry fully qualified namespace,
     which should follow the format: `<your-namespace>.servicebus.windows.net`
    2) SCHEMAREGISTRY_GROUP - The name of the schema group.

This example uses DefaultAzureCredential, which requests a token from Azure Active Directory.
For more information on DefaultAzureCredential, see
 https://docs.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#defaultazurecredential.
"""
import os
import json
import sys
import math

from azure.identity import DefaultAzureCredential
from azure.schemaregistry import SchemaRegistryClient, SchemaFormat


SCHEMAREGISTRY_FQN = os.environ["SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE"]
GROUP_NAME = os.environ["SCHEMAREGISTRY_GROUP"]
NAME = "your-schema-name"
FORMAT = SchemaFormat.AVRO

fields = []
# max fields = (schema size - no fields bytes)/size of each fields
schema_size = 100
SCHEMA_JSON = {
    "type": "record",
    "name": "example.User",
    "fields": fields,
}
schema_no_fields_size = sys.getsizeof(json.dumps(SCHEMA_JSON, separators=(",", ":")))
print(schema_no_fields_size)
fields.append({"name": "favor_number00000", "type": ["int", "null"]})
one_field_size = sys.getsizeof(json.dumps(SCHEMA_JSON, separators=(",", ":")))
print(one_field_size)
field_size = one_field_size - schema_no_fields_size
print(field_size)
num_fields = math.floor((schema_size-schema_no_fields_size)/field_size)
print(num_fields)
for i in range(1,num_fields):
    num_idx = f'{i:05d}'
    fields.append(
        {"name": f"favo_number{num_idx}", "type": ["int", "null"]},
    )

DEFINITION = json.dumps(SCHEMA_JSON, separators=(",", ":"))
print(sys.getsizeof(DEFINITION))


def register_schema(client, group_name, name, definition, format):
    print("Registering schema...")
    schema_properties = client.register_schema(
        group_name, name, definition, format
    )
    print("Schema registered, returned schema id is {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


def get_schema_by_id(client, schema_id):
    print("Getting schema by id...")
    schema = client.get_schema(schema_id)
    print(
        "The schema string of schema id: {} string is {}".format(id, schema.definition)
    )
    print("Schema properties are {}".format(schema_id))
    return schema.definition


def get_schema_id(client, group_name, name, definition, format):
    print("Getting schema id...")
    schema_properties = client.get_schema_properties(
        group_name, name, definition, format
    )
    print("The schema id is: {}".format(schema_properties.id))
    print("Schema properties are {}".format(schema_properties))
    return schema_properties.id


if __name__ == "__main__":
    token_credential = DefaultAzureCredential()
    schema_registry_client = SchemaRegistryClient(
        fully_qualified_namespace=SCHEMAREGISTRY_FQN, credential=token_credential
    )
    with schema_registry_client:
        schema_id = register_schema(
            schema_registry_client, GROUP_NAME, NAME, DEFINITION, FORMAT
        )
#        schema_str = get_schema_by_id(schema_registry_client, schema_id)
#        schema_id = get_schema_id(
#            schema_registry_client, GROUP_NAME, NAME, DEFINITION, FORMAT
#        )
