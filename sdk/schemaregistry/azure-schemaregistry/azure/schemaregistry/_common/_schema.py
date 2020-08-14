from typing import Union
from enum import Enum


class SerializationType(Enum):
    AVRO = 0
    JSON = 1


class Schema:  # TODO: 1. Naming: Schema Properties/Schema Description? 2. Should it be dict like object?
    def __init__(self, schema_id, serialization_type, schema_name, schema_group, schema_byte_array, parse_method):  # TODO: what is schema_byte_arry and parse_method?
        # type: (str, Union[str, Enum], str, str) -> None
        self.schema_id = schema_id  # TODO: property vs instance variable
        self.serialization_type = serialization_type
        self.schema_name = schema_name
        self.schema_group = schema_group
        self.schema = None  # TODO: for Avro/Json, schema would just be a JSON string? what about protocolbuf

