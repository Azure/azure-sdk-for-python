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
import pytest
import uuid

from azure.schemaregistry.aio import SchemaRegistryClient
from azure.identity.aio import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from schemaregistry_preparer import SchemaRegistryPreparer
from devtools_testutils import AzureMgmtTestCase


class SchemaRegistryAsyncTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @SchemaRegistryPreparer()
    async def test_schema_basic_async(self, schemaregistry_endpoint, schemaregistry_group, schemaregistry_tenant_id, schemaregistry_client_id, schemaregistry_client_secret, **kwargs):
        credential = ClientSecretCredential(tenant_id=schemaregistry_tenant_id, client_id=schemaregistry_client_id, client_secret=schemaregistry_client_secret)
        client = SchemaRegistryClient(endpoint=schemaregistry_endpoint, credential=credential)
        async with client, credential:
            schema_name = 'test-schema-' + str(uuid.uuid4())
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            serialization_type = "Avro"
            schema_properties = await client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)

            assert schema_properties.schema_id is not None
            assert schema_properties.location is not None
            assert schema_properties.location_by_id is not None
            assert schema_properties.version is 1
            assert schema_properties.type == "Avro"

            returned_schema = await client.get_schema(schema_id=schema_properties.schema_id)

            assert returned_schema.schema_id == schema_properties.schema_id
            assert returned_schema.location is not None
            assert returned_schema.location_by_id is not None
            assert returned_schema.version == 1
            assert returned_schema.type == "Avro"
            assert returned_schema.content == schema_str

            returned_schema_id = await client.get_schema_id(schemaregistry_group, schema_name, serialization_type, schema_str)

            assert returned_schema_id.schema_id == schema_properties.schema_id
            assert returned_schema_id.location is not None
            assert returned_schema_id.location_by_id is not None
            assert returned_schema_id.version == 1
            assert returned_schema_id.type == "Avro"

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @SchemaRegistryPreparer()
    async def test_schema_update_async(self, schemaregistry_endpoint, schemaregistry_group, schemaregistry_tenant_id, schemaregistry_client_id, schemaregistry_client_secret, **kwargs):
        credential = ClientSecretCredential(tenant_id=schemaregistry_tenant_id, client_id=schemaregistry_client_id, client_secret=schemaregistry_client_secret)
        client = SchemaRegistryClient(endpoint=schemaregistry_endpoint, credential=credential)
        async with client, credential:
            schema_name = 'test-schema-' + str(uuid.uuid4())
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            serialization_type = "Avro"
            schema_properties = await client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)

            assert schema_properties.schema_id is not None
            assert schema_properties.location is not None
            assert schema_properties.location_by_id is not None
            assert schema_properties.version == 1
            assert schema_properties.type == "Avro"

            schema_str_new = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_food","type":["string","null"]}]}"""
            new_schema_properties = await client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str_new)

            assert new_schema_properties.schema_id is not None
            assert new_schema_properties.location is not None
            assert new_schema_properties.location_by_id is not None
            assert new_schema_properties.version == 2
            assert new_schema_properties.type == "Avro"

            new_schema = await client.get_schema(schema_id=new_schema_properties.schema_id)

            assert new_schema.schema_id != schema_properties.schema_id
            assert new_schema.schema_id == new_schema_properties.schema_id
            assert new_schema.location is not None
            assert new_schema.location_by_id is not None
            assert new_schema.content == schema_str_new
            assert new_schema.version == 2
            assert new_schema.type == "Avro"

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @SchemaRegistryPreparer()
    async def test_schema_negative_wrong_credential_async(self, schemaregistry_endpoint, schemaregistry_group, schemaregistry_tenant_id, schemaregistry_client_id, schemaregistry_client_secret, **kwargs):
        credential = ClientSecretCredential(tenant_id="fake", client_id="fake", client_secret="fake")
        client = SchemaRegistryClient(endpoint=schemaregistry_endpoint, credential=credential)
        async with client, credential:
            schema_name = 'test-schema-' + str(uuid.uuid4())
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            serialization_type = "Avro"
            with pytest.raises(ClientAuthenticationError):
                await client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @SchemaRegistryPreparer()
    async def test_schema_negative_wrong_endpoint_async(self, schemaregistry_endpoint, schemaregistry_group, schemaregistry_tenant_id, schemaregistry_client_id, schemaregistry_client_secret, **kwargs):
        credential = ClientSecretCredential(tenant_id=schemaregistry_tenant_id, client_id=schemaregistry_client_id, client_secret=schemaregistry_client_secret)
        client = SchemaRegistryClient(endpoint=str(uuid.uuid4()) + ".servicebus.windows.net", credential=credential)
        async with client, credential:
            schema_name = 'test-schema-' + str(uuid.uuid4())
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            serialization_type = "Avro"
            with pytest.raises(ServiceRequestError):
                await client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @SchemaRegistryPreparer()
    async def test_schema_negative_no_schema_async(self, schemaregistry_endpoint, schemaregistry_group, schemaregistry_tenant_id, schemaregistry_client_id, schemaregistry_client_secret, **kwargs):
        credential = ClientSecretCredential(tenant_id=schemaregistry_tenant_id, client_id=schemaregistry_client_id, client_secret=schemaregistry_client_secret)
        client = SchemaRegistryClient(endpoint=schemaregistry_endpoint, credential=credential)
        async with client, credential:
            with pytest.raises(HttpResponseError):
                await client.get_schema('a')

            with pytest.raises(HttpResponseError):
                await client.get_schema('a' * 32)
