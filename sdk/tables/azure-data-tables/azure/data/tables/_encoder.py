from typing import Any, Iterator, Optional, Tuple, Union, Mapping
from uuid import UUID
from json import JSONEncoder
from datetime import datetime
from enum import Enum

from ._serialize import EdmType
from ._common_conversion import _encode_base64, _to_utc_datetime

_ODATA_SUFFIX = "@odata.type"


class TableEntityEncoder:

    def prepare_key(self, key: str) -> str:
        """Duplicate the single quote char to escape."""
        try:
            return key.replace("'", "''")
        except (AttributeError, TypeError):
            raise TypeError('PartitionKey or RowKey must be of type string.')

    def prepare_value(self, value: Any) -> Optional[Union[str, int, float, bool]]:
        """This is a utility to allow customers to reproduce our internal encoding for types like datetime and bytes.
        """
        _, encoded = self.encode_property(None, value)
        return encoded

    def encode_property(self, name: Optional[str], value: Any) -> Tuple[Optional[Union[EdmType, str]], Optional[Union[str, int, float, bool]]]:
        """This is a migration of the old add_entity_properties method in serialize.py, with some simplications like
        removing int validation.
        """
        if isinstance(value, bool):
            return None, value
        if isinstance(value, str):
            return None, value
        if isinstance(value, int):
            return None, value  # TODO: Test what happens if the supplied value exceeds int32.
        if isinstance(value, float):
            # The default JSONEncoder will automatically convert to 'NaN', 'Infinity' and '-Infinity'.
            return EdmType.DOUBLE, value
        if isinstance(value, UUID):
            return EdmType.GUID, str(value)
        if isinstance(value, bytes):
            return EdmType.BINARY, _encode_base64(value)
        if isinstance(value, datetime):
            try:
                if value.tables_service_value:
                    return EdmType.DATETIME, value.tables_service_value
            except AttributeError:
                pass
            return EdmType.DATETIME, _to_utc_datetime(value)
        # To support value in tuple
        try:
            if len(value) == 2:
                if value[1] == EdmType.INT64:  # TODO: Test if this works with either string or enum input.
                    return EdmType.INT64, str(value[0])  # TODO: Test what happens if the supplied value exceeds int64
                return self.encode_property(name, value[0])
        except TypeError:
            pass
        if name:
            raise TypeError(f"Unsupported data type '{type(value)}' for entity property '{name}'.")
        raise TypeError(f"Unsupported data type '{type(value)}'.")

    def encode_entity(self, entity: Mapping) -> Mapping[str, Union[str, int, float, bool]]:
        """This method currently behaves the same as the existing serialization function in that
        there is no special treatment for the system keys - PartitionKey, RowKey, Timestamp, Etag.

        We could investigate whether, where and how it would be most effective to check for these.
        """
        encoded = {}
        for key, value in entity.items():  # TODO: Confirm what to do with None values (before and after encoding).
            if "PartitionKey" in key or "RowKey" in key:
                if key == "PartitionKey" or key == "RowKey":
                    encoded[key] = self.prepare_key(value)
                continue
            if _ODATA_SUFFIX in key or key + _ODATA_SUFFIX in entity:
                if value in ["Edm.String", "Edm.Int32", "Edm.Boolean"]:
                    continue
                encoded[key] = value
                continue
            edm_type, value = self.encode_property(key, value)
            # The edm type is decided by value
            # For example, when value=EntityProperty(str(uuid.uuid4), "Edm.Guid"),
            # the type is string instead of Guid after encoded
            if edm_type:
                encoded[key + _ODATA_SUFFIX] = edm_type.value
            encoded[key] = value
        return encoded


class TableEntityJSONEncoder(JSONEncoder, TableEntityEncoder):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def iterencode(self, o: Any, _one_shot: bool = ...) -> Iterator[str]:
        if isinstance(o, Mapping):
            o = self.encode_entity(o)
        return super().iterencode(o, _one_shot)
