# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Callable, Dict, Optional, Union, Any, Mapping, Type, Tuple
from urllib.parse import quote
from base64 import b64encode
from datetime import datetime, timedelta, timezone
from uuid import UUID
from enum import Enum
from math import isnan
import os

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.credentials import AccessToken, AzureNamedKeyCredential
from azure.core.exceptions import ResourceExistsError, DecodeError, ResourceNotFoundError
from azure.data.tables import (
    generate_account_sas,
    AccountSasPermissions,
    ResourceTypes,
    EntityProperty,
    EdmType,
    TableEntity,
    TableAnalyticsLogging,
    TableMetrics,
    TableServiceClient,
    _error,
)
from azure.data.tables._constants import DEFAULT_COSMOS_ENDPOINT_SUFFIX, DEFAULT_STORAGE_ENDPOINT_SUFFIX
from azure.data.tables._error import _decode_error
from azure.data.tables._common_conversion import _encode_base64, _to_utc_datetime, _decode_base64_to_bytes

from devtools_testutils import is_live, get_credential

TEST_TABLE_PREFIX = "pytablesync"

SERVICE_UNAVAILABLE_RESP_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status'
    ">unavailable</Status><LastSyncTime></LastSyncTime></GeoReplication"
    "></StorageServiceStats> "
)

SERVICE_LIVE_RESP_BODY = (
    '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status'
    ">live</Status><LastSyncTime>Wed, 19 Jan 2021 22:28:43 GMT</LastSyncTime></GeoReplication"
    "></StorageServiceStats> "
)

_ERROR_TYPE_NOT_SUPPORTED = "Type not supported when sending data to the service: {0}."
_ERROR_VALUE_TOO_LARGE = "{0} is too large to be cast to type {1}."


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args, **kwargs):
        return self.token


