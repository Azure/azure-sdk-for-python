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
import avro
import avro.io
from io import BytesIO
import asyncio
import pytest

from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer.aio import AvroSerializer
from azure.identity.aio import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from devtools_testutils import AzureTestCase, PowerShellPreparer

SchemaRegistryPowerShellPreparer = functools.partial(PowerShellPreparer, "schemaregistry", schemaregistry_fully_qualified_namespace="fake_resource.servicebus.windows.net/", schemaregistry_group="fakegroup")

class AvroSerializerAsyncTests(AzureTestCase):

    def create_client(self, fully_qualified_namespace):
        credential = self.get_credential(SchemaRegistryClient, is_async=True)
        return self.create_client_from_credential(SchemaRegistryClient, credential, fully_qualified_namespace=fully_qualified_namespace, is_async=True)

    @pytest.mark.asyncio
    @SchemaRegistryPowerShellPreparer()
    async def test_basic_sr_avro_serializer_with_auto_register_schemas(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        async with sr_client:
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            schema = avro.schema.parse(schema_str)

            dict_data = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
            encoded_data = await sr_avro_serializer.serialize(dict_data, schema=schema_str)

            assert encoded_data[0:4] == b'\0\0\0\0'
            schema_properties = await sr_client.get_schema_id(schemaregistry_group, schema.fullname, "Avro", str(schema))
            schema_id = schema_properties.schema_id
            assert encoded_data[4:36] == schema_id.encode("utf-8")

            decoded_data = await sr_avro_serializer.deserialize(encoded_data)
            assert decoded_data["name"] == u"Ben"
            assert decoded_data["favorite_number"] == 7
            assert decoded_data["favorite_color"] == u"red"

    @pytest.mark.asyncio
    @SchemaRegistryPowerShellPreparer()
    async def test_basic_sr_avro_serializer_without_auto_register_schemas(self, schemaregistry_fully_qualified_namespace, schemaregistry_group, **kwargs):
        sr_client = self.create_client(schemaregistry_fully_qualified_namespace)
        sr_avro_serializer = AvroSerializer(client=sr_client, group_name=schemaregistry_group, auto_register_schemas=True)

        async with sr_client:
            schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
            schema = avro.schema.parse(schema_str)

            dict_data = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
            encoded_data = await sr_avro_serializer.serialize(dict_data, schema=schema_str)

            assert encoded_data[0:4] == b'\0\0\0\0'
            schema_properties = await sr_client.get_schema_id(schemaregistry_group, schema.fullname, "Avro", str(schema))
            schema_id = schema_properties.schema_id
            assert encoded_data[4:36] == schema_id.encode("utf-8")

            decoded_data = await sr_avro_serializer.deserialize(encoded_data)
            assert decoded_data["name"] == u"Ben"
            assert decoded_data["favorite_number"] == 7
            assert decoded_data["favorite_color"] == u"red"
