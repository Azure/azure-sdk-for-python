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

from azure.schemaregistry.aio import SchemaRegistryClient
from azure.identity.aio import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async

SchemaRegistryEnvironmentVariableLoader = functools.partial(
    EnvironmentVariableLoader,
    "schemaregistry",
    schemaregistry_avro_fully_qualified_namespace="fake_resource_avro.servicebus.windows.net",
    schemaregistry_json_fully_qualified_namespace="fake_resource_json.servicebus.windows.net",
    schemaregistry_custom_fully_qualified_namespace="fake_resource_custom.servicebus.windows.net",
    schemaregistry_group="fakegroup"
)
AVRO_SCHEMA_STR = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
JSON_SCHEMA = {
    "$id": "https://example.com/person.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "User",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The person's name."
        },
        "favoriteNumber": {
            "type": "integer",
            "description": "The person's favorite positive number.",
            "minimum": 0
        },
        "favoriteColor": {
            "description": "The person's favorite color",
            "type": "string",
        }
    }
}
JSON_SCHEMA_STR = json.dumps(JSON_SCHEMA, separators=(",", ":"))
CUSTOM_SCHEMA_STR = "My favorite color is yellow."

AVRO_FORMAT = "Avro"
JSON_FORMAT = "Json"
CUSTOM_FORMAT = "Custom"

avro_args = (AVRO_FORMAT, AVRO_SCHEMA_STR)
json_args = (JSON_FORMAT, JSON_SCHEMA_STR)
custom_args = (CUSTOM_FORMAT, CUSTOM_SCHEMA_STR)

format_params = [avro_args, json_args, custom_args]
format_ids = [AVRO_FORMAT, JSON_FORMAT, CUSTOM_FORMAT]

class ArgPasser:
    def __call__(self, fn):
        async def _preparer(test_class, format, schema_str, **kwargs):
            await fn(test_class, format, schema_str, **kwargs)
        return _preparer