class TableTestCase(object):
    def account_url(self, account, endpoint_type):
        """Return an url of storage account.

        :param str storage_account: Storage account name
        :param str storage_type: The Storage type part of the URL. Should be "table", or "cosmos", etc.
        """
        try:
            if endpoint_type == "table":
                return account.primary_endpoints.table.rstrip("/")
            if endpoint_type == "cosmos":
                return "https://{}.table.{}".format(
                    account.name, os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
                )
        except AttributeError:  # Didn't find "primary_endpoints"
            if endpoint_type == "table":
                return "https://{}.table.{}".format(
                    account, os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX", DEFAULT_STORAGE_ENDPOINT_SUFFIX)
                )
            if endpoint_type == "cosmos":
                return "https://{}.table.{}".format(
                    account, os.getenv("TABLES_COSMOS_ENDPOINT_SUFFIX", DEFAULT_COSMOS_ENDPOINT_SUFFIX)
                )

    def generate_sas_token(self):
        fake_key = "a" * 30 + "b" * 30

        return "?" + generate_account_sas(
            credential=AzureNamedKeyCredential(name="fakename", key=fake_key),
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True, list=True),
            start=datetime.now() - timedelta(hours=24),
            expiry=datetime.now() + timedelta(days=8),
        )

    def get_token_credential(self):
        if is_live():
            return get_credential()
        return self.generate_fake_token_credential()

    def generate_fake_token_credential(self):
        return FakeTokenCredential()

    def get_datetime(self):
        return datetime(year=2022, month=4, day=1, hour=9, minute=30, second=45, tzinfo=timezone.utc)

    def set_uuid_variable(self, variables, name, uuid_param):
        uuid_string = variables.setdefault(name, str(uuid_param))
        return UUID(uuid_string)

    def _get_table_reference(self, prefix=TEST_TABLE_PREFIX):
        table_name = self.get_resource_name(prefix)
        return table_name

    def _create_table(self, ts, prefix=TEST_TABLE_PREFIX, table_list=None):
        table_name = self._get_table_reference(prefix)
        try:
            table = ts.create_table(table_name)
            if table_list is not None:
                table_list.append(table)
        except ResourceExistsError:
            table = ts.get_table_client(table_name)
        return table

    def _delete_all_tables(self, ts):
        if self.is_live:
            for table in ts.list_tables():
                ts.delete_table(table.name)
            self.sleep(10)

    def _create_pk_rk(self, pk, rk):
        try:
            pk = pk if pk is not None else self.get_resource_name("pk").decode("utf-8")
            rk = rk if rk is not None else self.get_resource_name("rk").decode("utf-8")
        except AttributeError:
            pk = pk if pk is not None else self.get_resource_name("pk")
            rk = rk if rk is not None else self.get_resource_name("rk")
        return pk, rk

    def _create_random_base_entity_dict(self):
        """
        Creates a dict-based entity with only pk and rk.
        """
        partition, row = self._create_pk_rk(None, None)
        return {
            "PartitionKey": partition,
            "RowKey": row,
        }

    def _create_random_entity_dict(self, pk=None, rk=None):
        """
        Creates a dictionary-based entity with fixed values, using all
        of the supported data types.
        """
        partition, row = self._create_pk_rk(pk, rk)
        properties = {
            "PartitionKey": partition,
            "RowKey": row,
            "age": 39,
            "sex": "male",
            "married": True,
            "deceased": False,
            "optional": None,
            "ratio": 3.1,
            "evenratio": 3.0,
            "double": (5, EdmType.DOUBLE),
            "large": 933311100,
            "Birthday": datetime(1973, 10, 4, tzinfo=timezone.utc),
            "birthday": datetime(1970, 10, 4, tzinfo=timezone.utc),
            "binary": b"binary",
            "other": EntityProperty(20, EdmType.INT32),
            "clsid": UUID("c9da6455-213d-42c9-9a79-3e9149a57833"),
        }
        return TableEntity(**properties)

    def _create_updated_entity_dict(self, partition, row):
        """
        Creates a dictionary-based entity with fixed values, with a
        different set of values than the default entity. It
        adds fields, changes field values, changes field types,
        and removes fields when compared to the default entity.
        """
        return {
            "PartitionKey": partition,
            "RowKey": row,
            "age": "abc",
            "sex": "female",
            "sign": "aquarius",
            "birthday": datetime(1991, 10, 4, tzinfo=timezone.utc),
        }

    def _assert_default_entity(self, entity):
        """
        Asserts that the entity passed in matches the default entity.
        """
        assert entity["age"] == 39
        assert entity["sex"] == "male"
        assert entity["married"] == True
        assert entity["deceased"] == False
        assert not "optional" in entity
        assert entity["ratio"] == 3.1
        assert entity["evenratio"] == 3.0
        assert entity["double"] == 5.0
        assert entity["large"] == 933311100
        assert entity["Birthday"] == datetime(1973, 10, 4, tzinfo=timezone.utc)
        assert entity["birthday"] == datetime(1970, 10, 4, tzinfo=timezone.utc)
        assert entity["binary"] == b"binary"
        assert entity["other"] == 20
        assert entity["clsid"] == UUID("c9da6455-213d-42c9-9a79-3e9149a57833")
        assert entity.metadata.pop("etag", None)
        assert isinstance(entity.metadata.pop("timestamp", None), datetime)
        assert not entity.metadata, "Found metadata: {}".format(entity.metadata)

    def _assert_default_entity_json_full_metadata(self, entity, headers=None):
        """
        Asserts that the entity passed in matches the default entity.
        """
        assert entity["age"] == 39
        assert entity["sex"] == "male"
        assert entity["married"] == True
        assert entity["deceased"] == False
        assert not "optional" in entity
        assert not "aquarius" in entity
        assert entity["ratio"] == 3.1
        assert entity["evenratio"] == 3.0
        assert entity["double"] == 5.0
        assert entity["large"] == 933311100
        assert entity["Birthday"] == datetime(1973, 10, 4, tzinfo=timezone.utc)
        assert entity["birthday"] == datetime(1970, 10, 4, tzinfo=timezone.utc)
        assert entity["binary"] == b"binary"
        assert entity["other"] == 20
        assert entity["clsid"] == UUID("c9da6455-213d-42c9-9a79-3e9149a57833")
        assert entity.metadata.pop("etag", None)
        assert isinstance(entity.metadata.pop("timestamp", None), datetime)
        assert sorted(list(entity.metadata.keys())) == ["editLink", "id", "type"], "Found metadata: {}".format(
            entity.metadata
        )

    def _assert_default_entity_json_no_metadata(self, entity, headers=None):
        """
        Asserts that the entity passed in matches the default entity.
        """
        assert entity["age"] == 39
        assert entity["sex"] == "male"
        assert entity["married"] == True
        assert entity["deceased"] == False
        assert not "optional" in entity
        assert not "aquarius" in entity
        assert entity["ratio"] == 3.1
        assert entity["evenratio"] == 3.0
        assert entity["double"] == 5.0
        assert entity["large"] == 933311100
        assert entity["Birthday"].startswith("1973-10-04T00:00:00")
        assert entity["birthday"].startswith("1970-10-04T00:00:00")
        assert entity["Birthday"].endswith("00Z")
        assert entity["birthday"].endswith("00Z")
        assert entity["binary"] == b64encode(b"binary").decode("utf-8")
        assert entity["other"] == 20
        assert entity["clsid"] == "c9da6455-213d-42c9-9a79-3e9149a57833"
        assert entity.metadata.pop("etag", None)
        assert isinstance(entity.metadata.pop("timestamp", None), datetime)
        assert not entity.metadata

    def _assert_updated_entity(self, entity):
        """
        Asserts that the entity passed in matches the updated entity.
        """
        assert entity["age"] == "abc"
        assert entity["sex"] == "female"
        assert not "married" in entity
        assert not "deceased" in entity
        assert entity["sign"] == "aquarius"
        assert not "optional" in entity
        assert not "ratio" in entity
        assert not "evenratio" in entity
        assert not "double" in entity
        assert not "large" in entity
        assert not "Birthday" in entity
        assert entity["birthday"] == datetime(1991, 10, 4, tzinfo=timezone.utc)
        assert not "other" in entity
        assert not "clsid" in entity
        assert entity.metadata["etag"]
        assert entity.metadata["timestamp"]

    def _assert_merged_entity(self, entity):
        """
        Asserts that the entity passed in matches the default entity
        merged with the updated entity.
        """
        assert entity["age"] == "abc"
        assert entity["sex"] == "female"
        assert entity["sign"] == "aquarius"
        assert entity["married"] == True
        assert entity["deceased"] == False
        assert entity["ratio"] == 3.1
        assert entity["evenratio"] == 3.0
        assert entity["double"] == 5.0
        assert entity["large"] == 933311100
        assert entity["Birthday"] == datetime(1973, 10, 4, tzinfo=timezone.utc)
        assert entity["birthday"] == datetime(1991, 10, 4, tzinfo=timezone.utc)
        assert entity["other"] == 20
        assert isinstance(entity["clsid"], UUID)
        assert str(entity["clsid"]) == "c9da6455-213d-42c9-9a79-3e9149a57833"
        assert entity.metadata["etag"]
        assert entity.metadata["timestamp"]

    def _assert_valid_metadata(self, metadata):
        keys = metadata.keys()
        assert "version" in keys
        assert "date" in keys
        assert "etag" in keys
        assert len(keys) == 3

    def _assert_valid_batch_transaction(self, transaction, length):
        assert length == len(transaction)

    def _assert_properties_default(self, prop):
        assert prop is not None

        self._assert_logging_equal(prop["analytics_logging"], TableAnalyticsLogging())
        self._assert_metrics_equal(prop["hour_metrics"], TableMetrics())
        self._assert_metrics_equal(prop["minute_metrics"], TableMetrics())
        self._assert_cors_equal(prop["cors"], [])

    def _assert_policy_datetime(self, val1, val2):
        assert isinstance(val2, datetime)
        assert val1.year == val2.year
        assert val1.month == val2.month
        assert val1.day == val2.day
        assert val1.hour == val2.hour
        assert val1.minute == val2.minute
        assert val1.second == val2.second

    def _assert_logging_equal(self, log1, log2):
        if log1 is None or log2 is None:
            assert log1 == log2
            return

        assert log1.version == log2.version
        assert log1.read == log2.read
        assert log1.write == log2.write
        assert log1.delete == log2.delete
        self._assert_retention_equal(log1.retention_policy, log2.retention_policy)

    def _assert_delete_retention_policy_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            assert policy1 == policy2
            return

        assert policy1.enabled == policy2.enabled
        assert policy1.days == policy2.days

    def _assert_static_website_equal(self, prop1, prop2):
        if prop1 is None or prop2 is None:
            assert prop1 == prop2
            return

        assert prop1.enabled == prop2.enabled
        assert prop1.index_document == prop2.index_document
        assert prop1.error_document404_path == prop2.error_document404_path

    def _assert_delete_retention_policy_not_equal(self, policy1, policy2):
        if policy1 is None or policy2 is None:
            assert policy1 != policy2
            return

        assert policy1.enabled == policy2.enabled and policy1.days == policy2.days

    def _assert_metrics_equal(self, metrics1, metrics2):
        if metrics1 is None or metrics2 is None:
            assert metrics1 == metrics2
            return

        assert metrics1.version == metrics2.version
        assert metrics1.enabled == metrics2.enabled
        assert metrics1.include_apis == metrics2.include_apis
        self._assert_retention_equal(metrics1.retention_policy, metrics2.retention_policy)

    def _assert_cors_equal(self, cors1, cors2):
        if cors1 is None or cors2 is None:
            assert cors1 == cors2
            return

        assert len(cors1) == len(cors2)
        for i in range(0, len(cors1)):
            rule1 = cors1[i]
            rule2 = cors2[i]
            assert sorted(rule1.allowed_origins) == sorted(rule2.allowed_origins)
            assert sorted(rule1.allowed_methods) == sorted(rule2.allowed_methods)
            assert rule1.max_age_in_seconds == rule2.max_age_in_seconds
            assert sorted(rule1.exposed_headers) == sorted(rule2.exposed_headers)
            assert sorted(rule1.allowed_headers) == sorted(rule2.allowed_headers)

    def _assert_retention_equal(self, ret1, ret2):
        assert ret1.enabled == ret2.enabled
        assert ret1.days == ret2.days

    def _tear_down(self):
        if is_live():
            self._delete_all_tables(self.ts)
            self.test_tables = []
            self.ts.close()

    def _create_query_table(self, entity_count):
        """
        Creates a table with the specified name and adds entities with the
        default set of values. PartitionKey is set to 'MyPartition' and RowKey
        is set to a unique counter value starting at 1 (as a string).
        """
        table_name = self.get_resource_name("querytable")
        table = self.ts.create_table(table_name)
        self.query_tables.append(table_name)
        client = self.ts.get_table_client(table_name)
        entity = self._create_random_entity_dict()
        for i in range(1, entity_count + 1):
            entity["RowKey"] = entity["RowKey"] + str(i)
            client.create_entity(entity)
        return client

    def _insert_two_opposite_entities(self, pk=None, rk=None):
        entity1 = self._create_random_entity_dict()
        resp = self.table.create_entity(entity1)

        partition, row = self._create_pk_rk(pk, rk)
        properties = {
            "PartitionKey": partition + "1",
            "RowKey": row + "1",
            "age": 49,
            "sex": "female",
            "married": False,
            "deceased": True,
            "optional": None,
            "ratio": 5.2,
            "evenratio": 6.0,
            "large": 39999011,
            "Birthday": datetime(1993, 4, 1, tzinfo=timezone.utc),
            "birthday": datetime(1990, 4, 1, tzinfo=timezone.utc),
            "binary": b"binary-binary",
            "other": EntityProperty(40, EdmType.INT32),
            "clsid": UUID("c8da6455-213e-42d9-9b79-3f9149a57833"),
        }
        self.table.create_entity(properties)
        return entity1, resp

    def _insert_random_entity(self, pk=None, rk=None):
        entity = self._create_random_entity_dict(pk, rk)
        metadata = self.table.create_entity(entity)
        return entity, metadata["etag"]

    def _set_up(self, account_name, credential, url="table"):
        self.table_name = self.get_resource_name("uttable")
        self.ts = TableServiceClient(
            self.account_url(account_name, url), credential=credential, table_name=self.table_name
        )
        self.table = self.ts.get_table_client(self.table_name)
        if self.is_live:
            try:
                self.ts.create_table(self.table_name)
            except ResourceExistsError:
                pass

        self.query_tables = []

    def _assert_stats_default(self, stats):
        assert stats is not None
        assert stats["geo_replication"] is not None

        assert stats["geo_replication"]["status"] == "live"
        assert stats["geo_replication"]["last_sync_time"] is not None

    def _assert_stats_unavailable(self, stats):
        assert stats is not None
        assert stats["geo_replication"] is not None

        assert stats["geo_replication"]["status"] == "unavailable"
        assert stats["geo_replication"]["last_sync_time"] is None

    @staticmethod
    def override_response_body_with_unavailable_status(response):
        response.http_response.text = lambda _: SERVICE_UNAVAILABLE_RESP_BODY

    @staticmethod
    def override_response_body_with_live_status(response):
        response.http_response.text = lambda _: SERVICE_LIVE_RESP_BODY


