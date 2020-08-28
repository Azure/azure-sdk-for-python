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

from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avro_serializer import SchemaRegistryAvroSerializer
from azure.schemaregistry.serializer.avro_serializer._avro_serializer import AvroObjectSerializer
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from schemaregistry_preparer import SchemaRegistryPreparer
from devtools_testutils import AzureMgmtTestCase


class SchemaRegistryAvroSerializerTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    def test_raw_avro_serializer(self):
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        schema = avro.schema.parse(schema_str)
        dict_data = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}

        raw_avro_object_serailizer = AvroObjectSerializer()

        # encoding part
        encode_stream = BytesIO()
        raw_avro_object_serailizer.serialize(encode_stream, dict_data, schema)
        encoded_payload = encode_stream.getvalue()
        encode_stream.close()

        # decoding part
        decoded_data = raw_avro_object_serailizer.deserialize(encoded_payload, schema)

        assert decoded_data['name'] == "Ben"
        assert decoded_data['favorite_number'] == 7
        assert decoded_data['favorite_color'] == 'red'

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @SchemaRegistryPreparer()
    def test_basic_sr_avro_serializer(self, schemaregistry_endpoint, schemaregistry_group, schemaregistry_tenant_id,
                          schemaregistry_client_id, schemaregistry_client_secret, **kwargs):
        pass
