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
try:
    import jsonschema
except ImportError:
    pass
from typing import Mapping, Any

from azure.core.exceptions import ResourceNotFoundError
from azure.schemaregistry import SchemaRegistryClient, SchemaFormat
from azure.schemaregistry.encoder.jsonencoder import JsonSchemaEncoder, InvalidContentError, JsonSchemaDraftIdentifier
from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
    recorded_by_proxy,
)

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

DRAFT07_SCHEMA_JSON = {
    "$id": "https://example.com/persondraft07.schema.json",
    "$schema": "http://json-schema.org/draft-07/schema",
    "title": "PersonDraft07",
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
        },
        "org": {
            "type": "string",
            "description": "Organization name."
        }
    }
}
DRAFT07_SCHEMA_STR = json.dumps(DRAFT07_SCHEMA_JSON)

class TestJsonSchemaEncoder(AzureRecordedTestCase):

    def create_client(self, **kwargs) -> SchemaRegistryClient:
        fully_qualified_namespace = kwargs.pop("fully_qualified_namespace")
        credential = self.get_credential(SchemaRegistryClient)
        return self.create_client_from_credential(SchemaRegistryClient, credential, fully_qualified_namespace=fully_qualified_namespace)
    
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_sr_json_encoder_encode_decode_w_schema_id(self, **kwargs):
        schemaregistry_json_fully_qualified_namespace = kwargs.pop("schemaregistry_json_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)
        sr_json_encoder = JsonSchemaEncoder(
            client=sr_client, group_name=schemaregistry_group, validate=JsonSchemaDraftIdentifier.DRAFT2020_12
        )

        # pre-register schema
        schema_properties = sr_client.register_schema(schemaregistry_group, DRAFT2020_12_SCHEMA_JSON["title"], DRAFT2020_12_SCHEMA_STR, SchemaFormat.JSON)
        schema_id = schema_properties.id

        # encode + validate w/ schema_id
        dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
        encoded_message_content = sr_json_encoder.encode(dict_content, schema_id=schema_id)
        content_type = encoded_message_content["content_type"]
        encoded_content = encoded_message_content["content"]
        assert content_type.split("+")[0] == 'application/json;serialization=Json'
        assert content_type.split("+")[1] == schema_id

        # passing both schema + schema_id to encode raises error
        with pytest.raises(TypeError):
            encoded_message_content = sr_json_encoder.encode(dict_content, schema_id=schema_id, schema=DRAFT2020_12_SCHEMA_STR)

        # decode
        encoded_content_dict = {"content": encoded_content, "content_type": content_type}
        decoded_content = sr_json_encoder.decode(encoded_content_dict)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 7
        assert decoded_content["favorite_color"] == u"red"

        # bad content type when decoding raises error
        mime_type, schema_id = encoded_content_dict["content_type"].split("+")
        encoded_content_dict["content_type"] = "binary/fake+" + schema_id
        with pytest.raises(InvalidContentError) as e:
            decoded_content = sr_json_encoder.decode(encoded_content_dict)

        encoded_content_dict["content_type"] = 'a+b+c'
        with pytest.raises(InvalidContentError) as e:
            decoded_content = sr_json_encoder.decode(encoded_content_dict)


    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_sr_json_encoder_encode_schema_str(self, **kwargs):
        schemaregistry_json_fully_qualified_namespace = kwargs.pop("schemaregistry_json_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)
        sr_json_encoder = JsonSchemaEncoder(
            client=sr_client, group_name=schemaregistry_group, validate=JsonSchemaDraftIdentifier.DRAFT_07
        )

        # encoding without registering schema raises error
        dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red", "org": u"Azure"}
        with pytest.raises(ResourceNotFoundError):
            encoded_message_content = sr_json_encoder.encode(dict_content, schema=DRAFT07_SCHEMA_STR)

        # pre-register schema
        schema_properties = sr_client.register_schema(schemaregistry_group, DRAFT07_SCHEMA_JSON["title"], DRAFT07_SCHEMA_STR, SchemaFormat.JSON)
        schema_id = schema_properties.id

        # encode + validate w/ schema str
        encoded_message_content = sr_json_encoder.encode(dict_content, schema=DRAFT07_SCHEMA_STR)
        content_type = encoded_message_content["content_type"]
        assert content_type.split("+")[0] == 'application/json;serialization=Json'
        assert content_type.split("+")[1] == schema_id

        sr_client.close()
        sr_json_encoder.close()

        # use encoder w/o group_name to decode
        extra_sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)
        sr_json_encoder_no_group = JsonSchemaEncoder(client=extra_sr_client, validate=JsonSchemaDraftIdentifier.DRAFT_07)
        decoded_content = sr_json_encoder_no_group.decode(encoded_message_content)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 7
        assert decoded_content["favorite_color"] == u"red"
        assert decoded_content["org"] == u"Azure"

        # using encoder w/o group_name to encode raises error
        # group_name is used w/ schema to get_schema_id
        with pytest.raises(TypeError):
            encoded_message_content = sr_json_encoder_no_group.encode(dict_content, schema=DRAFT2020_12_SCHEMA_STR)

        sr_json_encoder_no_group.close()
        extra_sr_client.close()


    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_sr_json_encoder_encode_message_type(self, **kwargs):
        schemaregistry_json_fully_qualified_namespace = kwargs.pop("schemaregistry_json_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)
        sr_json_encoder = JsonSchemaEncoder(
            client=sr_client, group_name=schemaregistry_group, validate=JsonSchemaDraftIdentifier.DRAFT2020_12
        )

        # pre-register schema
        schema_properties = sr_client.register_schema(schemaregistry_group, DRAFT2020_12_SCHEMA_JSON["title"], DRAFT2020_12_SCHEMA_STR, SchemaFormat.JSON)
        schema_id = schema_properties.id
        dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}

        # message type that doesn't fit MessageType protocol
        class BadExample:
            def __init__(self, not_content):
                self.not_content = not_content

        # encoding invalid message_type raises error
        with pytest.raises(TypeError) as e:
            sr_json_encoder.encode({"name": u"Ben"}, schema_id=schema_id, message_type=BadExample) 
        assert "subtype of the MessageType" in (str(e.value))

        # decoding invalid message_type raises error
        bad_ex = BadExample('fake')
        with pytest.raises(TypeError) as e:    # caught TypeError
            sr_json_encoder.decode(message=bad_ex) 
        assert "subtype of the MessageType" in (str(e.value))

        # message type that fits MessageType protocol
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

        # encode/decode valid message_type
        # test that extra kwargs pass through to message_type constructor
        good_ex_obj = sr_json_encoder.encode(dict_content, schema_id=schema_id, message_type=GoodExample, extra='val') 
        decoded_content_obj = sr_json_encoder.decode(message=good_ex_obj)

        assert decoded_content_obj["name"] == u"Ben"
        assert decoded_content_obj["favorite_number"] == 7
        assert decoded_content_obj["favorite_color"] == u"red"
        sr_client.close()
        sr_json_encoder.close()


    @pytest.mark.skip('not allowing schema generation callable for now')
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_sr_json_encoder_encode_decode_with_generate_schema_callable(self, **kwargs):
        schemaregistry_json_fully_qualified_namespace = kwargs.pop("schemaregistry_json_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)
        sr_json_encoder = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, validate=JsonSchemaDraftIdentifier.DRAFT2020_12)

        from genson import SchemaBuilder
        def generate_schema(content: Mapping[str, Any]) -> Mapping[str, Any]:
            builder = SchemaBuilder()
            try:
                builder.add_object(content)
                schema = builder.to_schema()
                schema["title"] = "Example.PersonTitle"
                return schema
            except:
                raise ValueError('schema cannot be generated')

        # pre-register schema generated by callable
        dict_content = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
        schema = generate_schema(dict_content)
        schema_properties = sr_client.register_schema(schemaregistry_group, schema["title"], json.dumps(schema), SchemaFormat.JSON)
        schema_id = schema_properties.id

        # encode w/ callable + override default schema
        encoded_message_content = sr_json_encoder.encode(dict_content, schema=generate_schema)
        content_type = encoded_message_content["content_type"]
        encoded_content = encoded_message_content["content"]
        assert content_type.split("+")[0] == 'application/json;serialization=Json'
        assert content_type.split("+")[1] == schema_id

        # decode
        encoded_content_dict = {"content": encoded_content, "content_type": content_type}
        decoded_content = sr_json_encoder.decode(encoded_content_dict)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 7
        assert decoded_content["favorite_color"] == u"red"

        # invalid content for generating schema
        def invalid_content():
            pass

        with pytest.raises(InvalidContentError):
            encoded_message_content = sr_json_encoder.encode(invalid_content, schema=generate_schema)
        sr_json_encoder.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_sr_json_encoder_validate(self, **kwargs):
        schemaregistry_json_fully_qualified_namespace = kwargs.pop("schemaregistry_json_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_json_fully_qualified_namespace)

        # pre-register schema
        schema_properties = sr_client.register_schema(schemaregistry_group, DRAFT2020_12_SCHEMA_JSON["title"], DRAFT2020_12_SCHEMA_STR, SchemaFormat.JSON)
        schema_id = schema_properties.id
        
        # not passing in validate raises error
        with pytest.raises(TypeError):
            sr_json_encoder = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group)

        # invalid draft identifier raises error
        with pytest.raises(ValueError) as exc:
            sr_json_encoder = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, validate="http://json-schema.org/draft-01/schema")
        assert "not a supported identifier" in str(exc.value)

        # Draft 3/4 do not accept float for integer type
        dict_content = {"name": u"Ben", "favorite_number": 1.0, "favorite_color": u"red"}
        sr_json_encoder_d3 = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, validate=JsonSchemaDraftIdentifier.DRAFT_03)
        with pytest.raises(InvalidContentError) as exc:
            sr_json_encoder_d3.encode(dict_content, schema=DRAFT2020_12_SCHEMA_STR)
        assert isinstance(exc.value.__cause__, jsonschema.exceptions.ValidationError)
        assert exc.value.__cause__.message == "1.0 is not of type 'integer'"
        sr_json_encoder_d4 = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, validate=JsonSchemaDraftIdentifier.DRAFT_04)
        with pytest.raises(InvalidContentError) as exc:
            sr_json_encoder_d4.encode(dict_content, schema_id=schema_id)
        assert isinstance(exc.value.__cause__, jsonschema.exceptions.ValidationError)
        assert exc.value.__cause__.message == "1.0 is not of type 'integer'"

        # Draft 6+ does accept float for integer type + test passing str value
        sr_json_encoder_d6 = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, validate=JsonSchemaDraftIdentifier.DRAFT_06.value)
        encoded_message_content = sr_json_encoder_d6.encode(dict_content, schema=DRAFT2020_12_SCHEMA_STR)
        content_type = encoded_message_content["content_type"]
        assert content_type.split("+")[0] == 'application/json;serialization=Json'

        assert content_type.split("+")[1] == schema_id
        sr_json_encoder_d19 = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, validate=JsonSchemaDraftIdentifier.DRAFT2019_09)
        encoded_message_content = sr_json_encoder_d19.encode(dict_content, schema_id=schema_id)

        # decode w/ Draft 3/4 validation raises error
        with pytest.raises(InvalidContentError) as exc:
            sr_json_encoder_d3.decode(encoded_message_content)
        assert isinstance(exc.value.__cause__, jsonschema.exceptions.ValidationError)
        assert exc.value.__cause__.message == "1.0 is not of type 'integer'"
        with pytest.raises(InvalidContentError) as exc:
            sr_json_encoder_d4.decode(encoded_message_content)
        assert isinstance(exc.value.__cause__, jsonschema.exceptions.ValidationError)
        assert exc.value.__cause__.message == "1.0 is not of type 'integer'"

        # decode w/ Draft 6+ validation passes
        decoded_content = sr_json_encoder_d6.decode(encoded_message_content)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 1.0
        assert decoded_content["favorite_color"] == u"red"
        decoded_content = sr_json_encoder_d19.decode(encoded_message_content)
        assert decoded_content["name"] == u"Ben"
        assert decoded_content["favorite_number"] == 1.0
        assert decoded_content["favorite_color"] == u"red"

        # wrong data type, check with draft 7 validator
        sr_json_encoder_d7 = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, validate=JsonSchemaDraftIdentifier.DRAFT_07)
        dict_content_bad = {"name": u"Ben", "favorite_number": 7, "favorite_color": 7}
        with pytest.raises(InvalidContentError) as e:
            encoded_message_content = sr_json_encoder_d7.encode(dict_content_bad, schema=DRAFT2020_12_SCHEMA_STR)
        assert "schema_id" in e.value.details

        # "turn off" validation w/ callable, wrong data type isn't detected
        def callable_validate(content: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
            pass

        sr_json_encoder_no_validate = JsonSchemaEncoder(client=sr_client, group_name=schemaregistry_group, validate=callable_validate)
        dict_content_bad = {"name": u"Ben", "favorite_number": 7, "favorite_color": 7}
        encoded_message_content = sr_json_encoder_no_validate.encode(dict_content_bad, schema=DRAFT2020_12_SCHEMA_STR)
        sr_json_encoder_d3.close()
        sr_json_encoder_d4.close()
        sr_json_encoder_d6.close()
        sr_json_encoder_d7.close()
        sr_json_encoder_d19.close()
        sr_json_encoder_no_validate.close()
