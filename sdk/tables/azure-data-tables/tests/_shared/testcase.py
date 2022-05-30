# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import division
from base64 import b64encode
from datetime import datetime, timedelta
from dateutil.tz import tzutc
import uuid

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
    _error
)
from azure.data.tables._error import _decode_error
from azure.identity import DefaultAzureCredential

from devtools_testutils import is_live

SLEEP_DELAY = 30

TEST_TABLE_PREFIX = "pytablesync"

SERVICE_UNAVAILABLE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>unavailable</Status><LastSyncTime></LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '

SERVICE_LIVE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                         '>live</Status><LastSyncTime>Wed, 19 Jan 2021 22:28:43 GMT</LastSyncTime></GeoReplication' \
                         '></StorageServiceStats> '


class FakeTokenCredential(object):
    """Protocol for classes able to provide OAuth tokens.
    :param str scopes: Lets you specify the type of access needed.
    """

    def __init__(self):
        self.token = AccessToken("YOU SHALL NOT PASS", 0)

    def get_token(self, *args, **kwargs):
        return self.token


class TableTestCase(object):
    def connection_string(self, account, key):
        return (
            "DefaultEndpointsProtocol=https;AccountName="
            + account
            + ";AccountKey="
            + str(key)
            + ";EndpointSuffix=core.windows.net"
        )

    def account_url(self, account, endpoint_type):
        """Return an url of storage account.

        :param str storage_account: Storage account name
        :param str storage_type: The Storage type part of the URL. Should be "table", or "cosmos", etc.
        """
        try:
            if endpoint_type == "table":
                return account.primary_endpoints.table.rstrip("/")
            if endpoint_type == "cosmos":
                return "https://{}.table.cosmos.azure.com".format(account.name)
        except AttributeError:  # Didn't find "primary_endpoints"
            if endpoint_type == "table":
                return "https://{}.{}.core.windows.net".format(account, endpoint_type)
            if endpoint_type == "cosmos":
                return "https://{}.table.cosmos.azure.com".format(account)

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
            return DefaultAzureCredential()
        return self.generate_fake_token()

    def generate_fake_token(self):
        return FakeTokenCredential()

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
            "sex": u"male",
            "married": True,
            "deceased": False,
            "optional": None,
            "ratio": 3.1,
            "evenratio": 3.0,
            "double": (5, EdmType.DOUBLE),
            "large": 933311100,
            "Birthday": datetime(1973, 10, 4, tzinfo=tzutc()),
            "birthday": datetime(1970, 10, 4, tzinfo=tzutc()),
            "binary": b"binary",
            "other": EntityProperty(20, EdmType.INT32),
            "clsid": uuid.UUID("c9da6455-213d-42c9-9a79-3e9149a57833"),
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
            "age": u"abc",
            "sex": u"female",
            "sign": u"aquarius",
            "birthday": datetime(1991, 10, 4, tzinfo=tzutc()),
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
        assert entity["Birthday"] == datetime(1973, 10, 4, tzinfo=tzutc())
        assert entity["birthday"] == datetime(1970, 10, 4, tzinfo=tzutc())
        assert entity["binary"] == b"binary"
        assert entity["other"] == 20
        assert entity["clsid"] == uuid.UUID("c9da6455-213d-42c9-9a79-3e9149a57833")
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
        assert entity["Birthday"] == datetime(1973, 10, 4, tzinfo=tzutc())
        assert entity["birthday"] == datetime(1970, 10, 4, tzinfo=tzutc())
        assert entity["binary"] == b"binary"
        assert entity["other"] == 20
        assert entity["clsid"] == uuid.UUID("c9da6455-213d-42c9-9a79-3e9149a57833")
        assert entity.metadata.pop("etag", None)
        assert isinstance(entity.metadata.pop("timestamp", None), datetime)
        assert sorted(list(entity.metadata.keys())) == ['editLink', 'id', 'type'], "Found metadata: {}".format(entity.metadata)

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
        assert entity["birthday"] == datetime(1991, 10, 4, tzinfo=tzutc())
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
        assert entity["Birthday"] == datetime(1973, 10, 4, tzinfo=tzutc())
        assert entity["birthday"] == datetime(1991, 10, 4, tzinfo=tzutc())
        assert entity["other"] == 20
        assert isinstance(entity["clsid"], uuid.UUID)
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
        self._assert_cors_equal(prop["cors"], list())

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
            "PartitionKey": partition + u"1",
            "RowKey": row + u"1",
            "age": 49,
            "sex": u"female",
            "married": False,
            "deceased": True,
            "optional": None,
            "ratio": 5.2,
            "evenratio": 6.0,
            "large": 39999011,
            "Birthday": datetime(1993, 4, 1, tzinfo=tzutc()),
            "birthday": datetime(1990, 4, 1, tzinfo=tzutc()),
            "binary": b"binary-binary",
            "other": EntityProperty(40, EdmType.INT32),
            "clsid": uuid.UUID("c8da6455-213e-42d9-9b79-3f9149a57833"),
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
                error.error_code = 'ResourceNotFoundError'
                return error
    except DecodeError:
        pass
    return _decode_error(response, error_message, error_type, **kwargs)

_error._decode_error = _decode_proxy_error
