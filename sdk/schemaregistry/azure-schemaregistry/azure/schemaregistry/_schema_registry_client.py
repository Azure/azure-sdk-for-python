from ._generated._azure_schema_registry import AzureSchemaRegistry
from ._common._schema import Schema


class SchemaRegistryClient:
    def __init__(
            self,
            endpoint,
            credential,  # TODO P0: how to set credential/build pipeline?
            max_caches_size=0,  # TODO: cache for schemas?
            **kwargs
    ):
        self._client = AzureSchemaRegistry(endpoint=endpoint)

    # TODO: all http request needs to be parsed?
    def register_schema(self, schema_group, schema_name, serialization_type, schema_string):
        # type: (str, str, str, str) -> Schema
        return self._client.schema.register(schema_group, schema_name, serialization_type, schema_string)

    def get_schema(self, schema_id):
        # type: (str) -> Schema
        return self._client.schema.get_by_id(schema_id)

    def get_schema_id(self, schema_group, schema_name, serialization_type, schema_string):  # TODO: all should match?
        # type: (str, str, str, Union[str, Enum]) -> str
        return self._client.schema.get_id_by_content(schema_group, schema_name, serialization_type, schema_string)
