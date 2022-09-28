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
from devtools_testutils.azure_testcase import _is_autorest_v3

from azure.core.credentials import AccessToken

SchemaRegistryEnvironmentVariableLoader = functools.partial(EnvironmentVariableLoader, "schemaregistry", schemaregistry_fully_qualified_namespace="fake_resource.servicebus.windows.net/", schemaregistry_group="fakegroup")

class TestSchemaRegistryAsync(AzureRecordedTestCase):

    def create_client(self, **kwargs):
        fully_qualified_namespace = kwargs.pop("fully_qualified_namespace")
        credential = self.get_credential(SchemaRegistryClient, is_async=True)
        return self.create_client_from_credential(SchemaRegistryClient, credential, fully_qualified_namespace=fully_qualified_namespace, is_async=True)

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_schema_basic_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        async with client:
            name = self.get_resource_name('test-schema-basic-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            schema_properties = await client.register_schema(schemaregistry_group, name, schema_str, format, logging_enable=True)

            assert schema_properties.id is not None
            assert schema_properties.format == "Avro"

            returned_schema = await client.get_schema(schema_id=schema_properties.id, logging_enable=True)

            assert returned_schema.properties.id == schema_properties.id
            assert returned_schema.properties.format == "Avro"
            assert returned_schema.properties.group_name == schemaregistry_group
            assert returned_schema.properties.name == name
            assert returned_schema.definition == schema_str

            returned_version_schema = await client.get_schema(group_name=schemaregistry_group, name=name, version=schema_properties.version, logging_enable=True)

            assert returned_version_schema.properties.id == schema_properties.id
            assert returned_version_schema.properties.format == "Avro"
            assert returned_version_schema.properties.group_name == schemaregistry_group
            assert returned_version_schema.properties.name == name
            assert returned_version_schema.properties.version == schema_properties.version
            assert returned_version_schema.definition == schema_str

            with pytest.raises(TypeError) as exc:
                await client.get_schema(group_name=schemaregistry_group, version=schema_properties.version, logging_enable=True)
            assert "Missing" in str(exc)

            returned_schema_properties = await client.get_schema_properties(schemaregistry_group, name, schema_str, format, logging_enable=True)

            assert returned_schema_properties.id == schema_properties.id
            assert returned_schema.properties.group_name == schemaregistry_group
            assert returned_schema.properties.name == name
            assert returned_schema_properties.format == "Avro"
        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_schema_update_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        async with client:
            name = self.get_resource_name('test-schema-update-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            schema_properties = await client.register_schema(schemaregistry_group, name, schema_str, format)

            assert schema_properties.id is not None
            assert schema_properties.format == "Avro"

            schema_str_new = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_food","type":["string","null"]}]}"""
            new_schema_properties = await client.register_schema(schemaregistry_group, name, schema_str_new, format)

            assert new_schema_properties.id is not None
            assert new_schema_properties.format == "Avro"
            assert new_schema_properties.group_name == schemaregistry_group
            assert new_schema_properties.name == name

            new_schema = await client.get_schema(schema_id=new_schema_properties.id)

            assert new_schema.properties.id != schema_properties.id
            assert new_schema.properties.id == new_schema_properties.id
            assert new_schema.definition == schema_str_new
            assert new_schema.properties.format == "Avro"
            assert new_schema.properties.group_name == schemaregistry_group
            assert new_schema.properties.name == name

            old_schema = await client.get_schema(group_name=schemaregistry_group, name=name, version=schema_properties.version, logging_enable=True)

            assert old_schema.properties.id != new_schema_properties.id
            assert old_schema.properties.id == schema_properties.id
            assert old_schema.definition == schema_str
            assert old_schema.properties.format == "Avro"
            assert old_schema.properties.group_name == schemaregistry_group
            assert old_schema.properties.name == name
            assert old_schema.properties.version == schema_properties.version

        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_schema_same_twice_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name('test-schema-twice-async')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"age","type":["int","null"]},{"name":"city","type":["string","null"]}]}"""
        format = "Avro"
        async with client:
            schema_properties = await client.register_schema(schemaregistry_group, name, schema_str, format)
            schema_properties_second = await client.register_schema(schemaregistry_group, name, schema_str, format)
            assert schema_properties.id == schema_properties_second.id
        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_schema_negative_wrong_credential_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        credential = ClientSecretCredential(tenant_id="fake", client_id="fake", client_secret="fake")
        client = SchemaRegistryClient(fully_qualified_namespace=schemaregistry_fully_qualified_namespace, credential=credential)
        async with client, credential:
            name = self.get_resource_name('test-schema-negative-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            with pytest.raises(ClientAuthenticationError):
                await client.register_schema(schemaregistry_group, name, schema_str, format)

    @pytest.mark.live_test_only
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_schema_negative_wrong_endpoint_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(fully_qualified_namespace="fake.servicebus.windows.net")
        async with client:
            name = self.get_resource_name('test-schema-nonexist-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            # accepting both errors for now due to: https://github.com/Azure/azure-sdk-tools/issues/2907
            with pytest.raises((ServiceRequestError, HttpResponseError)) as exc_info:
                await client.register_schema(schemaregistry_group, name, schema_str, format)
            if exc_info.type is HttpResponseError:
                response_content = json.loads(exc_info.value.response.content)
                assert any([(m in response_content["Message"]) for m in ["Name does not resolve", "Unable to find a record"]])

        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_schema_negative_no_schema_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        async with client:
            with pytest.raises(HttpResponseError):
                await client.get_schema('a')

            with pytest.raises(HttpResponseError):
                await client.get_schema('a' * 32)
        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_schema_negative_no_schema_version_async(self, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop("schemaregistry_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name('test-schema-negative-version')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"age","type":["int","null"]},{"name":"city","type":["string","null"]}]}"""
        format = "Avro"
        async with client:
            schema_properties = await client.register_schema(schemaregistry_group, name, schema_str, format)
            version = schema_properties.version + 1
            with pytest.raises(HttpResponseError):
                await client.get_schema(group_name=schemaregistry_group, name=name, version=version)
        await client._generated_client._config.credential.close()

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy_async
    async def test_register_schema_errors(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = 'test-schema'
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"age","type":["int","null"]},{"name":"city","type":["string","null"]}]}"""
        format = "Avro"

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
    @recorded_by_proxy_async
    async def test_get_schema_properties_errors(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = 'test-schema'
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"age","type":["int","null"]},{"name":"city","type":["string","null"]}]}"""
        format = "Avro"

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
    @recorded_by_proxy_async
    async def test_get_schema_errors(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        async with client:
            with pytest.raises(ValueError) as e:
                await client.get_schema(None)

            with pytest.raises(HttpResponseError) as e:
                await client.get_schema('fakeschemaid')
            assert e.value.error.code == 'InvalidRequest'
            assert e.value.status_code == 400
            assert e.value.reason == 'Bad Request'
