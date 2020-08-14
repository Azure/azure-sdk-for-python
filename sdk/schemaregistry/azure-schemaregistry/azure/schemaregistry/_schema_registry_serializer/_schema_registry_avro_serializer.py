from .._schema_registry_client import SchemaRegistryClient
from .._common._serializer._avro_serializer import AvroObjectSerializer


class SchemaRegistryAvroSerializer:
    def __init__(self, endpoint, credential, max_cache_size):  # TODO: or just use_cache flag?
        self._schema_registry_client = SchemaRegistryClient(endpoint, credential)
        self._serializer = AvroObjectSerializer()

    def serialize(self, data, schema):
        pass

    def deserialize(self, data):
        pass