class TestSchemaRegistryAsync(AzureRecordedTestCase):

    def create_client(self, **kwargs):
        fully_qualified_namespace = kwargs.pop("fully_qualified_namespace")
        credential = self.get_credential(SchemaRegistryClient, is_async=True)
        return self.create_client_from_credential(SchemaRegistryClient, credential, fully_qualified_namespace=fully_qualified_namespace, is_async=True)

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy_async
    async def test_schema_basic_async(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(f"schemaregistry_{format.lower()}_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        async with client:
            name = self.get_resource_name(f"test-schema-basic-async-{format.lower()}")
            schema_properties = await client.register_schema(schemaregistry_group, name, schema_str, format.upper(), logging_enable=True)

            assert schema_properties.id is not None
            assert schema_properties.format == format

            returned_schema = await client.get_schema(schema_id=schema_properties.id, logging_enable=True)

            assert returned_schema.properties.id == schema_properties.id
            assert returned_schema.properties.format == format
            assert returned_schema.properties.group_name == schemaregistry_group
            assert returned_schema.properties.name == name
            assert returned_schema.definition.replace("\/", "/") == schema_str

            returned_version_schema = await client.get_schema(group_name=schemaregistry_group, name=name, version=schema_properties.version, logging_enable=True)

            assert returned_version_schema.properties.id == schema_properties.id
            assert returned_version_schema.properties.format == format
            assert returned_version_schema.properties.group_name == schemaregistry_group
            assert returned_version_schema.properties.name == name
            assert returned_version_schema.properties.version == schema_properties.version
            assert returned_version_schema.definition.replace("\/", "/") == schema_str

            with pytest.raises(TypeError) as exc:
                await client.get_schema(group_name=schemaregistry_group, version=schema_properties.version, logging_enable=True)
            assert "Missing" in str(exc)

            returned_schema_properties = await client.get_schema_properties(schemaregistry_group, name, schema_str, format, logging_enable=True)

            assert returned_schema_properties.id == schema_properties.id
            assert returned_schema.properties.group_name == schemaregistry_group
            assert returned_schema.properties.name == name
            assert returned_schema_properties.format == format
        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy_async
    async def test_schema_update_async(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(f"schemaregistry_{format.lower()}_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        async with client:
            name = self.get_resource_name(f"test-schema-update-async-{format.lower()}")
            schema_properties = await client.register_schema(schemaregistry_group, name, schema_str, format)

            assert schema_properties.id is not None
            assert schema_properties.format == format

            schema_str_new = schema_str.replace("color", "food").replace("Color", "Food")   # for JSON and Avro string case
            new_schema_properties = await client.register_schema(schemaregistry_group, name, schema_str_new, format)

            assert new_schema_properties.id is not None
            assert new_schema_properties.format == format
            assert new_schema_properties.group_name == schemaregistry_group
            assert new_schema_properties.name == name

            new_schema = await client.get_schema(schema_id=new_schema_properties.id)

            assert new_schema.properties.id != schema_properties.id
            assert new_schema.properties.id == new_schema_properties.id
            assert new_schema.definition.replace("\/", "/") == schema_str_new
            assert new_schema.properties.format == format
            assert new_schema.properties.group_name == schemaregistry_group
            assert new_schema.properties.name == name

            old_schema = await client.get_schema(group_name=schemaregistry_group, name=name, version=schema_properties.version, logging_enable=True)

            assert old_schema.properties.id != new_schema_properties.id
            assert old_schema.properties.id == schema_properties.id
            assert old_schema.definition.replace("\/", "/") == schema_str
            assert old_schema.properties.format == format
            assert old_schema.properties.group_name == schemaregistry_group
            assert old_schema.properties.name == name
            assert old_schema.properties.version == schema_properties.version

        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy_async
    async def test_schema_same_twice_async(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(f"schemaregistry_{format.lower()}_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name(f"test-schema-twice-async-{format.lower()}")
        async with client:
            schema_properties = await client.register_schema(schemaregistry_group, name, schema_str, format)
            schema_properties_second = await client.register_schema(schemaregistry_group, name, schema_str, format)
            assert schema_properties.id == schema_properties_second.id
        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy_async
    async def test_schema_negative_wrong_credential_async(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(f"schemaregistry_{format.lower()}_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        credential = ClientSecretCredential(tenant_id="fake", client_id="fake", client_secret="fake")
        client = SchemaRegistryClient(fully_qualified_namespace=schemaregistry_fully_qualified_namespace, credential=credential)
        async with client, credential:
            name = self.get_resource_name(f"test-schema-negative-async-{format.lower()}")
            with pytest.raises(ClientAuthenticationError):
                await client.register_schema(schemaregistry_group, name, schema_str, format)

    @pytest.mark.live_test_only
    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy_async
    async def test_schema_negative_wrong_endpoint_async(self, format, schema_str, **kwargs):
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace="fake.servicebus.windows.net")
        async with client:
            name = self.get_resource_name(f"test-schema-nonexist-async-{format.lower()}")
            # accepting both errors for now due to: https://github.com/Azure/azure-sdk-tools/issues/2907
            with pytest.raises((ServiceRequestError, HttpResponseError)) as exc_info:
                await client.register_schema(schemaregistry_group, name, schema_str, format)
            if exc_info.type is HttpResponseError:
                response_content = json.loads(exc_info.value.response.content)
                assert any([(m in response_content["Message"]) for m in ["Name does not resolve", "Unable to find a record"]])

        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy_async
    async def test_schema_negative_no_schema_async(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(f"schemaregistry_{format.lower()}_fully_qualified_namespace")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        async with client:
            with pytest.raises(HttpResponseError):
                await client.get_schema('a')

            with pytest.raises(HttpResponseError):
                await client.get_schema('a' * 32)
        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy_async
    async def test_schema_negative_no_schema_version_async(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(f"schemaregistry_{format.lower()}_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name(f"test-schema-negative-version-{format.lower()}")
        async with client:
            schema_properties = await client.register_schema(schemaregistry_group, name, schema_str, format)
            version = schema_properties.version + 1
            with pytest.raises(HttpResponseError):
                await client.get_schema(group_name=schemaregistry_group, name=name, version=version)
        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy_async
    async def test_register_schema_errors(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(f"schemaregistry_{format.lower()}_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = 'test-schema'

        async with client:
            with pytest.raises(ValueError) as e:
                await client.register_schema(None, name, schema_str, format)

            with pytest.raises(ValueError) as e:
                await client.register_schema(schemaregistry_group, None, schema_str, format)

            with pytest.raises(HttpResponseError) as e:
                await client.register_schema(schemaregistry_group, name, None, format)
            assert e.value.error.code == 'InvalidRequest'
            assert e.value.status_code == 400
            assert e.value.reason == 'Bad Request'

            with pytest.raises(AttributeError) as e:
                await client.register_schema(schemaregistry_group, name, schema_str, None)

            with pytest.raises(HttpResponseError) as e:
                await client.register_schema(schemaregistry_group, name, schema_str, 'invalid-format')
            assert e.value.error.code == 'InvalidSchemaType'
            assert e.value.status_code == 415
            assert e.value.reason == 'Unsupported Media Type'
    
    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy_async
    async def test_get_schema_properties_errors(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(f"schemaregistry_{format.lower()}_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = 'test-schema'

        async with client:
            with pytest.raises(ValueError) as e:
                await client.get_schema_properties(None, name, schema_str, format)

            with pytest.raises(ValueError) as e:
                await client.get_schema_properties(schemaregistry_group, None, schema_str, format)

            with pytest.raises(HttpResponseError) as e:
                await client.get_schema_properties(schemaregistry_group, name, None, format)
            assert e.value.error.code == 'InvalidRequest'
            assert e.value.status_code == 400
            assert e.value.reason == 'Bad Request'

            with pytest.raises(AttributeError) as e:
                await client.get_schema_properties(schemaregistry_group, name, schema_str, None)

            with pytest.raises(HttpResponseError) as e:
                await client.get_schema_properties(schemaregistry_group, name, schema_str, 'invalid-format')
            assert e.value.error.code == 'InvalidSchemaType'
            assert e.value.status_code == 415
            assert e.value.reason == 'Unsupported Media Type'

            with pytest.raises(HttpResponseError) as e:
                await client.get_schema_properties(schemaregistry_group, 'never-registered', schema_str, format)
            assert e.value.error.code == 'ItemNotFound'
            assert e.value.status_code == 404
            assert e.value.reason == 'Not Found'

    @SchemaRegistryEnvironmentVariableLoader()
    @pytest.mark.parametrize("format, schema_str", format_params, ids=format_ids)
    @ArgPasser()
    @recorded_by_proxy_async
    async def test_get_schema_errors(self, format, schema_str, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop(f"schemaregistry_{format.lower()}_fully_qualified_namespace")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        async with client:
            with pytest.raises(ValueError) as e:
                await client.get_schema(None)

            with pytest.raises(HttpResponseError) as e:
                await client.get_schema('fakeschemaid')
            assert e.value.error.code == 'InvalidRequest'
            assert e.value.status_code == 400
            assert e.value.reason == 'Bad Request'
