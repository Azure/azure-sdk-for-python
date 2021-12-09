# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils import AzureRecordedTestCase, ResponseCallback
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError,
    AzureError,
)
from azure.core.pipeline.policies import RetryMode
from azure.core.pipeline.transport import(
    AioHttpTransport
)

from azure.data.tables.aio import TableServiceClient

from _shared.asynctestcase import AsyncTableTestCase

from async_preparers import tables_decorator_async


class RetryAioHttpTransport(AioHttpTransport):
    """Transport to test retry"""
    def __init__(self, *args, **kwargs):
        super(RetryAioHttpTransport, self).__init__(*args, **kwargs)
        self.count = 0

    async def send(self, request, **kwargs):
        self.count += 1
        response = await super(RetryAioHttpTransport, self).send(request, **kwargs)
        return response


# --Test Class -----------------------------------------------------------------
class TestStorageRetryAsync(AzureRecordedTestCase, AsyncTableTestCase):

    async def _set_up(self, tables_storage_account_name, tables_primary_storage_account_key, url='table', default_table=True, **kwargs):
        self.table_name = self.get_resource_name('uttable')
        self.ts = TableServiceClient(
            self.account_url(tables_storage_account_name, url),
            credential=tables_primary_storage_account_key,
            **kwargs
        )
        self.table = self.ts.get_table_client(self.table_name)
        if self.is_live and default_table:
            try:
                await self.ts.create_table(self.table_name)
            except ResourceExistsError:
                pass

        self.query_tables = []

    # --Test Cases --------------------------------------------
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_retry_on_server_error_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key, default_table=False)
        try:
            callback = ResponseCallback(status=201, new_status=500).override_status

            new_table_name = self.get_resource_name('uttable')
            # The initial create will return 201, but we overwrite it with 500 and retry.
            # The retry will then get a 409 conflict.
            with pytest.raises(ResourceExistsError):
                await self.ts.create_table(new_table_name, raw_response_hook=callback)
        finally:
            await self.ts.delete_table(new_table_name)
            await self._tear_down()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_retry_on_timeout_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        await self._set_up(
            tables_storage_account_name,
            tables_primary_storage_account_key,
            default_table=False,
            retry_mode=RetryMode.Exponential,
            retry_backoff_factor=1)

        callback = ResponseCallback(status=200, new_status=408).override_first_status

        try:
            # The initial create will return 201, but we overwrite it with 408 and retry.
            # The retry will then succeed.
            await self.ts.get_service_properties(raw_response_hook=callback)
        finally:
            await self._tear_down()

    @pytest.mark.live_test_only
    @tables_decorator_async
    async def test_retry_on_socket_timeout_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        retry_transport = RetryAioHttpTransport(connection_timeout=11, read_timeout=0.000000000001)
        await self._set_up(
            tables_storage_account_name,
            tables_primary_storage_account_key,
            retry_mode=RetryMode.Fixed,
            retry_backoff_factor=1,
            transport=retry_transport,
            default_table=False)

        with pytest.raises(AzureError) as error:
            await self.ts.get_service_properties()

        # 3 retries + 1 original == 4
        assert retry_transport.count == 4
        # This call should succeed on the server side, but fail on the client side due to socket timeout
        assert 'Timeout on reading' in str(error.value), 'Expected socket timeout but got different exception.'

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_no_retry_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key, retry_total=0, default_table=False)

        new_table_name = self.get_resource_name('uttable')

        # Force the create call to error with a 500
        callback = ResponseCallback(status=201, new_status=500).override_status

        try:
            with pytest.raises(HttpResponseError) as error:
                await self.ts.create_table(new_table_name, raw_response_hook=callback)
            assert error.value.response.status_code == 500
            assert error.value.reason == 'Created'

        finally:
            await self.ts.delete_table(new_table_name)
            await self._tear_down()
# ------------------------------------------------------------------------------
