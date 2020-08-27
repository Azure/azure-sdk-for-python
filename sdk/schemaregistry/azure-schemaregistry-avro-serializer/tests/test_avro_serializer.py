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
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from schemaregistry_preparer import SchemaRegistryPreparer
from devtools_testutils import AzureMgmtTestCase


class SchemaRegistryTests(AzureMgmtTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    def test_basic_avro_serializer(self):
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        schema = avro.schema.parse(schema_str)
        dict_data = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}

        # encoding part
        encode_stream = BytesIO()
        writer = avro.io.DatumWriter(schema)
        writer.write(dict_data, avro.io.BinaryEncoder(encode_stream))
        encoded_payload = encode_stream.getvalue()
        encode_stream.close()

        # decoding part
        decode_stream = BytesIO(encoded_payload)
        avro_reader = avro.io.DatumReader(writers_schema=schema)
        bin_decoder = avro.io.BinaryDecoder(decode_stream)
        decoded_data = avro_reader.read(bin_decoder)
        decode_stream.close()

        assert decoded_data['name'] == "Ben"
        assert decoded_data['favorite_number'] == 7
        assert decoded_data['favorite_color'] == 'red'
