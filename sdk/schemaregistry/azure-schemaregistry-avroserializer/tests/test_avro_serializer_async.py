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
import functools
import pytest
import uuid
import json
from io import BytesIO
import pytest

import avro
from avro.io import AvroTypeException


from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer.aio import AvroSerializer
from azure.schemaregistry.serializer.avroserializer.exceptions import SchemaParseError, SchemaSerializationError, SchemaDeserializationError
from azure.identity.aio import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer

SchemaRegistryPowerShellPreparer = functools.partial(PowerShellPreparer, "schemaregistry", schemaregistry_fully_qualified_namespace="fake_resource.servicebus.windows.net/", schemaregistry_group="fakegroup")

class TestAvroSerializerAsync(AzureRecordedTestCase):

    def create_client(self, fully_qualified_namespace):
        credential = self.get_credential(SchemaRegistryClient, is_async=True)
        return self.create_client_from_credential(SchemaRegistryClient, credential, fully_qualified_namespace=fully_qualified_namespace, is_async=True)

    @pytest.mark.asyncio
    @SchemaRegistryPowerShellPreparer()
    async def test_basic_sr_avro_serializer_with_auto_register_schemas(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        async with sr_client:
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            schema_str = "{\"type\": \"record\", \"name\": \"User\", \"namespace\": \"example.avro\", \"fields\": [{\"type\": \"string\", \"name\": \"name\"}, {\"type\": [\"int\", \"null\"], \"name\": \"favorite_number\"}, {\"type\": [\"string\", \"null\"], \"name\": \"favorite_color\"}]}"
            schema = avro.schema.parse(schema_str)

            dict_data = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
            encoded_data = await sr_avro_serializer.serialize(dict_data, schema=schema_str)

            assert encoded_data[0:4] == b'\0\0\0\0'
            schema_properties = await sr_client.get_schema_properties(schemaregistry_group, schema.fullname, str(schema), "Avro")
            schema_id = schema_properties.id
            assert encoded_data[4:36] == schema_id.encode("utf-8")

            decoded_data = await sr_avro_serializer.deserialize(encoded_data)
            assert decoded_data["name"] == u"Ben"
            assert decoded_data["favorite_number"] == 7
            assert decoded_data["favorite_color"] == u"red"

    @pytest.mark.asyncio
    @SchemaRegistryPowerShellPreparer()
    async def test_basic_sr_avro_serializer_without_auto_register_schemas(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        async with sr_client:
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            schema_str = "{\"type\": \"record\", \"name\": \"User\", \"namespace\": \"example.avro\", \"fields\": [{\"type\": \"string\", \"name\": \"name\"}, {\"type\": [\"int\", \"null\"], \"name\": \"favorite_number\"}, {\"type\": [\"string\", \"null\"], \"name\": \"favorite_color\"}]}"
            schema = avro.schema.parse(schema_str)

            dict_data = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
            encoded_data = await sr_avro_serializer.serialize(dict_data, schema=schema_str)

            assert encoded_data[0:4] == b'\0\0\0\0'
            schema_properties = await sr_client.get_schema_properties(schemaregistry_group, schema.fullname, str(schema), "Avro")
            schema_id = schema_properties.id
            assert encoded_data[4:36] == schema_id.encode("utf-8")

            decoded_data = await sr_avro_serializer.deserialize(encoded_data)
            assert decoded_data["name"] == u"Ben"
            assert decoded_data["favorite_number"] == 7
            assert decoded_data["favorite_color"] == u"red"

    ################################################################# 
    ######################### PARSE SCHEMAS #########################
    ################################################################# 

    @SchemaRegistryPowerShellPreparer()
    async def test_parse_invalid_json_string(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)
        invalid_schema = {
            "name":"User",
            "type":"record",
            "namespace":"example.avro",
            "fields":[{"name":"name","type":"string"}]
        }
        invalid_schema_string = "{}".format(invalid_schema)
        with pytest.raises(SchemaParseError):    # caught avro SchemaParseError
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=invalid_schema_string) 

    ######################### PRIMITIVES #########################

    @SchemaRegistryPowerShellPreparer()
    async def test_parse_primitive_types(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        primitive_string = "string"
        with pytest.raises(SchemaParseError) as e:
            await sr_avro_serializer.serialize("hello", schema=primitive_string) 

    ######################### type fixed #########################

    @SchemaRegistryPowerShellPreparer()
    async def test_parse_fixed_types(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        # avro bug: should give warning from IgnoredLogicalType error since precision < 0
        #fixed_type_ignore_logical_type_error = """{"type": "fixed", "size": 4, "namespace":"example.avro", "name":"User", "precision": -1}"""
        #await sr_avro_serializer.serialize({}, schema=fixed_type_ignore_logical_type_error) 

        schema_no_size = """{"type": "fixed", "name":"User"}"""
        with pytest.raises(SchemaParseError):    # caught AvroException
            await sr_avro_serializer.serialize({}, schema=schema_no_size) 

        schema_no_name = """{"type": "fixed", "size": 3}"""
        with pytest.raises(SchemaParseError):    # caught SchemaParseError
            await sr_avro_serializer.serialize({}, schema=schema_no_name) 

        schema_wrong_name = """{"type": "fixed", "name": 1, "size": 3}"""
        with pytest.raises(SchemaParseError):    # caught SchemaParseError
            await sr_avro_serializer.serialize({}, schema=schema_wrong_name) 

        schema_wrong_namespace = """{"type": "fixed", "name": "User", "size": 3, "namespace": 1}"""
        with pytest.raises(SchemaParseError):    # caught SchemaParseError
            await sr_avro_serializer.serialize({}, schema=schema_wrong_namespace) 

    ######################### type unspecified #########################

    @SchemaRegistryPowerShellPreparer()
    async def test_parse_invalid_type(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        schema_no_type = """{
            "name": "User",
            "namespace":"example.avro",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(SchemaParseError):    # caught avro SchemaParseError    
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_no_type) 

        schema_wrong_type_type = """{
            "name":"User",
            "type":1,
            "namespace":"example.avro",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_wrong_type_type) 

    ######################### RECORD SCHEMA #########################

    @SchemaRegistryPowerShellPreparer()
    async def test_parse_record_name(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        schema_name_has_dot = """{
            "namespace": "thrownaway",
            "name":"User.avro",
            "type":"record",
            "fields":[{"name":"name","type":"string"}]
        }"""
        encoded_schema = await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_name_has_dot) 
        schema_id = encoded_schema[4:36].decode("utf-8")
        registered_schema = await sr_client.get_schema(schema_id)
        decoded_registered_schema = json.loads(registered_schema.definition)

        assert decoded_registered_schema["name"] == "User.avro"
        assert decoded_registered_schema["namespace"] == "thrownaway"

        schema_name_no_namespace = """{
            "name":"User",
            "type":"record",
            "fields":[{"name":"name","type":"string"}]
        }"""
        encoded_schema = await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_name_no_namespace) 
        schema_id = encoded_schema[4:36].decode("utf-8")
        registered_schema = await sr_client.get_schema(schema_id)
        decoded_registered_schema = json.loads(registered_schema.definition)

        assert decoded_registered_schema["name"] == "User"
        assert "namespace" not in decoded_registered_schema

        schema_invalid_fullname = """{
            "name":"abc",
            "type":"record",
            "namespace":"9example.avro",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_invalid_fullname) 

        schema_invalid_name_in_fullname = """{
            "name":"1abc",
            "type":"record",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_invalid_name_in_fullname) 

        schema_invalid_name_reserved_type = """{
            "name":"record",
            "type":"record",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_invalid_name_reserved_type) 

        schema_wrong_type_name = """{
            "name":1,
            "type":"record",
            "namespace":"example.avro",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_wrong_type_name) 

        schema_no_name = """{
            "namespace":"example.avro",
            "type":"record",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_no_name) 

    @SchemaRegistryPowerShellPreparer()
    async def test_parse_error_schema_as_record(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        schema_error_type = """{
            "name":"User",
            "namespace":"example.avro.error",
            "type":"error",
            "fields":[{"name":"name","type":"string"}]
        }"""
        encoded_data = await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_error_type) 
        schema_id = encoded_data[4:36].decode("utf-8")
        registered_schema = await sr_client.get_schema(schema_id)
        decoded_registered_schema = json.loads(registered_schema.definition)
        assert decoded_registered_schema["type"] == "error"

    @SchemaRegistryPowerShellPreparer()
    async def test_parse_record_fields(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        schema_no_fields = """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record"
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_no_fields) 

        schema_wrong_type_fields = """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record"
            "fields": "hello"
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_wrong_type_fields) 

        schema_wrong_field_item_type = """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record"
            "fields": ["hello"]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_wrong_field_item_type) 

        schema_record_field_no_name= """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record",
            "fields":[{"type":"string"}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_record_field_no_name) 

        schema_record_field_wrong_type_name= """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record",
            "fields":[{"name": 1, "type":"string"}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_record_field_wrong_type_name) 

        schema_record_field_with_invalid_order = """{
            "name":"User",
            "namespace":"example.avro.order",
            "type":"record",
            "fields":[{"name":"name","type":"string","order":"fake_order"}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_record_field_with_invalid_order) 

        schema_record_duplicate_fields = """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record",
            "fields":[{"name":"name","type":"string"}, {"name":"name","type":"string"}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_record_duplicate_fields) 

        schema_field_type_invalid = """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record",
            "fields":[{"name":"name","type":1}]
        }"""
        with pytest.raises(SchemaParseError):
            await sr_avro_serializer.serialize({"name": u"Ben"}, schema=schema_field_type_invalid) 

    ################################################################# 
    #################### SERIALIZE AND DESERIALIZE ##################
    ################################################################# 

    @SchemaRegistryPowerShellPreparer()
    async def test_serialize_primitive(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        null_type = """{"type": "null"}"""
        encoded_data = await sr_avro_serializer.serialize(None, schema=null_type) 
        assert len(encoded_data) == 36  # assert no data encoded

    @SchemaRegistryPowerShellPreparer()
    async def test_serialize_record(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        # add below to schema later if possible
        # {"name":"example.innerrec","type":"record","fields":[{"name":"a","type":"int"}]},
        # {"name":"innerenum","type":"enum","symbols":["FOO", "BAR"]},
        # {"name":"innerarray","type":"array","items":"int"},
        # {"name":"innermap","type":"map","values":"int"},
        # {"name":"innerfixed","type":"fixed","size":74}
        schema_record = """{
            "name":"User",
            "namespace":"example.avro.populatedrecord",
            "type":"record",
            "fields":[
                {"name":"name","type":"string"},
                {"name":"age","type":"int"},
                {"name":"married","type":"boolean"},
                {"name":"height","type":"float"},
                {"name":"randb","type":"bytes"}
            ]
        }"""
        data = {
            "name": u"Ben",
            "age": 3,
            "married": False,
            "height": 13.5,
            "randb": b"\u00FF"
        }

        encoded_data = await sr_avro_serializer.serialize(data, schema=schema_record)
        decoded_data = await sr_avro_serializer.deserialize(encoded_data)
        assert decoded_data == data
