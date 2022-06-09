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

from azure.schemaregistry import SchemaRegistryClient
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

SchemaRegistryEnvironmentVariableLoader = functools.partial(EnvironmentVariableLoader, "schemaregistry", schemaregistry_fully_qualified_namespace="fake_resource.servicebus.windows.net/", schemaregistry_group="fakegroup")

class TestSchemaRegistry(AzureRecordedTestCase):

    def create_client(self, **kwargs):
        fully_qualified_namespace = kwargs.pop("fully_qualified_namespace")
        credential = self.get_credential(SchemaRegistryClient)
        return self.create_client_from_credential(SchemaRegistryClient, credential, fully_qualified_namespace=fully_qualified_namespace)

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_schema_basic(self, **kwargs):
                schemaregistry_fully_qualified_namespace = kwargs.pop("schemaregistry_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name('test-schema-basic')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        format = "Avro"
        schema_properties = client.register_schema(schemaregistry_group, name, schema_str, format, logging_enable=True)

        assert schema_properties.id is not None
        assert schema_properties.format == "Avro"

        returned_schema = client.get_schema(schema_id=schema_properties.id, logging_enable=True)

        assert returned_schema.properties.id == schema_properties.id
        assert returned_schema.properties.format == "Avro"
        assert returned_schema.properties.group_name == schemaregistry_group
        assert returned_schema.properties.name == name
        assert returned_schema.definition == schema_str

        returned_schema_properties = client.get_schema_properties(schemaregistry_group, name, schema_str, format, logging_enable=True)

        assert returned_schema_properties.id == schema_properties.id
        assert returned_schema_properties.format == "Avro"
        assert returned_schema.properties.group_name == schemaregistry_group
        assert returned_schema.properties.name == name

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_schema_update(self, **kwargs):
                schemaregistry_fully_qualified_namespace = kwargs.pop("schemaregistry_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name('test-schema-update')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        format = "Avro"
        schema_properties = client.register_schema(schemaregistry_group, name, schema_str, format)

        assert schema_properties.id is not None
        assert schema_properties.format == "Avro"

        schema_str_new = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_food","type":["string","null"]}]}"""
        new_schema_properties = client.register_schema(schemaregistry_group, name, schema_str_new, format)

        assert new_schema_properties.id is not None
        assert new_schema_properties.format == "Avro"
        assert new_schema_properties.group_name == schemaregistry_group
        assert new_schema_properties.name == name

        new_schema = client.get_schema(schema_id=new_schema_properties.id)

        assert new_schema.properties.id != schema_properties.id
        assert new_schema.properties.id == new_schema_properties.id
        assert new_schema.definition == schema_str_new
        assert new_schema.properties.format == "Avro"
        assert new_schema.properties.group_name == schemaregistry_group
        assert new_schema.properties.name == name

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_schema_same_twice(self, **kwargs):
                schemaregistry_fully_qualified_namespace = kwargs.pop("schemaregistry_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = self.get_resource_name('test-schema-twice')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"age","type":["int","null"]},{"name":"city","type":["string","null"]}]}"""
        format = "Avro"
        schema_properties = client.register_schema(schemaregistry_group, name, schema_str, format)
        schema_properties_second = client.register_schema(schemaregistry_group, name, schema_str, format)
        assert schema_properties.id == schema_properties_second.id

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_schema_negative_wrong_credential(self, **kwargs):
                schemaregistry_fully_qualified_namespace = kwargs.pop("schemaregistry_fully_qualified_namespace")
        print(schemaregistry_fully_qualified_namespace)
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        credential = ClientSecretCredential(tenant_id="fake", client_id="fake", client_secret="fake")
        client = SchemaRegistryClient(fully_qualified_namespace=schemaregistry_fully_qualified_namespace, credential=credential)
        name = self.get_resource_name('test-schema-negative')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        format = "Avro"
        with pytest.raises(ClientAuthenticationError):
            client.register_schema(schemaregistry_group, name, schema_str, format)

    @pytest.mark.skip("Figure out why live_test_only mark not working for non-live mode")
    @pytest.mark.live_test_only
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_schema_negative_wrong_endpoint(self, **kwargs):
                schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace="fake.servicebus.windows.net")
        name = self.get_resource_name('test-schema-nonexist')
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        format = "Avro"
        # accepting both errors for now due to: https://github.com/Azure/azure-sdk-tools/issues/2907
        with pytest.raises((ServiceRequestError, HttpResponseError)) as exc_info:
            client.register_schema(schemaregistry_group, name, schema_str, format)
        if exc_info.type is HttpResponseError:
            response_content = json.loads(exc_info.value.response.content)
            assert "Name does not resolve" in response_content["Message"]

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_schema_negative_no_schema(self, **kwargs):
                schemaregistry_fully_qualified_namespace = kwargs.pop("schemaregistry_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        with pytest.raises(HttpResponseError):
            client.get_schema('a')

        with pytest.raises(HttpResponseError):
            client.get_schema('a' * 32)

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_register_schema_errors(self, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop("schemaregistry_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = 'test-schema'
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"age","type":["int","null"]},{"name":"city","type":["string","null"]}]}"""
        format = "Avro"

        with pytest.raises(ValueError) as e:
            client.register_schema(None, name, schema_str, format)

        with pytest.raises(ValueError) as e:
            client.register_schema(schemaregistry_group, None, schema_str, format)

        with pytest.raises(HttpResponseError) as e:
            client.register_schema(schemaregistry_group, name, None, format)
        assert e.value.error.code == 'InvalidRequest'
        assert e.value.status_code == 400
        assert e.value.reason == 'Bad Request'

        with pytest.raises(AttributeError) as e:
            client.register_schema(schemaregistry_group, name, schema_str, None)

        with pytest.raises(HttpResponseError) as e:
            client.register_schema(schemaregistry_group, name, schema_str, 'invalid-format')
        assert e.value.error.code == 'InvalidSchemaType'
        assert e.value.status_code == 415
        assert e.value.reason == 'Unsupported Media Type'

    
    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_get_schema_properties_errors(self, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop("schemaregistry_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        name = 'test-schema'
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"age","type":["int","null"]},{"name":"city","type":["string","null"]}]}"""
        format = "Avro"

        with pytest.raises(ValueError) as e:
            client.get_schema_properties(None, name, schema_str, format)

        with pytest.raises(ValueError) as e:
            client.get_schema_properties(schemaregistry_group, None, schema_str, format)

        with pytest.raises(HttpResponseError) as e:
            client.get_schema_properties(schemaregistry_group, name, None, format)
        assert e.value.error.code == 'InvalidRequest'
        assert e.value.status_code == 400
        assert e.value.reason == 'Bad Request'

        with pytest.raises(AttributeError) as e:
            client.get_schema_properties(schemaregistry_group, name, schema_str, None)

        with pytest.raises(HttpResponseError) as e:
            client.get_schema_properties(schemaregistry_group, name, schema_str, 'invalid-format')
        assert e.value.error.code == 'InvalidSchemaType'
        assert e.value.status_code == 415
        assert e.value.reason == 'Unsupported Media Type'

        with pytest.raises(HttpResponseError) as e:
            client.get_schema_properties(schemaregistry_group, 'never-registered', schema_str, format)
        assert e.value.error.code == 'ItemNotFound'
        assert e.value.status_code == 404
        assert e.value.reason == 'Not Found'

    @SchemaRegistryEnvironmentVariableLoader()
    @recorded_by_proxy
    def test_get_schema_errors(self, **kwargs):
        schemaregistry_fully_qualified_namespace = kwargs.pop("schemaregistry_fully_qualified_namespace")
        schemaregistry_group = kwargs.pop("schemaregistry_group")
        client = self.create_client(fully_qualified_namespace=schemaregistry_fully_qualified_namespace)
        with pytest.raises(ValueError) as e:
            client.get_schema(None)

        with pytest.raises(HttpResponseError) as e:
            client.get_schema('fakeschemaid')
        assert e.value.error.code == 'InvalidRequest'
        assert e.value.status_code == 400
        assert e.value.reason == 'Bad Request'
