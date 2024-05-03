import abc, enum
from typing import Any, Optional, Tuple, Union, Mapping, TypeVar, Generic, Dict
from uuid import UUID
from datetime import datetime
from math import isnan

from ._serialize import EdmType
from ._entity import TableEntity
from ._deserialize import _convert_to_entity
from ._common_conversion import _encode_base64, _to_utc_datetime

_ODATA_SUFFIX = "@odata.type"
T = TypeVar("T")


class TableEntityEncoderABC(abc.ABC, Generic[T]):
    def prepare_key(self, key: str) -> str:
        """Duplicate the single quote char to escape."""
        try:
            return key.replace("'", "''")
        except (AttributeError, TypeError):
            raise TypeError('PartitionKey or RowKey must be of type string.')

    def prepare_value(self, name: Optional[str], value: Any) -> Tuple[Optional[EdmType], Optional[Union[str, int, float, bool]]]:
        """This is a utility to allow customers to reproduce our internal encoding for types like datetime, bytes, float and int64.
        """
        if isinstance(value, bool):
            return None, value
        if isinstance(value, enum.Enum):
            return None, value.value
        if isinstance(value, str):
            return None, value
        if isinstance(value, int):
            return None, value  # TODO: Test what happens if the supplied value exceeds int32.
        if isinstance(value, float):
            if isnan(value):
                return EdmType.DOUBLE, "NaN"
            if value == float("inf"):
                return EdmType.DOUBLE, "Infinity"
            if value == float("-inf"):
                return EdmType.DOUBLE, "-Infinity"
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
        if value is None:
            return None, None
        if name:
            raise TypeError(f"Unsupported data type '{type(value)}' for entity property '{name}'.")
        raise TypeError(f"Unsupported data type '{type(value)}'.")
    
    def prepare_value_in_tuple(self, value_tuple: Tuple[Any, Optional[Union[str, EdmType]]]) -> Tuple[EdmType, Any]:
        edm_type = EdmType(value_tuple[1]) # will throw ValueError when the edm type in tuple is invalid
        value = value_tuple[0]
        if edm_type == EdmType.BINARY:
            value = _encode_base64(value)
        if edm_type in [EdmType.INT64, EdmType.GUID, EdmType.STRING]:
            value = str(value)
        if edm_type == EdmType.INT32:
            value = int(value)
        if edm_type == EdmType.DOUBLE and not isinstance(value, str): # no conversion for edm_type in EdmType.Boolean and value in string
            if isnan(value):
                value = "NaN"
            elif value == float("inf"):
                value = "Infinity"
            elif value == float("-inf"):
                value = "-Infinity"
        if edm_type == EdmType.DATETIME:
            if not isinstance(value, str):
                try:
                    if value.tables_service_value:
                        value = value.tables_service_value
                except AttributeError:
                    pass
                value = _to_utc_datetime(value)
        # no conversion for edm_type in EdmType.Boolean
        return edm_type, value

    def encode_property(self, name: Optional[str], value: Any) -> Tuple[Optional[EdmType], Optional[Union[str, int, float, bool]]]:
        """This is a migration of the old add_entity_properties method in serialize.py, with some simplications like
        removing int validation.
        """
        if isinstance(value, tuple):
            return self.prepare_value_in_tuple(value)
        
        return self.prepare_value(name, value)
        
    
    @abc.abstractmethod
    def encode_entity(self, entity: T) -> Dict[str, Union[str, int, float, bool]]:
        """Encode an entity object into JSON format to send out.
        """
    
    @abc.abstractmethod
    def decode_entity(self, entity: Dict[str, Union[str, int, float, bool]]) -> T:
        ...


class TableEntityEncoder(TableEntityEncoderABC[Union[Mapping[str, Any], TableEntity]]):
    
    def encode_entity(self, entity: Union[Mapping[str, Any], TableEntity]) -> Dict[str, Union[str, int, float, bool]]:
        """This method currently behaves the same as the existing serialization function in that
        there is no special treatment for the system keys - PartitionKey, RowKey, Timestamp, Etag.

        We could investigate whether, where and how it would be most effective to check for these.
        """
        encoded = {}
        for key, value in entity.items():
            edm_type, value = self.encode_property(key, value)
            try:
                if _ODATA_SUFFIX in key or key + _ODATA_SUFFIX in entity:
                    encoded[key] = value
                    continue
                # The edm type is decided by value
                # For example, when value=EntityProperty(str(uuid.uuid4), "Edm.Guid"),
                # the type is string instead of Guid after encoded
                if edm_type:
                    encoded[key + _ODATA_SUFFIX] = edm_type.value if hasattr(edm_type, "value") else edm_type
            except TypeError as ex:
                pass
            encoded[key] = value
        return encoded
    
    def decode_entity(self, entity: Dict[str, Union[str, int, float, bool]]) -> TableEntity:
        return _convert_to_entity(entity)
