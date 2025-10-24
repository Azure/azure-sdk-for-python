# coding=utf-8

from enum import Enum
from corehttp.utils import CaseInsensitiveEnumMeta


class SchemaContentTypeValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Describes closed list of schema content type values."""

    AVRO = "application/json; serialization=Avro"
    """Avro encoding."""
    JSON = "application/json; serialization=Json"
    """JSON encoding"""
    CUSTOM = "text/plain; charset=utf-8"
    """Plain text custom encoding."""
    PROTOBUF = "text/vnd.ms.protobuf"
    """Protobuf encoding."""
