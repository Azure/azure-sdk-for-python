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

SchemaRegistryPowerShellPreparer = functools.partial(PowerShellPreparer, "schemaregistry", schemaregistry_endpoint="fake_resource.servicebus.windows.net/", schemaregistry_group="fakegroup")

class SchemaRegistryAsyncTests(AzureTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(SchemaRegistryClient, is_async=True)
        return self.create_client_from_credential(SchemaRegistryClient, credential, fully_qualified_namespace=endpoint, is_async=True)

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_basic_async(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_endpoint)
        async with client:
            schema_name = self.get_resource_name('test-schema-basic-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            assert len(client._id_to_schema) == 0
            assert len(client._description_to_properties) == 0
            schema_properties = await client.register_schema(schemaregistry_group, schema_name, schema_str, format)
            assert len(client._id_to_schema) == 1
            assert len(client._description_to_properties) == 1

            assert schema_properties.id is not None
            assert schema_properties.version is 1
            assert schema_properties.format == "Avro"

            returned_schema = await client.get_schema(id=schema_properties.id)

            assert returned_schema.properties.id == schema_properties.id
            assert returned_schema.properties.version == 1
            assert returned_schema.properties.format == "Avro"
            assert returned_schema.schema_definition == schema_str

            # check that same cached properties object is returned by get_schema_properties
            cached_properties = await client.get_schema_properties(schemaregistry_group, schema_name, schema_str, format)
            same_cached_properties = await client.get_schema_properties(schemaregistry_group, schema_name, schema_str, format)
            assert same_cached_properties == cached_properties

            # check if schema is added to cache when it does not exist in the cache
            cached_properties = client._description_to_properties[
                (schemaregistry_group, schema_name, schema_str, format)
            ]
            properties_cache_length = len(client._description_to_properties)
            del client._description_to_properties[
                (schemaregistry_group, schema_name, schema_str, format)
            ]
            assert len(client._description_to_properties) == properties_cache_length - 1

            returned_schema_properties = await client.get_schema_properties(schemaregistry_group, schema_name, schema_str, format)
            assert len(client._description_to_properties) == properties_cache_length

            assert returned_schema_properties.id == schema_properties.id
            assert returned_schema_properties.version == 1
            assert returned_schema_properties.format == "Avro"
        await client._generated_client._config.credential.close()

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_update_async(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_endpoint)
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

            # check that same cached schema object is returned by get_schema
            cached_schema = await client.get_schema(id=new_schema_properties.id)
            same_cached_schema = await client.get_schema(id=new_schema_properties.id)
            assert same_cached_schema == cached_schema

            # check if schema is added to cache when it does not exist in the cache
            cached_schema = client._id_to_schema[new_schema_properties.id]
            schema_cache_length = len(client._id_to_schema)
            del client._id_to_schema[new_schema_properties.id]
            assert len(client._id_to_schema) == schema_cache_length - 1

            new_schema = await client.get_schema(id=new_schema_properties.id)
            assert len(client._id_to_schema) == schema_cache_length

            assert new_schema.properties.id != schema_properties.id
            assert new_schema.properties.id == new_schema_properties.id
            assert new_schema.schema_definition == schema_str_new
            assert new_schema.properties.version == schema_properties.version + 1
            assert new_schema.properties.format == "Avro"

            # check that properties object is the same in caches
            client._id_to_schema = {}
            client._description_to_properties = {}
            new_schema = await client.get_schema(id=new_schema_properties.id)
            new_schema_properties = await client.get_schema_properties(schemaregistry_group, schema_name, schema_str_new, format)
            assert new_schema.properties == new_schema_properties
        await client._generated_client._config.credential.close()

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_same_twice_async(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_endpoint)
        schema_name = self.get_resource_name('test-schema-twice-async')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"age","type":["int","null"]},{"name":"city","type":["string","null"]}]}"""
        format = "Avro"
        async with client:
            schema_properties = await client.register_schema(schemaregistry_group, schema_name, schema_str, format)
            schema_cache_length = len(client._id_to_schema)
            desc_cache_length = len(client._description_to_properties)
            schema_properties_second = await client.register_schema(schemaregistry_group, schema_name, schema_str, format)
            schema_cache_second_length = len(client._id_to_schema)
            desc_cache_second_length = len(client._description_to_properties)
            assert schema_properties.id == schema_properties_second.id
            assert schema_cache_length == schema_cache_second_length
            assert desc_cache_length == desc_cache_second_length
        await client._generated_client._config.credential.close()

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_negative_wrong_credential_async(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        credential = ClientSecretCredential(tenant_id="fake", client_id="fake", client_secret="fake")
        client = SchemaRegistryClient(fully_qualified_namespace=schemaregistry_endpoint, credential=credential)
        async with client, credential:
            schema_name = self.get_resource_name('test-schema-negative-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            with pytest.raises(ClientAuthenticationError):
                await client.register_schema(schemaregistry_group, schema_name, schema_str, format)

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_negative_wrong_endpoint_async(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        client = self.create_client("nonexist.servicebus.windows.net")
        async with client:
            schema_name = self.get_resource_name('test-schema-nonexist-async')
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            format = "Avro"
            with pytest.raises(ServiceRequestError):
                await client.register_schema(schemaregistry_group, schema_name, schema_str, format)
        await client._generated_client._config.credential.close()

    @SchemaRegistryPowerShellPreparer()
    async def test_schema_negative_no_schema_async(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_endpoint)
        async with client:
            with pytest.raises(HttpResponseError):
                await client.get_schema('a')

            with pytest.raises(HttpResponseError):
                await client.get_schema('a' * 32)
        await client._generated_client._config.credential.close()