class ResponseCallback(object):
    def __init__(self, status=None, new_status=None):
        self.status = status
        self.new_status = new_status
        self.first = True
        self.count = 0

    def override_first_status(self, response):
        if self.first and response.http_response.status_code == self.status:
            response.http_response.status_code = self.new_status
            self.first = False
        self.count += 1

    def override_status(self, response):
        if response.http_response.status_code == self.status:
            response.http_response.status_code = self.new_status
        self.count += 1


class RetryCounter(object):
    def __init__(self):
        self.count = 0

    def simple_count(self, retry_context):
        self.count += 1


def _decode_proxy_error(response, error_message=None, error_type=None, **kwargs):  # pylint: disable=too-many-branches
    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(response)
        if isinstance(error_body, dict):
            # Special case: there was a playback error during test execution (test proxy only)
            message = error_body.get("Message")
            if message and message.startswith("Unable to find a record for the request"):
                error = ResourceNotFoundError(message=error_message, response=response)
                error.error_code = "ResourceNotFoundError"
                return error
    except DecodeError:
        pass
    return _decode_error(response, error_message, error_type, **kwargs)


_error._decode_error = _decode_proxy_error


def _to_entity_binary(value):
    return EdmType.BINARY, _encode_base64(value)


def _to_entity_bool(value):
    return None, value


