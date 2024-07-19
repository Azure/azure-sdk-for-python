# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import time

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, ResponseCallback

from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    AzureError,
    ServiceResponseError,
    ServiceRequestError,
)
from azure.core.pipeline.policies import RetryMode
from azure.core.pipeline.transport import RequestsTransport
from azure.data.tables import TableServiceClient, TableClient
from azure.data.tables._models import LocationMode

from _shared.testcase import TableTestCase

from preparers import tables_decorator
from requests.exceptions import ReadTimeout


class RetryRequestTransport(RequestsTransport):
    """Transport to test retry"""

    def __init__(self, *args, **kwargs):
        super(RetryRequestTransport, self).__init__(*args, **kwargs)
        self.count = 0

    def send(self, request, **kwargs):
        self.count += 1
        assert "connection_timeout" in kwargs.keys()
        assert "read_timeout" in kwargs.keys()
        timeout_error = ReadTimeout("Read timed out", request=request)
        raise ServiceResponseError(timeout_error, error=timeout_error)


class FailoverRetryTransport(RequestsTransport):
    """Transport to attempt to raise on first request but allow requests to secondary location.
    To simulate a failover scenario, pass the exception into the `failover` keyword arg on the method
    you wish to test, e.g.:
    client.get_entity("foo", "bar", failover=ServiceRequestError("Attempting to force failover"))
    """

    def __init__(self, location_mode="primary", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location_mode = location_mode
        self._already_raised = False

    def send(self, request, **kwargs):
        # DELETE operation is not allowed on secondary endpoint
        if request.method != "DELETE":
            if self._already_raised or self.location_mode == "secondary":
                assert "-secondary" in request.url
            else:
                assert "-secondary" not in request.url
        failover_on_error = kwargs.pop("failover", None)
        if failover_on_error and not self._already_raised:
            self._already_raised = True
            raise failover_on_error

        self._already_raised = False
        return super().send(request, **kwargs)


class SecondpageFailoverRetryTransport(RequestsTransport):
    """Transport to attempt to raise while listing on second page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._already_raised = False
        self.count = 0

    def send(self, request, **kwargs):
        if self._already_raised:
            assert "-secondary" in request.url
        else:
            assert "-secondary" not in request.url

        self.count += 1
        failover_on_error = kwargs.pop("failover", None)
        if self.count >= 2 and failover_on_error and not self._already_raised:
            self.count -= 1
            self._already_raised = True
            raise failover_on_error

        self._already_raised = False
        return super().send(request, **kwargs)


# --Test Class -----------------------------------------------------------------
class TestStorageRetry(AzureRecordedTestCase, TableTestCase):
    def _set_up(
        self, tables_storage_account_name, tables_primary_storage_account_key, url="table", default_table=True, **kwargs
    ):
        self.table_name = self.get_resource_name("uttable")
        self.ts = TableServiceClient(
            self.account_url(tables_storage_account_name, url), credential=tables_primary_storage_account_key, **kwargs
        )
        self.table = self.ts.get_table_client(self.table_name)
        if self.is_live and default_table:
            try:
                self.ts.create_table(self.table_name)
            except ResourceExistsError:
                pass

        self.query_tables = []

    # TODO: Figure out why this is needed by the "test_retry_on_socket_timeout" test
    def _tear_down(self, **kwargs):
        if self.is_live:
            try:
                self.ts.delete_table(self.table_name, **kwargs)
            except:
                pass

            try:
                for table_name in self.query_tables:
                    try:
                        self.ts.delete_table(table_name, **kwargs)
                    except:
                        pass
            except AttributeError:
                pass

    # --Test Cases --------------------------------------------
    @tables_decorator
    @recorded_by_proxy
    def test_retry_on_server_error(self, tables_storage_account_name, tables_primary_storage_account_key):
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key, default_table=False)
        try:
            callback = ResponseCallback(status=201, new_status=500).override_status

            new_table_name = self.get_resource_name("uttable")
            # The initial create will return 201, but we overwrite it with 500 and retry.
            # The retry will then get a 409 conflict.
            with pytest.raises(ResourceExistsError):
                self.ts.create_table(new_table_name, raw_response_hook=callback)
        finally:
            self.ts.delete_table(new_table_name)
            self._tear_down()

    @tables_decorator
    @recorded_by_proxy
    def test_retry_on_timeout(self, tables_storage_account_name, tables_primary_storage_account_key):
        self._set_up(
            tables_storage_account_name,
            tables_primary_storage_account_key,
            default_table=False,
            retry_mode=RetryMode.Exponential,
            retry_backoff_factor=1,
        )

        callback = ResponseCallback(status=200, new_status=408).override_first_status
        try:
            # The initial get will return 200, but we overwrite it with 408 and retry.
            # The retry will then succeed.
            self.ts.get_service_properties(raw_response_hook=callback)
        finally:
            self._tear_down()

    @pytest.mark.live_test_only
    @tables_decorator
    def test_retry_on_socket_timeout(self, tables_storage_account_name, tables_primary_storage_account_key):
        retry_transport = RetryRequestTransport()
        self._set_up(
            tables_storage_account_name,
            tables_primary_storage_account_key,
            transport=retry_transport,
            default_table=False,
            retry_mode=RetryMode.Fixed,
            retry_backoff_factor=1,
        )

        with pytest.raises(AzureError) as error:
            self.ts.get_service_properties(connection_timeout=11, read_timeout=0.000000000001)

        # 3 retries + 1 original == 4
        assert retry_transport.count == 4
        # This call should succeed on the server side, but fail on the client side due to socket timeout
        assert "Read timed out" in str(error.value)

    @tables_decorator
    @recorded_by_proxy
    def test_no_retry(self, tables_storage_account_name, tables_primary_storage_account_key):
        self._set_up(
            tables_storage_account_name, tables_primary_storage_account_key, retry_total=0, default_table=False
        )

        new_table_name = self.get_resource_name("uttable")

        # Force the create call to 'timeout' with a 408
        callback = ResponseCallback(status=201, new_status=500).override_status

        try:
            with pytest.raises(HttpResponseError) as error:
                self.ts.create_table(new_table_name, raw_response_hook=callback)
            assert error.value.response.status_code == 500
            assert error.value.reason == "Created"

        finally:
            self.ts.delete_table(new_table_name)
            self._tear_down()

    @tables_decorator
    @recorded_by_proxy
    def test_failover_and_retry_on_secondary(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        entity = {"PartitionKey": "foo", "RowKey": "bar"}

        # secondary endpoint only works on READ operations: get, list, query.
        # retry request type in frozenset({'PUT', 'HEAD', 'TRACE', 'OPTIONS', 'DELETE', 'GET'})
        with TableClient(
            url,
            table_name,
            credential=tables_primary_storage_account_key,
            retry_total=5,
            retry_to_secondary=True,
            transport=FailoverRetryTransport(),
        ) as client:
            with pytest.raises(ServiceRequestError) as ex:
                client.create_table(failover=ServiceRequestError("Attempting to force failover"))  # POST, not retry
            assert "Attempting to force failover" in str(ex.value)

        # prepare a table
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
        if self.is_live:
            time.sleep(15)

        # test get_entity() without the entity
        with TableClient(
            url,
            table_name,
            credential=tables_primary_storage_account_key,
            retry_total=5,
            retry_to_secondary=True,
            transport=FailoverRetryTransport(),
        ) as client:
            # test passing three different error types(ServiceRequestError, ServiceResponseError, HttpResponseError) on get_entity()
            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=ServiceRequestError("Attempting to force failover"))
            assert "The specified resource does not exist." in str(ex.value)

            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=ServiceResponseError("Attempting to force failover"))
            assert "The specified resource does not exist." in str(ex.value)

            http_response_err = HttpResponseError("Attempting to force failover")
            http_response_err.status_code = 500  # 500 is in RETRY_CODES that will definitely retry on
            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=http_response_err)
            assert "The specified resource does not exist." in str(ex.value)

        # prepare an entity
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_entity(entity)
        if self.is_live:
            time.sleep(15)

        # test get_entity() when the entity is ready
        with TableClient(
            url,
            table_name,
            credential=tables_primary_storage_account_key,
            retry_total=5,
            retry_to_secondary=True,
            transport=FailoverRetryTransport(),
        ) as client:
            # test passing three different error types(ServiceRequestError, ServiceResponseError, HttpResponseError) on get_entity()
            client.get_entity(
                "foo", "bar", failover=ServiceRequestError("Attempting to force failover")
            )  # GET, succeed when retry
            client.get_entity(
                "foo", "bar", failover=ServiceResponseError("Attempting to force failover")
            )  # GET, succeed when retry
            http_response_err = HttpResponseError("Attempting to force failover")
            http_response_err.status_code = 500  # 500 is in RETRY_CODES that will definitely retry on
            client.get_entity("foo", "bar", failover=http_response_err)  # GET, succeed when retry

            with pytest.raises(ServiceRequestError) as ex:
                client.upsert_entity(
                    entity, failover=ServiceRequestError("Attempting to force failover")
                )  # PATCH, not retry
            assert "Attempting to force failover" in str(ex.value)

        with TableClient(
            url,
            table_name,
            credential=tables_primary_storage_account_key,
            retry_total=5,
            retry_to_secondary=True,
            transport=FailoverRetryTransport(),
        ) as client:
            entities = client.list_entities(
                failover=ServiceRequestError("Attempting to force failover")
            )  # GET, succeed when retry
            for e in entities:
                pass

        with TableClient(
            url,
            table_name,
            credential=tables_primary_storage_account_key,
            retry_total=5,
            retry_to_secondary=True,
            transport=FailoverRetryTransport(),
        ) as client:
            client.delete_entity(
                entity, failover=ServiceRequestError("Attempting to force failover")
            )  # DELETE, succeed when retry

            # clean up
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_failover_and_retry_on_primary(self, tables_storage_account_name, tables_primary_storage_account_key):
        url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        entity = {"PartitionKey": "foo", "RowKey": "bar"}

        # prepare a table
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
        if self.is_live:
            time.sleep(15)

        # test get_entity() without the entity
        with TableClient(
            url,
            table_name,
            credential=tables_primary_storage_account_key,
            retry_total=5,
            location_mode=LocationMode.SECONDARY,
            transport=FailoverRetryTransport(location_mode=LocationMode.SECONDARY),
        ) as client:
            # test passing three different error types(ServiceRequestError, ServiceResponseError, HttpResponseError) on get_entity()
            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=ServiceRequestError("Attempting to force failover"))
            assert "The specified resource does not exist." in str(ex.value)

            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=ServiceResponseError("Attempting to force failover"))
            assert "The specified resource does not exist." in str(ex.value)

            http_response_err = HttpResponseError("Attempting to force failover")
            http_response_err.status_code = 500  # 500 is in RETRY_CODES that will definitely retry on
            with pytest.raises(ResourceNotFoundError) as ex:
                client.get_entity("foo", "bar", failover=http_response_err)
            assert "The specified resource does not exist." in str(ex.value)

        # prepare an entity
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_entity(entity)
        if self.is_live:
            time.sleep(15)

        # test get_entity() when the entity is ready
        with TableClient(
            url,
            table_name,
            credential=tables_primary_storage_account_key,
            retry_total=5,
            location_mode=LocationMode.SECONDARY,
            transport=FailoverRetryTransport(location_mode=LocationMode.SECONDARY),
        ) as client:
            # test passing three different error types(ServiceRequestError, ServiceResponseError, HttpResponseError) on get_entity()
            client.get_entity(
                "foo", "bar", failover=ServiceRequestError("Attempting to force failover")
            )  # GET, retried on secondary endpoint
            client.get_entity(
                "foo", "bar", failover=ServiceResponseError("Attempting to force failover")
            )  # GET, succeed when retry
            http_response_err = HttpResponseError("Attempting to force failover")
            http_response_err.status_code = 500  # 500 is in RETRY_CODES that will definitely retry on
            client.get_entity("foo", "bar", failover=http_response_err)  # GET, succeed when retry

            entities = client.list_entities(
                failover=ServiceRequestError("Attempting to force failover")
            )  # GET, retried on secondary endpoint
            for e in entities:
                pass

        # clean up
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.delete_table()

    @tables_decorator
    @recorded_by_proxy
    def test_failover_and_retry_in_second_page_while_listing(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        url = self.account_url(tables_storage_account_name, "table")
        table_name = self.get_resource_name("mytable")
        entity1 = {"PartitionKey": "k1", "RowKey": "r1"}
        entity2 = {"PartitionKey": "k2", "RowKey": "r2"}

        # prepare entities so that can list in more than one page
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.create_table()
            client.create_entity(entity1)
            client.create_entity(entity2)

        with TableClient(
            url, table_name, credential=tables_primary_storage_account_key, transport=SecondpageFailoverRetryTransport()
        ) as client:
            entities = client.list_entities(
                results_per_page=1, failover=ServiceRequestError("Attempting to force failover")
            )
            next(entities)
            with pytest.raises(AssertionError):
                next(entities)

        # clean up
        with TableClient(url, table_name, credential=tables_primary_storage_account_key) as client:
            client.delete_table()


# ------------------------------------------------------------------------------
