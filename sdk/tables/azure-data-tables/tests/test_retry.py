# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, ResponseCallback

from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError,
    AzureError,
)
from azure.core.pipeline.policies import RetryMode
from azure.core.pipeline.transport import RequestsTransport
from azure.data.tables import TableServiceClient

from _shared.testcase import TableTestCase

from preparers import tables_decorator


class RetryRequestTransport(RequestsTransport):
    """Transport to test retry"""
    def __init__(self, *args, **kwargs):
        super(RetryRequestTransport, self).__init__(*args, **kwargs)
        self.count = 0

    def send(self, request, **kwargs):
        self.count += 1
        response = super(RetryRequestTransport, self).send(request, **kwargs)
        return response

# --Test Class -----------------------------------------------------------------
class TestStorageRetry(AzureRecordedTestCase, TableTestCase):
    def _set_up(self, tables_storage_account_name, tables_primary_storage_account_key, url='table', default_table=True, **kwargs):
        self.table_name = self.get_resource_name('uttable')
        self.ts = TableServiceClient(
            self.account_url(tables_storage_account_name, url),
            credential=tables_primary_storage_account_key,
            **kwargs
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
    def test_retry_on_server_error(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key, default_table=False)
        try:
            callback = ResponseCallback(status=201, new_status=500).override_status

            new_table_name = self.get_resource_name('uttable')
            # The initial create will return 201, but we overwrite it with 500 and retry.
            # The retry will then get a 409 conflict.
            with pytest.raises(ResourceExistsError):
                self.ts.create_table(new_table_name, raw_response_hook=callback)
        finally:
            self.ts.delete_table(new_table_name)
            self._tear_down()

    @tables_decorator
    @recorded_by_proxy
    def test_retry_on_timeout(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        self._set_up(
            tables_storage_account_name,
            tables_primary_storage_account_key,
            default_table=False,
            retry_mode=RetryMode.Exponential,
            retry_backoff_factor=1
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
        retry_transport = RetryRequestTransport(connection_timeout=11, read_timeout=0.000000000001)
        self._set_up(
            tables_storage_account_name,
            tables_primary_storage_account_key,
            transport=retry_transport,
            default_table=False,
            retry_mode=RetryMode.Fixed,
            retry_backoff_factor=1)

        with pytest.raises(AzureError) as error:
            self.ts.get_service_properties()

        # 3 retries + 1 original == 4
        assert retry_transport.count == 4
        # This call should succeed on the server side, but fail on the client side due to socket timeout
        assert 'read timeout' in str(error.value), 'Expected socket timeout but got different exception.'

    @tables_decorator
    @recorded_by_proxy
    def test_no_retry(self, **kwargs):
        tables_storage_account_name = kwargs.pop("tables_storage_account_name")
        tables_primary_storage_account_key = kwargs.pop("tables_primary_storage_account_key")
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key, retry_total=0, default_table=False)

        new_table_name = self.get_resource_name('uttable')

        # Force the create call to 'timeout' with a 408
        callback = ResponseCallback(status=201, new_status=500).override_status

        try:
            with pytest.raises(HttpResponseError) as error:
                self.ts.create_table(new_table_name, raw_response_hook=callback)
            assert error.value.response.status_code == 500
            assert error.value.reason == 'Created'

        finally:
            self.ts.delete_table(new_table_name)
            self._tear_down()
# ------------------------------------------------------------------------------
