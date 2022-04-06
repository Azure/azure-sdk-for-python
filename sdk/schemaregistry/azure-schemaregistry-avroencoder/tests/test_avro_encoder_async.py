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
from typing import Type
import pytest
import uuid
import json
from io import BytesIO
import pytest

import avro
from avro.errors import AvroTypeException


from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry.encoder.avroencoder.aio import AvroEncoder
from azure.schemaregistry.encoder.avroencoder import InvalidSchemaError, InvalidContentError

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async

SchemaRegistryEnvironmentVariableLoader = functools.partial(EnvironmentVariableLoader, "schemaregistry", schemaregistry_fully_qualified_namespace="fake_resource.servicebus.windows.net/", schemaregistry_group="fakegroup")

class TestAvroEncoderAsync(AzureRecordedTestCase):

    def create_client(self, **kwargs):
        fully_qualified_namespace = kwargs.pop("fully_qualified_namespace")
        credential = self.get_credential(SchemaRegistryClient, is_async=True)
        return self.create_client_from_credential(SchemaRegistryClient, credential, fully_qualified_namespace=fully_qualified_namespace, is_async=True)

    @pytest.mark.asyncio
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_basic_sr_avro_encoder_with_auto_register_schemas(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        async with sr_client:
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            schema_str = "{\"type\": \"record\", \"name\": \"User\", \"namespace\": \"example.avro\", \"fields\": [{\"type\": \"string\", \"name\": \"name\"}, {\"type\": [\"int\", \"null\"], \"name\": \"favorite_number\"}, {\"type\": [\"string\", \"null\"], \"name\": \"favorite_color\"}]}"
            schema = avro.schema.parse(schema_str)

            dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
            encoded_message_content = await sr_avro_encoder.encode(dict_content, schema=schema_str)
            content_type = encoded_message_content["content_type"]
            encoded_content = encoded_message_content["content"]

            # wrong data type
            dict_content_bad = {"name": u"Ben", "favorite_number": 7, "favorite_color": 7}
            with pytest.raises(InvalidContentError) as e:
                encoded_message_content = await sr_avro_encoder.encode(dict_content_bad, schema=schema_str)
            assert "schema_id" in e.value.details

            assert content_type.split("+")[0] == 'avro/binary'
            schema_properties = await sr_client.get_schema_properties(schemaregistry_group, schema.fullname, str(schema), "Avro")
            schema_id = schema_properties.id
            assert content_type.split("+")[1] == schema_id

            encoded_content_dict = {"content": encoded_content, "content_type": content_type}
            decoded_content = await sr_avro_encoder.decode(encoded_content_dict)
            assert decoded_content["name"] == u"Ben"
            assert decoded_content["favorite_number"] == 7
            assert decoded_content["favorite_color"] == u"red"

            # bad content type
            mime_type, schema_id = encoded_content_dict["content_type"].split("+")
            encoded_content_dict["content_type"] = "binary/fake+" + schema_id
            with pytest.raises(InvalidContentError) as e:
                decoded_content = await sr_avro_encoder.decode(encoded_content_dict)

            encoded_content_dict["content_type"] = 'a+b+c'
            with pytest.raises(InvalidContentError) as e:
                decoded_content = await sr_avro_encoder.decode(encoded_content_dict)

            # check that AvroEncoder won't work with message types that don't follow protocols
            class BadExample:
                def __init__(self, not_content):
                    self.not_content = not_content

            with pytest.raises(TypeError) as e:
                await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_str, message_type=BadExample) 
            assert "subtype of the MessageType" in (str(e.value))

            bad_ex = BadExample('fake')
            with pytest.raises(TypeError) as e:
                await sr_avro_encoder.decode(message=bad_ex) 
            assert "subtype of the MessageType" in (str(e.value))

            # check that AvroEncoder will work with message types that follow protocols
            class GoodExample:
                def __init__(self, content, **kwargs):
                    self.content = content
                    self.content_type = None
                    self.extra = kwargs.pop('extra', None)
                
                @classmethod
                def from_message_content(cls, content: bytes, content_type: str, **kwargs):
                    ge = cls(content)
                    ge.content_type = content_type
                    return ge

                def __message_content__(self):
                    return {"content": self.content, "content_type": self.content_type}

            good_ex_obj = await sr_avro_encoder.encode(dict_content, schema=schema_str, message_type=GoodExample, extra='val')
            decoded_content_obj = await sr_avro_encoder.decode(message=good_ex_obj)

            assert decoded_content_obj["name"] == u"Ben"
            assert decoded_content_obj["favorite_number"] == 7
            assert decoded_content_obj["favorite_color"] == u"red"

    @pytest.mark.asyncio
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_basic_sr_avro_encoder_without_auto_register_schemas(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        async with sr_client:
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            schema_str = "{\"type\": \"record\", \"name\": \"User\", \"namespace\": \"example.avro\", \"fields\": [{\"type\": \"string\", \"name\": \"name\"}, {\"type\": [\"int\", \"null\"], \"name\": \"favorite_number\"}, {\"type\": [\"string\", \"null\"], \"name\": \"favorite_color\"}]}"
            schema = avro.schema.parse(schema_str)

            dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
            encoded_message_content = await sr_avro_encoder.encode(dict_content, schema=schema_str)
            content_type = encoded_message_content["content_type"]
            encoded_content = encoded_message_content["content"]

            assert content_type.split("+")[0] == 'avro/binary'
            schema_properties = await sr_client.get_schema_properties(schemaregistry_group, schema.fullname, str(schema), "Avro")
            schema_id = schema_properties.id
            assert content_type.split("+")[1] == schema_id

            encoded_content_dict = {"content": encoded_content, "content_type": content_type}
            decoded_content = await sr_avro_encoder.decode(encoded_content_dict)
            assert decoded_content["name"] == u"Ben"
            assert decoded_content["favorite_number"] == 7
            assert decoded_content["favorite_color"] == u"red"

    @pytest.mark.asyncio
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_basic_sr_avro_encoder_decode_readers_schema(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""

        dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
        encoded_message_content = await sr_avro_encoder.encode(dict_content, schema=schema_str)
        content_type = encoded_message_content["content_type"]
        encoded_content = encoded_message_content["content"]

        # readers_schema with removed field
        readers_schema_remove_field = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]}]}"""
        encoded_content_dict = {"content": encoded_content, "content_type": content_type}
        decoded_content = await sr_avro_encoder.decode(encoded_content_dict, readers_schema=readers_schema_remove_field)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 7

        # readers_schema with extra field with default
        readers_schema_extra_field = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}, {"name":"favorite_city","type":["string","null"], "default": "Redmond"}]}"""
        encoded_content_dict = {"content": encoded_content, "content_type": content_type}
        decoded_content = await sr_avro_encoder.decode(encoded_content_dict, readers_schema=readers_schema_extra_field)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 7
        assert decoded_content["favorite_color"] == "red"
        assert decoded_content["favorite_city"] == "Redmond"

        # readers_schema with changed name results in error
        readers_schema_change_name = """{"namespace":"fakeexample.avro","type":"record","name":"fake_user","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        with pytest.raises(InvalidSchemaError) as e:
            decoded_content = await sr_avro_encoder.decode(encoded_content_dict, readers_schema=readers_schema_change_name)
        assert "Incompatible schemas" in e.value.message
        assert "schema_id" in e.value.details
        assert "schema_definition" in e.value.details

        # invalid readers_schema
        invalid_schema = {
            "name":"User",
            "type":"record",
            "namespace":"example.avro",
            "fields":[{"name":"name","type":"string"}]
        }
        invalid_schema_string = "{}".format(invalid_schema)
        with pytest.raises(InvalidSchemaError) as e:
            decoded_content = await sr_avro_encoder.decode(encoded_content_dict, readers_schema=invalid_schema_string)
        assert "Invalid schema" in e.value.message
        assert "schema_id" in e.value.details
        assert "schema_definition" in e.value.details
    
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_basic_sr_avro_encoder_with_request_options(self, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop("schemaregistry_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""

        dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
        with pytest.raises(TypeError) as e:
            encoded_message_content = await sr_avro_encoder.encode(dict_content, schema=schema_str, request_options={"fake_kwarg": True})
        assert 'request() got an unexpected keyword' in str(e.value)
        encoded_message_content = await sr_avro_encoder.encode(dict_content, schema=schema_str)
        content_type = encoded_message_content["content_type"]
        encoded_content = encoded_message_content["content"]

        encoded_content_dict = {"content": encoded_content, "content_type": content_type}
        with pytest.raises(TypeError) as e:
            decoded_content = await sr_avro_encoder.decode(encoded_content_dict, request_options={"fake_kwarg": True})
        assert 'request() got an unexpected keyword' in str(e.value)

    ################################################################# 
    ######################### PARSE SCHEMAS #########################
    ################################################################# 

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_parse_invalid_json_string(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)
        invalid_schema = {
            "name":"User",
            "type":"record",
            "namespace":"example.avro",
            "fields":[{"name":"name","type":"string"}]
        }
        invalid_schema_string = "{}".format(invalid_schema)
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=invalid_schema_string) 

    ######################### PRIMITIVES #########################

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_parse_primitive_types(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        primitive_string = "string"
        with pytest.raises(InvalidSchemaError) as e:
            await sr_avro_encoder.encode("hello", schema=primitive_string) 

    ######################### type fixed #########################

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_parse_fixed_types(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        # avro bug: should give warning from IgnoredLogicalType error since precision < 0
        #fixed_type_ignore_logical_type_error = """{"type": "fixed", "size": 4, "namespace":"example.avro", "name":"User", "precision": -1}"""
        #await sr_avro_encoder.encode({}, schema=fixed_type_ignore_logical_type_error) 

        schema_no_size = """{"type": "fixed", "name":"User"}"""
        with pytest.raises(InvalidSchemaError):    # caught AvroException
            await sr_avro_encoder.encode({}, schema=schema_no_size) 

        schema_no_name = """{"type": "fixed", "size": 3}"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({}, schema=schema_no_name) 

        schema_wrong_name = """{"type": "fixed", "name": 1, "size": 3}"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({}, schema=schema_wrong_name) 

        schema_wrong_namespace = """{"type": "fixed", "name": "User", "size": 3, "namespace": 1}"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({}, schema=schema_wrong_namespace) 

    ######################### type unspecified #########################

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_parse_invalid_type(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        schema_no_type = """{
            "name": "User",
            "namespace":"example.avro",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_no_type) 

        schema_wrong_type_type = """{
            "name":"User",
            "type":1,
            "namespace":"example.avro",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_wrong_type_type) 

    ######################### RECORD SCHEMA #########################

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_parse_record_name(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        schema_name_has_dot = """{
            "namespace": "thrownaway",
            "name":"User.avro",
            "type":"record",
            "fields":[{"name":"name","type":"string"}]
        }"""
        encoded_schema = await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_name_has_dot) 
        schema_id = encoded_schema["content_type"].split("+")[1]
        registered_schema = await sr_client.get_schema(schema_id)
        decoded_registered_schema = json.loads(registered_schema.definition)

        assert decoded_registered_schema["name"] == "User.avro"
        assert decoded_registered_schema["namespace"] == "thrownaway"

        schema_name_no_namespace = """{
            "name":"User",
            "type":"record",
            "fields":[{"name":"name","type":"string"}]
        }"""
        encoded_schema = await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_name_no_namespace) 
        schema_id = encoded_schema["content_type"].split("+")[1]
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
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_invalid_fullname) 

        schema_invalid_name_in_fullname = """{
            "name":"1abc",
            "type":"record",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_invalid_name_in_fullname) 

        schema_invalid_name_reserved_type = """{
            "name":"record",
            "type":"record",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_invalid_name_reserved_type) 

        schema_wrong_type_name = """{
            "name":1,
            "type":"record",
            "namespace":"example.avro",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_wrong_type_name) 

        schema_no_name = """{
            "namespace":"example.avro",
            "type":"record",
            "fields":[{"name":"name","type":"string"}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_no_name) 

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_parse_error_schema_as_record(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        schema_error_type = """{
            "name":"User",
            "namespace":"example.avro.error",
            "type":"error",
            "fields":[{"name":"name","type":"string"}]
        }"""
        encoded_message_content = await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_error_type) 
        schema_id = encoded_message_content["content_type"].split("+")[1]
        registered_schema = await sr_client.get_schema(schema_id)
        decoded_registered_schema = json.loads(registered_schema.definition)
        assert decoded_registered_schema["type"] == "error"

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_parse_record_fields(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        schema_no_fields = """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record"
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_no_fields) 

        schema_wrong_type_fields = """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record"
            "fields": "hello"
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_wrong_type_fields) 

        schema_wrong_field_item_type = """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record"
            "fields": ["hello"]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_wrong_field_item_type) 

        schema_record_field_no_name= """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record",
            "fields":[{"type":"string"}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_record_field_no_name) 

        schema_record_field_wrong_type_name= """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record",
            "fields":[{"name": 1, "type":"string"}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_record_field_wrong_type_name) 

        schema_record_field_with_invalid_order = """{
            "name":"User",
            "namespace":"example.avro.order",
            "type":"record",
            "fields":[{"name":"name","type":"string","order":"fake_order"}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_record_field_with_invalid_order) 

        schema_record_duplicate_fields = """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record",
            "fields":[{"name":"name","type":"string"}, {"name":"name","type":"string"}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_record_duplicate_fields) 

        schema_field_type_invalid = """{
            "name":"User",
            "namespace":"example.avro",
            "type":"record",
            "fields":[{"name":"name","type":1}]
        }"""
        with pytest.raises(InvalidSchemaError):
            await sr_avro_encoder.encode({"name": u"Ben"}, schema=schema_field_type_invalid) 

    ################################################################# 
    #################### ENCODE AND DECODE ##########################
    ################################################################# 

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_encode_primitive(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

        null_type = """{"type": "null"}"""
        encoded_message_content = await sr_avro_encoder.encode(None, schema=null_type) 
        assert len(encoded_message_content["content"]) == 0 # assert no content encoded

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_encode_record(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        sr_avro_encoder = AvroEncoder(client=sr_client, group_name=schemaregistry_group, auto_register=True)

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
        content = {
            "name": u"Ben",
            "age": 3,
            "married": False,
            "height": 13.5,
            "randb": b"\u00FF"
        }

        encoded_message_content = await sr_avro_encoder.encode(content, schema=schema_record)
        decoded_content = await sr_avro_encoder.decode(encoded_message_content)
        assert decoded_content == content