def _to_entity_datetime(value):
    if isinstance(value, str):
        # Pass a serialized datetime straight through
        return EdmType.DATETIME, value
    try:
        # Check is this is a 'round-trip' datetime, and if so
        # pass through the original value.
        if value.tables_service_value:
            return EdmType.DATETIME, value.tables_service_value
    except AttributeError:
        pass
    return EdmType.DATETIME, _to_utc_datetime(value)


def _to_entity_float(value):
    if isinstance(value, str):
        # Pass a serialized value straight through
        return EdmType.DOUBLE, value
    if isnan(value):
        return EdmType.DOUBLE, "NaN"
    if value == float("inf"):
        return EdmType.DOUBLE, "Infinity"
    if value == float("-inf"):
        return EdmType.DOUBLE, "-Infinity"
    return EdmType.DOUBLE, value


def _to_entity_guid(value):
    return EdmType.GUID, str(value)


def _to_entity_int32(value):
    value = int(value)
    if value >= 2**31 or value < -(2**31):
        raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT32))
    return None, value


def _to_entity_int64(value):
    int_value = int(value)
    if int_value >= 2**63 or int_value < -(2**63):
        raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT64))
    return EdmType.INT64, str(value)


def _to_entity_str(value):
    return EdmType.STRING, str(value)


