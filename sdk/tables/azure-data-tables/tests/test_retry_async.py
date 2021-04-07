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
    AioHttpTransport
)

from azure.data.tables.aio import TableServiceClient
from azure.data.tables.aio._policies_async import LinearRetry, ExponentialRetry
from azure.data.tables import LocationMode

from _shared.asynctestcase import AsyncTableTestCase
from _shared.testcase import (
    ResponseCallback,
    RetryCounter
)

from preparers import TablesPreparer


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
class StorageRetryTest(AzureTestCase, AsyncTableTestCase):

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

    async def _tear_down(self, **kwargs):
        if self.is_live:
            try:
                await self.ts.delete_table(self.table_name, **kwargs)
            except:
                pass

            try:
                for table_name in self.query_tables:
                    try:
                        await self.ts.delete_table(table_name, **kwargs)
                    except:
                        pass
            except AttributeError:
                pass

    # --Test Cases --------------------------------------------
    @TablesPreparer()
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


    @TablesPreparer()
    async def test_retry_on_timeout_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        retry = ExponentialRetry(initial_backoff=1, increment_base=2)
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key, retry_policy=retry, default_table=False)

        new_table_name = self.get_resource_name('uttable')
        callback = ResponseCallback(status=201, new_status=408).override_status

        try:
            # The initial create will return 201, but we overwrite it with 408 and retry.
            # The retry will then get a 409 conflict.
            with pytest.raises(ResourceExistsError):
                await self.ts.create_table(new_table_name, raw_response_hook=callback)
        finally:
            await self.ts.delete_table(new_table_name)
            await self._tear_down()


    @TablesPreparer()
    async def test_retry_callback_and_retry_context_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        retry = LinearRetry(backoff=1)
        await self._set_up(tables_storage_account_name, tables_primary_storage_account_key, retry_policy=retry, default_table=False)

        new_table_name = self.get_resource_name('uttable')
        callback = ResponseCallback(status=201, new_status=408).override_status

        def assert_exception_is_present_on_retry_context(**kwargs):
            self.assertIsNotNone(kwargs.get('response'))
            self.assertEqual(kwargs['response'].status_code, 408)
        try:
            # The initial create will return 201, but we overwrite it with 408 and retry.
            # The retry will then get a 409 conflict.
            with pytest.raises(ResourceExistsError):
                await self.ts.create_table(new_table_name, raw_response_hook=callback, retry_hook=assert_exception_is_present_on_retry_context)
        finally:
            await self.ts.delete_table(new_table_name)
            await self._tear_down()

    @pytest.mark.live_test_only
    @TablesPreparer()
    async def test_retry_on_socket_timeout_async(self, tables_storage_account_name, tables_primary_storage_account_key):
        retry = LinearRetry(backoff=1)
        retry_transport = RetryAioHttpTransport(connection_timeout=11, read_timeout=0.000000000001)
        await self._set_up(
            tables_storage_account_name,
            tables_primary_storage_account_key,
            retry_policy=retry,
            transport=retry_transport,
            default_table=False)
    
        new_table_name = self.get_resource_name('uttable')
        try:
            with pytest.raises(AzureError) as error:
                await self.ts.create_table(new_table_name)

            # 3 retries + 1 original == 4
            assert retry_transport.count == 4
            # This call should succeed on the server side, but fail on the client side due to socket timeout
            self.assertTrue('Timeout on reading' in str(error.value), 'Expected socket timeout but got different exception.')

        finally:
            # TODO: Why can I not just reset the connection timeout???
            await self._set_up(tables_storage_account_name, tables_primary_storage_account_key, default_table=False)
            # we must make the timeout normal again to let the delete operation succeed
            await self.ts.delete_table(new_table_name)
            await self._tear_down()


    # Waiting on fix to client pipeline
    # @TablesPreparer()
    # async def test_no_retry_async(self, tables_storage_account_name, tables_primary_storage_account_key):
    #     await self._set_up(tables_storage_account_name, tables_primary_storage_account_key, retry_total=0, default_table=False)

    #     new_table_name = self.get_resource_name('uttable')

    #     # Force the create call to 'timeout' with a 408
    #     callback = ResponseCallback(status=201, new_status=408).override_status

    #     try:
    #         with with pytest.raises(HttpResponseError) as error:
    #             await self.ts.create_table(new_table_name, raw_response_hook=callback)
    #         self.assertEqual(error.value.response.status_code, 408)
    #         self.assertEqual(error.value.reason, 'Created')

    #     finally:
    #         await self.ts.delete_table(new_table_name)
    #         await self._tear_down()
# ------------------------------------------------------------------------------

