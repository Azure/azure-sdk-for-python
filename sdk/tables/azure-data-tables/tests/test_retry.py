# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest

from devtools_testutils import AzureTestCase


from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError,
    AzureError,
    ClientAuthenticationError
)
from azure.core.pipeline.transport import(
    RequestsTransport
)

from azure.data.tables import (
    TableServiceClient,
    LocationMode,
    LinearRetry,
    ExponentialRetry,
)

from _shared.testcase import (
    TableTestCase,
    ResponseCallback,
    RetryCounter
)

from preparers import TablesPreparer


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
class StorageRetryTest(AzureTestCase, TableTestCase):

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
    @TablesPreparer()
    def test_retry_on_server_error(self, tables_storage_account_name, tables_primary_storage_account_key):
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


    @TablesPreparer()
    def test_retry_on_timeout(self, tables_storage_account_name, tables_primary_storage_account_key):
        retry = ExponentialRetry(initial_backoff=1, increment_base=2)
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key, retry_policy=retry, default_table=False)

        new_table_name = self.get_resource_name('uttable')
        callback = ResponseCallback(status=201, new_status=408).override_status

        try:
            # The initial create will return 201, but we overwrite it with 408 and retry.
            # The retry will then get a 409 conflict.
            with pytest.raises(ResourceExistsError):
                self.ts.create_table(new_table_name, raw_response_hook=callback)
        finally:
            self.ts.delete_table(new_table_name)
            self._tear_down()


    @TablesPreparer()
    def test_retry_callback_and_retry_context(self, tables_storage_account_name, tables_primary_storage_account_key):
        retry = LinearRetry(backoff=1)
        self._set_up(tables_storage_account_name, tables_primary_storage_account_key, retry_policy=retry, default_table=False)

        new_table_name = self.get_resource_name('uttable')
        callback = ResponseCallback(status=201, new_status=408).override_status

        def assert_exception_is_present_on_retry_context(**kwargs):
            self.assertIsNotNone(kwargs.get('response'))
            self.assertEqual(kwargs['response'].status_code, 408)
        try:
            # The initial create will return 201, but we overwrite it with 408 and retry.
            # The retry will then get a 409 conflict.
            with pytest.raises(ResourceExistsError):
                self.ts.create_table(new_table_name, raw_response_hook=callback, retry_hook=assert_exception_is_present_on_retry_context)
        finally:
            self.ts.delete_table(new_table_name)
            self._tear_down()

    @pytest.mark.live_test_only
    @TablesPreparer()
    def test_retry_on_socket_timeout(self, tables_storage_account_name, tables_primary_storage_account_key):
        retry = LinearRetry(backoff=1)
        retry_transport = RetryRequestTransport(connection_timeout=11, read_timeout=0.000000000001)
        self._set_up(
            tables_storage_account_name,
            tables_primary_storage_account_key,
            retry_policy=retry,
            transport=retry_transport,
            default_table=False)
    
        new_table_name = self.get_resource_name('uttable')
        try:
            with pytest.raises(AzureError) as error:
                self.ts.create_table(new_table_name)

            # 3 retries + 1 original == 4
            assert retry_transport.count == 4
            # This call should succeed on the server side, but fail on the client side due to socket timeout
            self.assertTrue('read timeout' in str(error.value), 'Expected socket timeout but got different exception.')

        finally:
            # we must make the timeout normal again to let the delete operation succeed
            self.ts.delete_table(new_table_name, connection_timeout=(11, 11))
            self._tear_down(connection_timeout=(11, 11))


    # Waiting on fix to client pipeline
    # @TablesPreparer()
    # def test_no_retry(self, tables_storage_account_name, tables_primary_storage_account_key):
    #     self._set_up(tables_storage_account_name, tables_primary_storage_account_key, retry_total=0, default_table=False)

    #     new_table_name = self.get_resource_name('uttable')

    #     # Force the create call to 'timeout' with a 408
    #     callback = ResponseCallback(status=201, new_status=408).override_status

    #     try:
    #         with pytest.raises(HttpResponseError) as error:
    #             self.ts.create_table(new_table_name, raw_response_hook=callback)
    #         self.assertEqual(error.value.response.status_code, 408)
    #         self.assertEqual(error.value.reason, 'Created')

    #     finally:
    #         self.ts.delete_table(new_table_name)
    #         self._tear_down()
# ------------------------------------------------------------------------------

