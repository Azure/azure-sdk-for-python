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

from azure.schemaregistry import SchemaRegistryClient
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from devtools_testutils import AzureTestCase, PowerShellPreparer

SchemaRegistryPowerShellPreparer = functools.partial(PowerShellPreparer, "schemaregistry", schemaregistry_endpoint="fake_resource.servicebus.windows.net", schemaregistry_group="fakegroup")

class SchemaRegistryTests(AzureTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(SchemaRegistryClient)
        return self.create_client_from_credential(SchemaRegistryClient, credential, endpoint=endpoint)

    @SchemaRegistryPowerShellPreparer()
    def test_schema_basic(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_endpoint)
        schema_name = self.get_resource_name('test-schema-basic')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        serialization_type = "Avro"
        schema_properties = client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)

        assert schema_properties.schema_id is not None
        assert schema_properties.location is not None
        assert schema_properties.location_by_id is not None
        assert schema_properties.version is 1
        assert schema_properties.serialization_type == "Avro"

        returned_schema = client.get_schema(schema_id=schema_properties.schema_id)

        assert returned_schema.schema_properties.schema_id == schema_properties.schema_id
        assert returned_schema.schema_properties.location is not None
        assert returned_schema.schema_properties.location_by_id is not None
        assert returned_schema.schema_properties.version == 1
        assert returned_schema.schema_properties.serialization_type == "Avro"
        assert returned_schema.schema_content == schema_str

        returned_schema_properties = client.get_schema_id(schemaregistry_group, schema_name, serialization_type, schema_str)

        assert returned_schema_properties.schema_id == schema_properties.schema_id
        assert returned_schema_properties.location is not None
        assert returned_schema_properties.location_by_id is not None
        assert returned_schema_properties.version == 1
        assert returned_schema_properties.serialization_type == "Avro"

    @SchemaRegistryPowerShellPreparer()
    def test_schema_update(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_endpoint)
        schema_name = self.get_resource_name('test-schema-update')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        serialization_type = "Avro"
        schema_properties = client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)

        assert schema_properties.schema_id is not None
        assert schema_properties.location is not None
        assert schema_properties.location_by_id is not None
        assert schema_properties.version != 0
        assert schema_properties.serialization_type == "Avro"

        schema_str_new = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_food","type":["string","null"]}]}"""
        new_schema_properties = client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str_new)

        assert new_schema_properties.schema_id is not None
        assert new_schema_properties.location is not None
        assert new_schema_properties.location_by_id is not None
        assert new_schema_properties.version == schema_properties.version + 1
        assert new_schema_properties.serialization_type == "Avro"

        new_schema = client.get_schema(schema_id=new_schema_properties.schema_id)

        assert new_schema.schema_properties.schema_id != schema_properties.schema_id
        assert new_schema.schema_properties.schema_id == new_schema_properties.schema_id
        assert new_schema.schema_properties.location is not None
        assert new_schema.schema_properties.location_by_id is not None
        assert new_schema.schema_content == schema_str_new
        assert new_schema.schema_properties.version == schema_properties.version + 1
        assert new_schema.schema_properties.serialization_type == "Avro"

    @SchemaRegistryPowerShellPreparer()
    def test_schema_same_twice(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_endpoint)
        schema_name = self.get_resource_name('test-schema-twice')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"age","type":["int","null"]},{"name":"city","type":["string","null"]}]}"""
        serialization_type = "Avro"
        schema_properties = client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)
        schema_properties_second = client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)
        assert schema_properties.schema_id == schema_properties_second.schema_id

    @SchemaRegistryPowerShellPreparer()
    def test_schema_negative_wrong_credential(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        credential = ClientSecretCredential(tenant_id="fake", client_id="fake", client_secret="fake")
        client = SchemaRegistryClient(endpoint=schemaregistry_endpoint, credential=credential)
        schema_name = self.get_resource_name('test-schema-negative')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        serialization_type = "Avro"
        with pytest.raises(ClientAuthenticationError):
            client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)

    @SchemaRegistryPowerShellPreparer()
    def test_schema_negative_wrong_endpoint(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        client = self.create_client("nonexist.servicebus.windows.net")
        schema_name = self.get_resource_name('test-schema-nonexist')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        serialization_type = "Avro"
        with pytest.raises(ServiceRequestError):
            client.register_schema(schemaregistry_group, schema_name, serialization_type, schema_str)

    @SchemaRegistryPowerShellPreparer()
    def test_schema_negative_no_schema(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        client = self.create_client(schemaregistry_endpoint)
        with pytest.raises(HttpResponseError):
            client.get_schema('a')

        with pytest.raises(HttpResponseError):
            client.get_schema('a' * 32)
