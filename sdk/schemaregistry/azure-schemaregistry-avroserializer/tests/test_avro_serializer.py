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

from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.schemaregistry.serializer.avroserializer._avro_serializer import AvroObjectSerializer
from azure.identity import ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError, ServiceRequestError, HttpResponseError

from devtools_testutils import AzureTestCase, PowerShellPreparer

SchemaRegistryPowerShellPreparer = functools.partial(PowerShellPreparer, "schemaregistry", schemaregistry_endpoint="fake_resource.servicebus.windows.net", schemaregistry_group="fakegroup")

class SchemaRegistryAvroSerializerTests(AzureTestCase):

    def test_raw_avro_serializer(self):
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        schema = avro.schema.parse(schema_str)
        dict_data = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}

        raw_avro_object_serializer = AvroObjectSerializer()

        # encoding part
        encoded_payload = raw_avro_object_serializer.serialize(dict_data, schema)

        # decoding part
        decoded_data = raw_avro_object_serializer.deserialize(encoded_payload, schema)

        assert decoded_data["name"] == u"Ben"
        assert decoded_data["favorite_number"] == 7
        assert decoded_data["favorite_color"] == u"red"

        dict_data_missing_optional_fields = {"name": u"Alice"}
        encoded_payload = raw_avro_object_serializer.serialize(dict_data_missing_optional_fields, schema)
        decoded_data = raw_avro_object_serializer.deserialize(encoded_payload, schema)

        assert decoded_data["name"] == u"Alice"
        assert not decoded_data["favorite_number"]
        assert not decoded_data["favorite_color"]

    def test_raw_avro_serializer_negative(self):
        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        schema = avro.schema.parse(schema_str)

        raw_avro_object_serializer = AvroObjectSerializer()
        dict_data_wrong_type = {"name": u"Ben", "favorite_number": u"something", "favorite_color": u"red"}
        with pytest.raises(avro.io.AvroTypeException):
            raw_avro_object_serializer.serialize(dict_data_wrong_type, schema)

        dict_data_missing_required_field = {"favorite_number": 7, "favorite_color": u"red"}
        with pytest.raises(avro.io.AvroTypeException):
            raw_avro_object_serializer.serialize(dict_data_missing_required_field, schema)

    @SchemaRegistryPowerShellPreparer()
    def test_basic_sr_avro_serializer(self, schemaregistry_endpoint, schemaregistry_group, **kwargs):
        sr_client = self.create_basic_client(SchemaRegistryClient, endpoint=schemaregistry_endpoint)
        sr_avro_serializer = SchemaRegistryAvroSerializer(sr_client, schemaregistry_group)

        schema_str = """{"namespace":"example.avro","type":"record","name":"User","fields":[{"name":"name","type":"string"},{"name":"favorite_number","type":["int","null"]},{"name":"favorite_color","type":["string","null"]}]}"""
        schema = avro.schema.parse(schema_str)

        dict_data = {"name": u"Ben", "favorite_number": 7, "favorite_color": u"red"}
        encoded_data = sr_avro_serializer.serialize(dict_data, schema_str)

        assert schema_str in sr_avro_serializer._user_input_schema_cache
        assert str(avro.schema.parse(schema_str)) in sr_avro_serializer._schema_to_id

        assert encoded_data[0:4] == b'\0\0\0\0'
        schema_id = sr_client.get_schema_id(schemaregistry_group, schema.fullname, "Avro", str(schema)).schema_id
        assert encoded_data[4:36] == schema_id.encode("utf-8")

        assert schema_id in sr_avro_serializer._id_to_schema

        decoded_data = sr_avro_serializer.deserialize(encoded_data)
        assert decoded_data["name"] == u"Ben"
        assert decoded_data["favorite_number"] == 7
        assert decoded_data["favorite_color"] == u"red"

        sr_avro_serializer.close()