# Conversion from Python type to a function which returns a tuple of the
# type string and content string.
_PYTHON_TO_ENTITY_CONVERSIONS: Dict[Type, Callable[[Any], Tuple[Optional[EdmType], Any]]] = {
    int: _to_entity_int32,
    bool: _to_entity_bool,
    datetime: _to_entity_datetime,
    float: _to_entity_float,
    UUID: _to_entity_guid,
    Enum: _to_entity_str,
    str: _to_entity_str,
    bytes: _to_entity_binary,
}

# Conversion from Edm type to a function which returns a tuple of the
# type string and content string. These conversions are only used when the
# full EdmProperty tuple is specified. As a result, in this case we ALWAYS add
# the Odata type tag, even for field types where it's not necessary. This is why
# boolean and int32 have special processing below, as we would not normally add the
# Odata type tags for these to keep payload size minimal.
# This is also necessary for CLI compatibility.
_EDM_TO_ENTITY_CONVERSIONS: Dict[EdmType, Callable[[Any], Tuple[Optional[EdmType], Any]]] = {
    EdmType.BINARY: _to_entity_binary,
    EdmType.BOOLEAN: lambda v: (EdmType.BOOLEAN, v),
    EdmType.DATETIME: _to_entity_datetime,
    EdmType.DOUBLE: _to_entity_float,
    EdmType.GUID: _to_entity_guid,
    EdmType.INT32: lambda v: (EdmType.INT32, _to_entity_int32(v)[1]),  # Still using the int32 validation
    EdmType.INT64: _to_entity_int64,
    EdmType.STRING: _to_entity_str,
}


class TablesEntityDatetime(datetime):
    @property
    def tables_service_value(self):
        try:
            return self._service_value
        except AttributeError:
            return ""


def _from_entity_guid(value):
    return UUID(value)


def _from_entity_str(value: Union[str, bytes]) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def _from_entity_binary(value: str) -> bytes:
    return _decode_base64_to_bytes(value)


def _from_entity_int32(value: str) -> int:
    return int(value)


def _from_entity_int64(value: str) -> EntityProperty:
    return EntityProperty(int(value), EdmType.INT64)


def _clean_up_dotnet_timestamps(value):
    # .NET has more decimal places than Python supports in datetime objects, this truncates
    # values after 6 decimal places.
    value = value.split(".")
    ms = ""
    if len(value) == 2:
        ms = value[-1].replace("Z", "")
        if len(ms) > 6:
            ms = ms[:6]
        ms = ms + "Z"
        return ".".join([value[0], ms])

    return value[0]


