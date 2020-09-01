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
        encoded_payload = raw_avro_object_serailizer.serialize(dict_data, schema)

        # decoding part
        decoded_data = raw_avro_object_serailizer.deserialize(encoded_payload, schema)

        assert decoded_data['name'] == "Ben"
        assert decoded_data['favorite_number'] == 7
        assert decoded_data['favorite_color'] == 'red'

        dict_data_missing_optional_fields = {"name": "Alice"}
        encoded_payload = raw_avro_object_serailizer.serialize(dict_data_missing_optional_fields, schema)
        decoded_data = raw_avro_object_serailizer.deserialize(encoded_payload, schema)

        assert decoded_data['name'] == "Alice"
        assert not decoded_data['favorite_number']
        assert not decoded_data['favorite_color']

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    def test_raw_avro_serializer_negative(self):
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        schema = avro.schema.parse(schema_str)

        raw_avro_object_serailizer = AvroObjectSerializer()
        dict_data_wrong_type = {"name": "Ben", "favorite_number": "something", "favorite_color": "red"}
        with pytest.raises(avro.io.AvroTypeException):
            raw_avro_object_serailizer.serialize(dict_data_wrong_type, schema)

        dict_data_missing_required_field = {"favorite_number": 7, "favorite_color": "red"}
        with pytest.raises(avro.io.AvroTypeException):
            raw_avro_object_serailizer.serialize(dict_data_missing_required_field, schema)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @SchemaRegistryPreparer()
    def test_basic_sr_avro_serializer(self, schemaregistry_endpoint, schemaregistry_group, schemaregistry_tenant_id,
                          schemaregistry_client_id, schemaregistry_client_secret, **kwargs):
        credential = ClientSecretCredential(tenant_id=schemaregistry_tenant_id, client_id=schemaregistry_client_id,
                                            client_secret=schemaregistry_client_secret)

        sr_avro_serializer = SchemaRegistryAvroSerializer(schemaregistry_endpoint, credential, schemaregistry_group)
        sr_client = SchemaRegistryClient(schemaregistry_endpoint, credential)

        random_schema_namespace = 'testschema' + str(uuid.uuid4())[0:8]
        schema_str = "{\"namespace\":\"" + random_schema_namespace + "\"" +\
            ""","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        schema = avro.schema.parse(schema_str)

        dict_data = {"name": "Ben", "favorite_number": 7, "favorite_color": "red"}
        encoded_data = sr_avro_serializer.serialize(dict_data, schema_str)

        assert schema_str in sr_avro_serializer._user_input_schema_cache
        assert str(avro.schema.parse(schema_str)) in sr_avro_serializer._schema_to_id

        assert encoded_data[0:4] == b'\0\0\0\0'
        schema_id = sr_client.get_schema_id(schemaregistry_group, schema.fullname, "Avro", str(schema)).schema_id
        assert encoded_data[4:36] == schema_id.encode('utf-8')

        assert schema_id in sr_avro_serializer._id_to_schema

        decoded_data = sr_avro_serializer.deserialize(encoded_data)
        assert decoded_data['name'] == "Ben"
        assert decoded_data['favorite_number'] == 7
        assert decoded_data['favorite_color'] == 'red'

        sr_avro_serializer.close()
        sr_client.close()
