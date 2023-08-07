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
import json
import pytest
import jsonschema
from genson import SchemaBuilder
from typing import Mapping, Any

from azure.schemaregistry import SchemaFormat
from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry.encoder.jsonencoder.aio import JsonSchemaEncoder
from azure.schemaregistry.encoder.jsonencoder import InvalidContentError, JsonSchemaDraftIdentifier

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async

SchemaRegistryEnvironmentVariableLoader = functools.partial(
    EnvironmentVariableLoader,
    "schemaregistry",
    schemaregistry_json_fully_qualified_namespace="fake_resource_json.servicebus.windows.net",
    schemaregistry_group="fakegroup"
)

DRAFT2020_12_SCHEMA_JSON = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Person",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Person's name."
        },
        "favorite_color": {
            "type": "string",
            "description": "Favorite color."
        },
        "favorite_number": {
            "description": "Favorite number.",
            "type": "integer",
        }
    }
}
DRAFT2020_12_SCHEMA_STR = json.dumps(DRAFT2020_12_SCHEMA_JSON)
DRAFT2020_12_SCHEMA_BYTES = DRAFT2020_12_SCHEMA_STR.encode()

class TestJsonSchemaEncoderAsync(AzureRecordedTestCase):

    def create_client(self, **kwargs):
        fully_qualified_namespace = kwargs.pop("fully_qualified_namespace")
        credential = self.get_credential(SchemaRegistryClient, is_async=True)
        return self.create_client_from_credential(SchemaRegistryClient, credential, fully_qualified_namespace=fully_qualified_namespace, is_async=True)

    @pytest.mark.asyncio
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_sr_json_encoder_encode_decode_with_str_schema(self, schemaregistry_json_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)
        sr_json_encoder = JsonSchemaEncoder(client=sr_client, validate=JsonSchemaDraftIdentifier.DRAFT2020_12)

        # pre-register schema
        schema_properties = await sr_client.register_schema(schemaregistry_group, DRAFT2020_12_SCHEMA_JSON["title"], DRAFT2020_12_SCHEMA_STR, SchemaFormat.JSON)
        schema_id = schema_properties.id

        # encode w/ str schema
        dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
        encoded_message_content = await sr_json_encoder.encode(dict_content, schema=schema_id)
        content_type = encoded_message_content["content_type"]
        encoded_content = encoded_message_content["content"]
        assert content_type.split("+")[0] == 'application/json'
        assert content_type.split("+")[1] == schema_id

        # decode
        encoded_content_dict = {"content": encoded_content, "content_type": content_type}
        decoded_content = await sr_json_encoder.decode(encoded_content_dict)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 7
        assert decoded_content["favorite_color"] == u"red"

        # bad content type
        mime_type, schema_id = encoded_content_dict["content_type"].split("+")
        encoded_content_dict["content_type"] = "binary/fake+" + schema_id
        with pytest.raises(InvalidContentError) as e:
            decoded_content = await sr_json_encoder.decode(encoded_content_dict)

        encoded_content_dict["content_type"] = 'a+b+c'
        with pytest.raises(InvalidContentError) as e:
            decoded_content = await sr_json_encoder.decode(encoded_content_dict)

        # check that JsonSchemaEncoder won't work with message types that don't follow protocols
        class BadExample:
            def __init__(self, not_content):
                self.not_content = not_content

        with pytest.raises(TypeError) as e:
            await sr_json_encoder.encode({"name": u"Ben"}, schema=DRAFT2020_12_SCHEMA_STR, message_type=BadExample) 
        assert "subtype of the MessageType" in (str(e.value))

        bad_ex = BadExample('fake')
        with pytest.raises(TypeError) as e:    # caught TypeError
           await sr_json_encoder.decode(message=bad_ex) 
        assert "subtype of the MessageType" in (str(e.value))

        # check that JsonSchemaEncoder will work with message types that follow protocols
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

        # test that extra kwargs pass through to message_type constructor
        good_ex_obj = await sr_json_encoder.encode(dict_content, schema=DRAFT2020_12_SCHEMA_STR, message_type=GoodExample, extra='val') 
        decoded_content_obj = await sr_json_encoder.decode(message=good_ex_obj)

        assert decoded_content_obj["name"] == u"Ben"
        assert decoded_content_obj["favorite_number"] == 7
        assert decoded_content_obj["favorite_color"] == u"red"
        await sr_client.close()
        await sr_json_encoder.close()

        # no group_name passed into constructor, check encode fails, but decode works
        extra_sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)
        sr_json_encoder_no_group = JsonSchemaEncoder(client=extra_sr_client, auto_register=True)
        decoded_content = await sr_json_encoder_no_group.decode(encoded_message_content)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 7
        assert decoded_content["favorite_color"] == u"red"
        with pytest.raises(TypeError):
            encoded_message_content = await sr_json_encoder_no_group.encode(dict_content, schema=DRAFT2020_12_SCHEMA_STR)
        await sr_json_encoder_no_group.close()
        await extra_sr_client.close()

    @pytest.mark.asyncio
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_sr_json_encoder_encode_decode_with_bytes_schema(self, schemaregistry_json_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)
        # pass default schema
        sr_json_encoder = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, schema=DRAFT2020_12_SCHEMA_BYTES)

        # register schema first
        schema_properties = await sr_client.register_schema(schemaregistry_group, DRAFT2020_12_SCHEMA_JSON["title"], DRAFT2020_12_SCHEMA_STR, SchemaFormat.JSON)
        schema_id = schema_properties.id

        # encode w/ bytes schema
        dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
        encoded_message_content = await sr_json_encoder.encode(dict_content)
        content_type = encoded_message_content["content_type"]
        encoded_content = encoded_message_content["content"]
        assert content_type.split("+")[0] == 'application/json'
        assert content_type.split("+")[1] == schema_id

        # decode
        encoded_content_dict = {"content": encoded_content, "content_type": content_type}
        decoded_content = await sr_json_encoder.decode(encoded_content_dict)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 7
        assert decoded_content["favorite_color"] == u"red"
        await sr_json_encoder.close()

    @pytest.mark.asyncio
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_sr_json_encoder_encode_decode_with_generate_schema_callable(self, schemaregistry_json_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)
        sr_json_encoder = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, schema=DRAFT2020_12_SCHEMA_BYTES)

        def generate_schema(content: Mapping[str, Any]) -> Mapping[str, Any]:
            builder = SchemaBuilder()
            try:
                builder.add_object(content)
                schema = builder.to_schema()
                schema["title"] = "Example.PersonTitle"
                return schema
            except:
                raise ValueError('schema cannot be generated')

        # encode w/ callable + override default schema
        dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
        encoded_message_content = await sr_json_encoder.encode(dict_content, schema=generate_schema)
        content_type = encoded_message_content["content_type"]
        encoded_content = encoded_message_content["content"]
        assert content_type.split("+")[0] == 'application/json'
        assert content_type.split("+")[1] is not None

        # invalid content for generating schema
        def invalid_content():
            pass

        with pytest.raises(InvalidSchemaError):
            encoded_message_content = await sr_json_encoder.encode(invalid_content, schema=generate_schema)

        # decode
        encoded_content_dict = {"content": encoded_content, "content_type": content_type}
        decoded_content = await sr_json_encoder.decode(encoded_content_dict)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 7
        assert decoded_content["favorite_color"] == u"red"
        await sr_json_encoder.close()

    @pytest.mark.asyncio
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_sr_json_encoder_validate_content(self, schemaregistry_json_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)

        def default_validate(content: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
            jsonschema.Draft4Validator(schema).validate(content)

        sr_json_encoder = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, validate=default_validate)

        # encode w/ validation
        dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
        encoded_message_content = await sr_json_encoder.encode(dict_content, schema=DRAFT2020_12_SCHEMA_STR)
        content_type = encoded_message_content["content_type"]
        encoded_content = encoded_message_content["content"]
        assert content_type.split("+")[0] == 'application/json'
        assert content_type.split("+")[1] is not None

        # decode w/ validation
        encoded_content_dict = {"content": encoded_content, "content_type": content_type}
        decoded_content = await sr_json_encoder.decode(encoded_content_dict)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 7
        assert decoded_content["favorite_color"] == u"red"

        # wrong data type, check with validation
        dict_content_bad = {"name": u"Ben", "favorite_number": 7, "favorite_color": 7}
        with pytest.raises(InvalidContentError) as e:
            encoded_message_content = await sr_json_encoder.encode(dict_content_bad, schema=DRAFT2020_12_SCHEMA_STR)
        assert "schema_id" in e.value.details

        # override validation, bad content isn't detected
        dict_content_bad = {"name": u"Ben", "favorite_number": 7, "favorite_color": 7}
        encoded_message_content = await sr_json_encoder.encode(dict_content_bad, schema=DRAFT2020_12_SCHEMA_STR, validate=False)
        await sr_json_encoder.close()
