# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import abc
import enum
from typing import Any, Optional, Tuple, Mapping, Union, TypeVar, Generic, Dict
from uuid import UUID
from datetime import datetime
from math import isnan

from ._entity import EdmType, TableEntity
from ._deserialize import _convert_to_entity
from ._common_conversion import _encode_base64, _to_utc_datetime

_ODATA_SUFFIX = "@odata.type"
T = TypeVar("T")


class TableEntityEncoderABC(abc.ABC, Generic[T]):
    def prepare_key(self, key: str) -> str:
        """Duplicate the single quote char to escape.

        :param str key: The entity PartitionKey or RowKey value in table entity.
        :return: The entity PartitionKey or RowKey value in table entity.
        :rtype: str
        """
        try:
            return key.replace("'", "''")
        except (AttributeError, TypeError) as exc:
            raise TypeError("PartitionKey or RowKey must be of type string.") from exc

    def prepare_value(  # pylint: disable=too-many-return-statements
        self, name: Optional[str], value: Any
    ) -> Tuple[Optional[EdmType], Optional[Union[str, int, float, bool]]]:
        """Prepare the encoded value and its edm type.

        :param name: The entity property name.
        :type name: str or None
        :param value: The entity property value.
        :type value: Any
        :return: The value edm type and encoded value.
        :rtype: A tuple of ~azure.data.tables.EdmType or None, and str, int, float, bool or None
        """
        if isinstance(value, bool):
            return None, value
        if isinstance(value, enum.Enum):
            return self.prepare_value(name, value.value)
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
                if hasattr(value, "tables_service_value") and value.tables_service_value:
                    return EdmType.DATETIME, value.tables_service_value
            except AttributeError:
                pass
            return EdmType.DATETIME, _to_utc_datetime(value)
        if isinstance(value, tuple):
            return self._prepare_value_in_tuple(value)
        if value is None:
            return None, None
        if name:
            raise TypeError(f"Unsupported data type '{type(value)}' for entity property '{name}'.")
        raise TypeError(f"Unsupported data type '{type(value)}'.")

    def _prepare_value_in_tuple(  # pylint: disable=too-many-return-statements
        self, value: Tuple[Any, Optional[Union[str, EdmType]]]
    ) -> Tuple[Optional[EdmType], Optional[Union[str, int, float, bool]]]:
        unencoded_value = value[0]
        edm_type = value[1]
        if unencoded_value is None:
            return EdmType(edm_type), unencoded_value
        if edm_type == EdmType.STRING:
            return EdmType.STRING, str(unencoded_value)
        if edm_type == EdmType.INT64:
            return EdmType.INT64, str(unencoded_value)
        if edm_type == EdmType.INT32:
            return EdmType.INT32, int(unencoded_value)
        if edm_type == EdmType.BOOLEAN:
            return EdmType.BOOLEAN, unencoded_value
        if edm_type == EdmType.GUID:
            return EdmType.GUID, str(unencoded_value)
        if edm_type == EdmType.BINARY:
            # Leaving this with the double-encoding bug for now, as per original implementation
            return EdmType.BINARY, _encode_base64(unencoded_value)
        if edm_type == EdmType.DOUBLE:
            if isinstance(unencoded_value, str):
                # Pass a serialized value straight through
                return EdmType.DOUBLE, unencoded_value
            if isnan(unencoded_value):
                return EdmType.DOUBLE, "NaN"
            if unencoded_value == float("inf"):
                return EdmType.DOUBLE, "Infinity"
            if unencoded_value == float("-inf"):
                return EdmType.DOUBLE, "-Infinity"
            return EdmType.DOUBLE, unencoded_value
        if edm_type == EdmType.DATETIME:
            if isinstance(unencoded_value, str):
                # Pass a serialized datetime straight through
                return EdmType.DATETIME, unencoded_value
            try:
                # Check is this is a 'round-trip' datetime, and if so
                # pass through the original value.
                if unencoded_value.tables_service_value:
                    return EdmType.DATETIME, unencoded_value.tables_service_value
            except AttributeError:
                pass
            return EdmType.DATETIME, _to_utc_datetime(unencoded_value)
        raise TypeError(f"Unsupported data type '{type(value)}'.")

    @abc.abstractmethod
    def encode_entity(self, entity: T) -> Dict[str, Union[str, int, float, bool]]:
        """Encode an entity object into JSON format to send out.

        :param entity: A table entity.
        :type entity: Custom entity type
        :return: An entity with property's metadata in JSON format.
        :rtype: dict
        """

    @abc.abstractmethod
    def decode_entity(self, entity: Dict[str, Union[str, int, float, bool]]) -> T: ...


class TableEntityEncoder(TableEntityEncoderABC[Union[TableEntity, Mapping[str, Any]]]):
    def encode_entity(self, entity: Union[TableEntity, Mapping[str, Any]]) -> Dict[str, Union[str, int, float, bool]]:
        """Encode an entity object into JSON format to send out.
        The entity format is:

        .. code-block:: json

            {
                "Address":"Mountain View",
                "Age":23,
                "AmountDue":200.23,
                "CustomerCode@odata.type":"Edm.Guid",
                "CustomerCode":"c9da6455-213d-42c9-9a79-3e9149a57833",
                "CustomerSince@odata.type":"Edm.DateTime",
                "CustomerSince":"2008-07-10T00:00:00",
                "IsActive":true,
                "NumberOfOrders@odata.type":"Edm.Int64",
                "NumberOfOrders":"255",
                "PartitionKey":"my_partition_key",
                "RowKey":"my_row_key"
            }

        :param entity: A table entity.
        :type entity: ~azure.data.tables.TableEntity or Mapping[str, Any]
        :return: An entity with property's metadata in JSON format.
        :rtype: dict
        """
        encoded = {}
        for key, value in entity.items():
            edm_type, value = self.prepare_value(key, value)
            try:
                if _ODATA_SUFFIX in key or key + _ODATA_SUFFIX in entity:
                    encoded[key] = value
                    continue
                # The edm type is decided by value
                # For example, when value=EntityProperty(str(uuid.uuid4), "Edm.Guid"),
                # the type is string instead of Guid after encoded
                if edm_type:
                    encoded[key + _ODATA_SUFFIX] = edm_type.value if hasattr(edm_type, "value") else edm_type
            except TypeError:
                pass
            encoded[key] = value
        return encoded

    def decode_entity(self, entity: Dict[str, Union[str, int, float, bool]]) -> TableEntity:
        return _convert_to_entity(entity)