def _from_entity_datetime(value):
    # Cosmos returns this with a decimal point that throws an error on deserialization
    cleaned_value = _clean_up_dotnet_timestamps(value)
    try:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    dt_obj._service_value = value  # pylint:disable=protected-access,assigning-non-slot
    return dt_obj


_ENTITY_TO_PYTHON_CONVERSIONS = {
    EdmType.BINARY: _from_entity_binary,
    EdmType.INT32: _from_entity_int32,
    EdmType.INT64: _from_entity_int64,
    EdmType.DOUBLE: float,
    EdmType.DATETIME: _from_entity_datetime,
    EdmType.GUID: _from_entity_guid,
    EdmType.STRING: _from_entity_str,
}


# The old encoder
def _add_entity_properties(source: Union[TableEntity, Mapping[str, Any]]) -> Dict[str, Any]:
    """Converts an entity object to json to send.
    The entity format is:
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

    :param source: A table entity.
    :type source: ~azure.data.tables.TableEntity or Mapping[str, Any]
    :return: An entity with property's metadata in JSON format.
    :rtype: dict
    """

    properties = {}

    to_send = dict(source)  # shallow copy

    # set properties type for types we know if value has no type info.
    # if value has type info, then set the type to value.type
    for name, value in to_send.items():
        if value is None:
            continue
        mtype: Optional[EdmType] = None
        if isinstance(value, Enum):
            convert = _PYTHON_TO_ENTITY_CONVERSIONS[str]
            mtype, value = convert(value)
        elif isinstance(value, datetime):
            mtype, value = _to_entity_datetime(value)
        elif isinstance(value, tuple):
            if value[0] is None:
                continue
            convert = _EDM_TO_ENTITY_CONVERSIONS[EdmType(value[1])]
            mtype, value = convert(value[0])
        else:
            try:
                convert = _PYTHON_TO_ENTITY_CONVERSIONS[type(value)]
            except KeyError:
                raise TypeError(_ERROR_TYPE_NOT_SUPPORTED.format(type(value))) from None
            mtype, value = convert(value)

        # form the property node
        properties[name] = value
        if mtype:
            properties[name + "@odata.type"] = mtype.value

    # generate the entity_body
    return properties


# The old decoder
def _convert_to_entity(entry_element):
    """Convert json response to entity.
    The entity format is:
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

    :param entry_element: The entity in response.
    :type entry_element: Mapping[str, Any]
    :return: An entity dict with additional metadata.
    :rtype: dict[str, Any]
    """
    entity = TableEntity()

    properties = {}
    edmtypes = {}
    odata = {}

    for name, value in entry_element.items():
        if name.startswith("odata."):
            odata[name[6:]] = value
        elif name.endswith("@odata.type"):
            edmtypes[name[:-11]] = value
        else:
            properties[name] = value

    partition_key = properties.pop("PartitionKey", None)
    if partition_key is not None:
        entity["PartitionKey"] = partition_key

    # Row key is a known property
    row_key = properties.pop("RowKey", None)
    if row_key is not None:
        entity["RowKey"] = row_key

    # Timestamp is a known property
    timestamp = properties.pop("Timestamp", None)

    for name, value in properties.items():
        mtype = edmtypes.get(name)

        # Add type for Int32/64
        if isinstance(value, int) and mtype is None:
            mtype = EdmType.INT32

            if value >= 2**31 or value < (-(2**31)):
                mtype = EdmType.INT64

        # Add type for String
        if isinstance(value, str) and mtype is None:
            mtype = EdmType.STRING

        # no type info, property should parse automatically
        if not mtype:
            entity[name] = value
        elif mtype in [EdmType.STRING, EdmType.INT32]:
            entity[name] = value
        else:  # need an object to hold the property
            convert = _ENTITY_TO_PYTHON_CONVERSIONS.get(mtype)
            if convert is not None:
                new_property = convert(value)
            else:
                new_property = EntityProperty(mtype, value)
            entity[name] = new_property

    # extract etag from entry
    etag = odata.pop("etag", None)
    odata.pop("metadata", None)
    if timestamp:
        if not etag:
            etag = "W/\"datetime'" + quote(timestamp) + "'\""
        timestamp = _from_entity_datetime(timestamp)
    odata.update({"etag": etag, "timestamp": timestamp})
    entity._metadata = odata  # pylint: disable=protected-access
    return entity
