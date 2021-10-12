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
import os

from azure.schemaregistry.aio import SchemaRegistryClient
from azure.identity.aio import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from schemaregistry_preparer import SchemaRegistryPreparer
from devtools_testutils import AzureTestCase, PowerShellPreparer
from devtools_testutils.azure_testcase import _is_autorest_v3

from azure.core.credentials import AccessToken

SchemaRegistryPowerShellPreparer = functools.partial(PowerShellPreparer, "schemaregistry", schemaregistry_fully_qualified_namespace="fake_resource.servicebus.windows.net/", schemaregistry_group="fakegroup")

class SchemaRegistryAsyncTests(AzureTestCase):

    def create_client(self, fully_qualified_namespace):
        credential = self.get_credential(SchemaRegistryClient, is_async=True)
        return self.create_client_from_credential(SchemaRegistryClient, credential, fully_qualified_namespace=fully_qualified_namespace, is_async=True)

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_basic_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_fully_qualified_namespace)
        async with client:
            schema_name = self.get_resource_name('test-schema-basic-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            schema_properties = await client.register_schema(schemaregistry_group, schema_name, schema_str, format)

            assert schema_properties.id is not None
            assert schema_properties.version is 1
            assert schema_properties.format == "Avro"

            returned_schema = await client.get_schema(id=schema_properties.id)

            assert returned_schema.properties.id == schema_properties.id
            assert returned_schema.properties.version == 1
            assert returned_schema.properties.format == "Avro"
            assert returned_schema.schema_definition == schema_str

            returned_schema_properties = await client.get_schema_properties(schemaregistry_group, schema_name, schema_str, format)

            assert returned_schema_properties.id == schema_properties.id
            assert returned_schema_properties.version == 1
            assert returned_schema_properties.format == "Avro"
        await client._generated_client._config.credential.close()

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_update_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_fully_qualified_namespace)
        async with client:
            schema_name = self.get_resource_name('test-schema-update-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            schema_properties = await client.register_schema(schemaregistry_group, schema_name, schema_str, format)

            assert schema_properties.id is not None
            assert schema_properties.version != 0
            assert schema_properties.format == "Avro"

            schema_str_new = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_food","type":["string","null"]}]}"""
            new_schema_properties = await client.register_schema(schemaregistry_group, schema_name, schema_str_new, format)

            assert new_schema_properties.id is not None
            assert new_schema_properties.version == schema_properties.version + 1
            assert new_schema_properties.format == "Avro"

            new_schema = await client.get_schema(id=new_schema_properties.id)

            assert new_schema.properties.id != schema_properties.id
            assert new_schema.properties.id == new_schema_properties.id
            assert new_schema.schema_definition == schema_str_new
            assert new_schema.properties.version == schema_properties.version + 1
            assert new_schema.properties.format == "Avro"

        await client._generated_client._config.credential.close()

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_same_twice_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_fully_qualified_namespace)
        schema_name = self.get_resource_name('test-schema-twice-async')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"age","type":["int","null"]},{"name":"city","type":["string","null"]}]}"""
        format = "Avro"
        async with client:
            schema_properties = await client.register_schema(schemaregistry_group, schema_name, schema_str, format)
            schema_properties_second = await client.register_schema(schemaregistry_group, schema_name, schema_str, format)
            assert schema_properties.id == schema_properties_second.id
        await client._generated_client._config.credential.close()

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_negative_wrong_credential_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        credential = ClientSecretCredential(tenant_id="fake", client_id="fake", client_secret="fake")
        client = SchemaRegistryClient(fully_qualified_namespace=schemaregistry_fully_qualified_namespace, credential=credential)
        async with client, credential:
            schema_name = self.get_resource_name('test-schema-negative-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            with pytest.raises(ClientAuthenticationError):
                await client.register_schema(schemaregistry_group, schema_name, schema_str, format)

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_negative_wrong_endpoint_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client("nonexist.servicebus.windows.net")
        async with client:
            schema_name = self.get_resource_name('test-schema-nonexist-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            with pytest.raises(ServiceRequestError):
                await client.register_schema(schemaregistry_group, schema_name, schema_str, format)
        await client._generated_client._config.credential.close()

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_negative_no_schema_async(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_fully_qualified_namespace)
        async with client:
            with pytest.raises(HttpResponseError):
                await client.get_schema('a')

            with pytest.raises(HttpResponseError):
                await client.get_schema('a' * 32)
        await client._generated_client._config.credential.close()
