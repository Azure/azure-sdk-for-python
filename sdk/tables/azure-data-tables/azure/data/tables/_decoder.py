# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import abc
from typing import Any, Optional, Tuple, Mapping, Union, TypeVar, Generic, Dict
from datetime import datetime, timezone
from urllib.parse import quote
from uuid import UUID

from ._common_conversion import _decode_base64_to_bytes
from ._encoder import T
from ._entity import EntityProperty, EdmType, TableEntity
from ._deserialize import TablesEntityDatetime


def _from_entity_datetime(value):
    # Cosmos returns this with a decimal point that throws an error on deserialization
    value = value.split(".")
    if len(value) == 2:
        ms = value[-1].replace("Z", "")
        if len(ms) > 6:
            ms = ms[:6]
        ms = ms + "Z"
        cleaned_value = ".".join([value[0], ms])
    else:
        cleaned_value = value[0]

    try:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    dt_obj._service_value = value  # pylint:disable=protected-access,assigning-non-slot
    return dt_obj


class TableEntityDecoderABC(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def decode_entity(self, entity_json: Dict[str, Union[str, int, float, bool]]) -> T:
        """Decode the entity in response in JSON format to a custom entity type.

        :param entity: A table entity.
        :type entity: Custom entity type
        :return: An entity with property's metadata in JSON format.
        :rtype: dict
        """


class TableEntityDecoder(TableEntityDecoderABC[Union[TableEntity, Mapping[str, Any]]]):
    def decode_entity(self, entity_json: Dict[str, Union[str, int, float, bool]]) -> Union[TableEntity, Mapping[str, Any]]:
        """Decode the entity in response in JSON format to TableEntity type.
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

        :param entity_json: An entity with property's metadata in JSON format.
        :type entity_json: dict
        :return: A table entity.
        :rtype: ~azure.data.tables.TableEntity or Mapping[str, Any]
        """
        decoded = TableEntity()

        properties = {}
        edmtypes = {}
        odata = {}

        for name, value in entity_json.items():
            if name.startswith("odata."):
                odata[name[6:]] = value
            elif name.endswith("@odata.type"):
                edmtypes[name[:-11]] = value
            else:
                properties[name] = value

        # prepare metadata
        timestamp = properties.pop("Timestamp", None)
        etag = odata.pop("etag", None)
        if timestamp:
            if not etag:
                etag = "W/\"datetime'" + quote(timestamp) + "'\""
            timestamp = _from_entity_datetime(timestamp)
            decoded.metadata["etag"] = etag
            decoded.metadata["timestamp"] = timestamp

        for name, value in properties.items():
            if name in ["PartitionKey", "RowKey"]:
                decoded[name] = value
                continue
            
            edm_type = edmtypes.get(name)
            if isinstance(value, int) and edm_type is None:
                if value >= 2**31 or value < (-(2**31)):
                    edm_type = EdmType.INT64

            if not edm_type:
                decoded[name] = value # no type info, property should parse automatically
            elif edm_type == EdmType.BINARY:
                decoded[name] = _decode_base64_to_bytes(value)
            elif edm_type == EdmType.DOUBLE:
                decoded[name] = float(value)
            elif edm_type == EdmType.INT64:
                decoded[name] = EntityProperty(int(value), edm_type)
            elif edm_type == EdmType.DATETIME:
                decoded[name] = _from_entity_datetime(value)
            elif edm_type == EdmType.GUID:
                decoded[name] = UUID(value)
            else:
                decoded[name] = EntityProperty(value, edm_type)

        return decoded
