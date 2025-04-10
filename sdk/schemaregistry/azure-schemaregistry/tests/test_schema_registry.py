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
import os
import functools
import pytest
import json

from azure.schemaregistry import SchemaRegistryClient, SchemaFormat
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from mock_transport import MockResponse, MockTransport

# TODO: add protobuf env var for live testing when protobuf changes have been rolled out
is_livetest = str(os.getenv("AZURE_TEST_RUN_LIVE")).lower()
sr_namespaces = {
    "schemaregistry_avro_fully_qualified_namespace": "fake_resource_avro.servicebus.windows.net",
    "schemaregistry_json_fully_qualified_namespace": "fake_resource_json.servicebus.windows.net",
    "schemaregistry_custom_fully_qualified_namespace": "fake_resource_custom.servicebus.windows.net",
    "schemaregistry_group": "fakegroup",
}
# if is_livetest != "true":
#    sr_namespaces["schemaregistry_protobuf_fully_qualified_namespace"] = "fake_resource_protobuf.servicebus.windows.net"

SchemaRegistryEnvironmentVariableLoader = functools.partial(
    EnvironmentVariableLoader, "schemaregistry", **sr_namespaces
)
AVRO_SCHEMA_STR = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
JSON_SCHEMA = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "User",
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Name"},
        "favoriteNumber": {"type": "integer", "description": "Favorite positive number", "minimum": 0},
        "favoriteColor": {
            "description": "Favorite color",
            "type": "string",
        },
    },
}
JSON_SCHEMA_STR = json.dumps(JSON_SCHEMA, separators=(",", ":"))
CUSTOM_SCHEMA_STR = "My favorite color is yellow."
# current_path = os.getcwd()
# "\\" for Windows, "/" for Linux
# current_folder = current_path.split("\\")[-1].split("/")[-1]
# if current_folder == "tests":
#    proto_file = os.path.join(os.getcwd(), "person.proto")
# else:  # current_folder == "azure-schemaregistry"
#    proto_file = os.path.join(os.getcwd(), "tests", "person.proto")
#
# with open(proto_file, "r") as f:
#    PROTOBUF_SCHEMA_STR = f.read()

AVRO_FORMAT = "Avro"
JSON_FORMAT = "Json"
CUSTOM_FORMAT = "Custom"
# PROTOBUF_FORMAT = "Protobuf"

avro_args = (AVRO_FORMAT, AVRO_SCHEMA_STR)
json_args = (JSON_FORMAT, JSON_SCHEMA_STR)
custom_args = (CUSTOM_FORMAT, CUSTOM_SCHEMA_STR)
# protobuf_args = (PROTOBUF_FORMAT, PROTOBUF_SCHEMA_STR)

# TODO: add protobuf schema group to arm template + enable livetests
format_params = [avro_args, json_args, custom_args]
format_ids = [AVRO_FORMAT, JSON_FORMAT, CUSTOM_FORMAT]
# if is_livetest != "true":  # protobuf changes have not been rolled out
#    format_params.append(protobuf_args)
#    format_ids.append(PROTOBUF_FORMAT)

# TODO: remove when protobuf changes have been rolled out
format_params_no_protobuf = [avro_args, json_args, custom_args]
format_ids_no_protobuf = [AVRO_FORMAT, JSON_FORMAT, CUSTOM_FORMAT]


class ArgPasser:
    def __call__(self, fn):
        def _preparer(test_class, format, schema_str, **kwargs):
            fn(test_class, format, schema_str, **kwargs)

        return _preparer


