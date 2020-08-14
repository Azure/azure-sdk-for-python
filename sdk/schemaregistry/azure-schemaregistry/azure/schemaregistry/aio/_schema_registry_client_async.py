from .._schema import Schema


class SchemaRegistryClient:
    def __init__(
            self,
            endpoint,
            credential,
            max_caches_size,  # TODO: cache for schemas?

            **kwargs
    ):
        self._generated_client = None
        pass

    async def register_schema(self, schema_group, schema_name, schema_string, schema_type):
        # type: (str, str, str, str) -> Schema
        pass

    async def get_schema(self, schema_id):
        # type: (str) -> Schema
        pass

    async def get_schema_id(self, schema_group, schema_name, schema_string, serialization_type):  # TODO: all should match?
        # type: (str, str, str, Union[str, Enum]) -> str
        pass
