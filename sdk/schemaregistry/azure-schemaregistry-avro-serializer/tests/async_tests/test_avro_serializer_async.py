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
import avro
import avro.io
from io import BytesIO

from azure.schemaregistry.aio import SchemaRegistryClient
from azure.schemaregistry.serializer.avro_serializer.aio import SchemaRegistryAvroSerializer
from azure.identity.aio import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from schemaregistry_preparer import SchemaRegistryPreparer
from devtools_testutils import AzureMgmtTestCase


class SchemaRegistryAvroSerializerAsyncTests(AzureMgmtTestCase):
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @SchemaRegistryPreparer()
    async def test_basic_sr_avro_serializer_async(self, schemaregistry_endpoint, schemaregistry_group, schemaregistry_tenant_id,
                          schemaregistry_client_id, schemaregistry_client_secret, **kwargs):
        credential = ClientSecretCredential(tenant_id=schemaregistry_tenant_id, client_id=schemaregistry_client_id,
                                            client_secret=schemaregistry_client_secret)

        sr_avro_serializer = SchemaRegistryAvroSerializer(schemaregistry_endpoint, credential, schemaregistry_group)
        sr_client = SchemaRegistryClient(schemaregistry_endpoint, credential)

        random_schema_namespace = str(uuid.uuid4())[0:8]
        schema_str = "{\"namespace\":\"" + random_schema_namespace + "\"" +\
            ""","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        schema = avro.schema.parse(schema_str)

        dict_data = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
        encoded_data = await sr_avro_serializer.serialize(dict_data, schema_str)

        assert encoded_data[0:4] == b'\0\0\0\0'
        schema_id = (await sr_client.get_schema_id(schemaregistry_group, schema.fullname, "Avro", str(schema))).id
        assert encoded_data[4:36] == schema_id.encode('utf-8')

        decoded_data = await sr_avro_serializer.deserialize(encoded_data)
        assert decoded_data['name'] == "Ben"
        assert decoded_data['favorite_number'] == 7
        assert decoded_data['favorite_color'] == 'red'

        await sr_avro_serializer.close()
        await sr_client.close()
        await credential.close()