class TestSchemaRegistry(AzureRecordedTestCase):
    def create_client(self, **kwargs):
        fully_qualified_namespace = kwargs.pop("fully_qualified_namespace")
        credential = self.get_credential(SchemaRegistryClient)
        return self.create_client_from_credential(
            SchemaRegistryClient, credential, fully_qualified_namespace=fully_qualified_namespace
        )

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_schema_basic(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name(f"test-schema-basic-{format.lower()}")
        schema_properties = client.register_schema(schemaregistry_group, name, schema_str, format, logging_enable=True)

        assert schema_properties.id is not None
        assert schema_properties.format == format

        returned_schema = client.get_schema(schema_id=schema_properties.id, logging_enable=True)

        assert returned_schema.properties.id == schema_properties.id
        assert returned_schema.properties.format == format
        assert returned_schema.properties.group_name == schemaregistry_group
        assert returned_schema.properties.name == name
        assert returned_schema.definition.replace("\/", "/") == schema_str

        returned_version_schema = client.get_schema(
            group_name=schemaregistry_group, name=name, version=schema_properties.version, logging_enable=True
        )

        with pytest.raises(TypeError) as exc:
            client.get_schema(group_name=schemaregistry_group, name=name, logging_enable=True)
        assert "Missing" in str(exc)

        assert returned_version_schema.properties.id == schema_properties.id
        assert returned_version_schema.properties.format == format
        assert returned_version_schema.properties.group_name == schemaregistry_group
        assert returned_version_schema.properties.name == name
        assert returned_version_schema.properties.version == schema_properties.version
        assert returned_version_schema.definition.replace("\/", "/") == schema_str

        returned_schema_properties = client.get_schema_properties(
            schemaregistry_group, name, schema_str, format.upper(), logging_enable=True
        )

        assert returned_schema_properties.id == schema_properties.id
        assert returned_schema_properties.format == format
        assert returned_schema.properties.group_name == schemaregistry_group
        assert returned_schema.properties.name == name

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_schema_update(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name(f"test-schema-update-{format.lower()}")
        schema_properties = client.register_schema(schemaregistry_group, name, schema_str, format)

        assert schema_properties.id is not None
        assert schema_properties.format == format

        schema_str_new = schema_str.replace("color", "food").replace("Color", "Food")  # for JSON and Avro string case
        new_schema_properties = client.register_schema(schemaregistry_group, name, schema_str_new, format)

        assert new_schema_properties.id is not None
        assert new_schema_properties.format == format
        assert new_schema_properties.group_name == schemaregistry_group
        assert new_schema_properties.name == name

        new_schema = client.get_schema(schema_id=new_schema_properties.id)

        assert new_schema.properties.id != schema_properties.id
        assert new_schema.properties.id == new_schema_properties.id
        assert new_schema.definition.replace("\/", "/") == schema_str_new
        assert new_schema.properties.format == format
        assert new_schema.properties.group_name == schemaregistry_group
        assert new_schema.properties.name == name

        old_schema = client.get_schema(
            group_name=schemaregistry_group, name=name, version=schema_properties.version, logging_enable=True
        )

        assert old_schema.properties.id != new_schema_properties.id
        assert old_schema.properties.id == schema_properties.id
        assert old_schema.definition.replace("\/", "/") == schema_str
        assert old_schema.properties.format == format
        assert old_schema.properties.group_name == schemaregistry_group
        assert old_schema.properties.name == name
        assert old_schema.properties.version == schema_properties.version

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_schema_same_twice(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name(f"test-schema-twice-{format.lower()}")
        schema_properties = client.register_schema(schemaregistry_group, name, schema_str, format)
        schema_properties_second = client.register_schema(schemaregistry_group, name, schema_str, format)
        assert schema_properties.id == schema_properties_second.id

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_schema_negative_wrong_credential(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        credential = ClientSecretCredential(tenant_id="fake", client_id="fake", client_secret="fake")
        client = SchemaRegistryClient(
            fully_qualified_namespace=schemaregistry_fully_qualified_namespace, credential=credential
        )
        name = self.get_resource_name(f"test-schema-negative-{format.lower()}")
        with pytest.raises(ClientAuthenticationError):
            client.register_schema(schemaregistry_group, name, schema_str, format)

    @pytest.mark.live_test_only
    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_schema_negative_wrong_endpoint(self, format, schema_str, **kwargs):
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace="fake.servicebus.windows.net")
        name = self.get_resource_name(f"test-schema-nonexist-{format.lower()}")
        # accepting both errors for now due to: https://github.com/Azure/azure-sdk-tools/issues/2907
        with pytest.raises((ServiceRequestError, HttpResponseError)) as exc_info:
            client.register_schema(schemaregistry_group, name, schema_str, format)

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_schema_negative_no_schema(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        with pytest.raises(HttpResponseError):
            client.get_schema("a")

        with pytest.raises(HttpResponseError):
            client.get_schema("a" * 32)

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_schema_negative_no_schema_version(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name(f"test-schema-negative-version-{format.lower()}")
        schema_properties = client.register_schema(schemaregistry_group, name, schema_str, format)
        version = schema_properties.version + 1
        with pytest.raises(HttpResponseError):
            client.get_schema(group_name=schemaregistry_group, name=name, version=version)

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_register_schema_errors(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = "test-schema"

        with pytest.raises(ValueError) as e:
            client.register_schema(None, name, schema_str, format)

        with pytest.raises(ValueError) as e:
            client.register_schema(schemaregistry_group, None, schema_str, format)

        with pytest.raises(HttpResponseError) as e:
            client.register_schema(schemaregistry_group, name, None, format)
        assert e.value.error.code == "InvalidRequest"
        assert e.value.status_code == 400
        assert e.value.reason == "Bad Request"

        with pytest.raises(AttributeError) as e:
            client.register_schema(schemaregistry_group, name, schema_str, None)

        with pytest.raises(HttpResponseError) as e:
            client.register_schema(schemaregistry_group, name, schema_str, "invalid-format")
        assert e.value.error.code == "InvalidSchemaType"
        assert e.value.status_code == 415
        assert e.value.reason == "Unsupported Media Type"

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_get_schema_properties_errors(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = "test-schema"

        with pytest.raises(ValueError) as e:
            client.get_schema_properties(None, name, schema_str, format)

        with pytest.raises(ValueError) as e:
            client.get_schema_properties(schemaregistry_group, None, schema_str, format)

        with pytest.raises(HttpResponseError) as e:
            client.get_schema_properties(schemaregistry_group, name, None, format)
        assert e.value.error.code == "InvalidRequest"
        assert e.value.status_code == 400
        assert e.value.reason == "Bad Request"

        with pytest.raises(AttributeError) as e:
            client.get_schema_properties(schemaregistry_group, name, schema_str, None)

        with pytest.raises(HttpResponseError) as e:
            client.get_schema_properties(schemaregistry_group, name, schema_str, "invalid-format")
        assert e.value.error.code == "InvalidSchemaType"
        assert e.value.status_code == 415
        assert e.value.reason == "Unsupported Media Type"

        with pytest.raises(HttpResponseError) as e:
            client.get_schema_properties(schemaregistry_group, "never-registered", schema_str, format)
        assert e.value.error.code == "ItemNotFound"
        assert e.value.status_code == 404
        assert e.value.reason == "Not Found"

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_get_schema_errors(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        with pytest.raises(ValueError) as e:
            client.get_schema(None)

        with pytest.raises(HttpResponseError) as e:
            client.get_schema("fakeschemaid")
        assert e.value.error.code == "InvalidRequest"
        assert e.value.status_code == 400
        assert e.value.reason == "Bad Request"

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy
    def test_schema_apiversion(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        schemaregistry_group = kwargs.pop("schemaregistry_group")

        apiversion_2021_10 = "2021-10"
        client_2021_10 = self.create_client(
            fully_qualified_namespace=schemaregistry_fully_qualified_namespace, api_version=apiversion_2021_10
        )
        name = self.get_resource_name(f"test-schema-apiversion-{format.lower()}")

        schema_properties = client_2021_10.register_schema(
            schemaregistry_group, name, schema_str, format, logging_enable=True
        )

        assert schema_properties.id is not None
        assert schema_properties.format == format

        apiversion_2022_10 = "2022-10"
        client_2022_10 = self.create_client(
            fully_qualified_namespace=schemaregistry_fully_qualified_namespace, api_version=apiversion_2022_10
        )
        schema_properties = client_2022_10.register_schema(
            schemaregistry_group, name, schema_str, format, logging_enable=True
        )

        assert schema_properties.id is not None
        assert schema_properties.format == format

    @SchemaRegistryEnvironmentVariableLoader()
    # TODO: add back all after protobuf changes have been rolled out
    @pytest.mark.parametrize("format, schema_str", format_params_no_protobuf, ids=format_ids_no_protobuf)
    @ArgPasser()
    @recorded_by_proxy
    def test_schema_internal_ops_list(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(
            f"schemaregistry_{format.lower()}_fully_qualified_namespace"
        )
        schemaregistry_group = kwargs.pop("schemaregistry_group")

        sr_client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        schema_groups = sr_client._generated_client._list_schema_groups()
        for group in schema_groups:
            assert group == schemaregistry_group

        name = "test-schema1"
        sr_client.register_schema(schemaregistry_group, name, schema_str, format)

        schema_versions = sr_client._generated_client._list_schema_versions(schemaregistry_group, name)
        versions = []
        for version in schema_versions:
            versions.append(version)

        assert len(versions) > 0

    def test_get_schema_unknown_content_type(self, **kwargs):

        # test known content type first
        avro_schema_id = "avro_schema_id_123"
        avro_schema_name = "avro_name"
        avro_group_name = "avro_group"
        avro_schema_version = "1"
        avro_content_type = "application/json; serialization=Avro"
        transport = MockTransport(
            response=MockResponse(
                schema_id=avro_schema_id,
                schema_name=avro_schema_name,
                schema_group_name=avro_group_name,
                schema_version=avro_schema_version,
                content_type=avro_content_type,
            )
        )
        mock_fqn = f"schemaregistry_fqn"
        credential = self.get_credential(SchemaRegistryClient)
        mock_client = SchemaRegistryClient(
            fully_qualified_namespace=mock_fqn, credential=credential, transport=transport
        )

        with mock_client:

            # content type should return SchemaFormat enum
            schema = mock_client.get_schema(avro_schema_id)
            assert schema.properties.format == SchemaFormat.AVRO

            # get unknown schema with content type of format "application/json; serialization=<format>"
            foo_schema_id = "foo_schema_id_123"
            foo_schema_name = "foo_name"
            foo_group_name = "foo_group"
            foo_schema_version = "1"
            foo_content_type = "application/json; serialization=Foo"
            transport._response = MockResponse(
                schema_id=foo_schema_id,
                schema_name=foo_schema_name,
                schema_group_name=foo_group_name,
                schema_version=foo_schema_version,
                content_type=foo_content_type,
            )
            # get unknown schema by id should return format of the content type string
            schema = mock_client.get_schema(foo_schema_id)
            assert schema.properties.format == foo_content_type
            # get unknown schema by version should return format of the content type string
            schema = mock_client.get_schema(group_name=foo_group_name, name=foo_schema_name, version=foo_schema_version)
            assert schema.properties.format == foo_content_type

            # get unknown schema with content type of format "contenttype/<unknown>"
            bar_schema_id = "bar_schema_id_123"
            bar_schema_name = "bar_name"
            bar_group_name = "bar_group"
            bar_schema_version = "1"
            bar_content_type = "contenttype/bar"
            transport._response = MockResponse(
                schema_id=bar_schema_id,
                schema_name=bar_schema_name,
                schema_group_name=bar_group_name,
                schema_version=bar_schema_version,
                content_type=bar_content_type,
            )
            schema = mock_client.get_schema(bar_schema_id)

            # get unknown schema by id should return format of the content type string
            schema = mock_client.get_schema(bar_schema_id)
            assert schema.properties.format == bar_content_type
            # get unknown schema by version should return format of the content type string
            schema = mock_client.get_schema(group_name=bar_group_name, name=bar_schema_name, version=bar_schema_version)
            assert schema.properties.format == bar_content_type
