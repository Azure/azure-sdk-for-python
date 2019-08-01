# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
import asyncio

from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError,
    ServiceResponseError,
    ClientAuthenticationError
)

from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
    LocationMode,
    LinearRetry,
    ExponentialRetry,
    NoRetry
)

from testcase import (
    StorageTestCase,
    record,
    TestMode,
    ResponseCallback,
    RetryCounter,
)


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


# --Test Class -----------------------------------------------------------------
class StorageRetryTestAsync(StorageTestCase):
    def setUp(self):
        super(StorageRetryTestAsync, self).setUp()

    def tearDown(self):
        return super(StorageRetryTestAsync, self).tearDown()

    # --Test Cases --------------------------------------------

    async def _test_retry_on_server_error_async(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlobServiceClient, self.settings, transport=AiohttpTestTransport())

        # Force the create call to 'timeout' with a 408
        callback = ResponseCallback(status=201, new_status=500).override_status

        # Act
        try:
            # The initial create will return 201, but we overwrite it and retry.
            # The retry will then get a 409 and return false.
            with self.assertRaises(ResourceExistsError):
                await service.create_container(container_name, raw_response_hook=callback)
        finally:
            await service.delete_container(container_name)

        # Assert

    @record
    def test_retry_on_server_error_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_retry_on_server_error_async())

    async def _test_retry_on_timeout_async(self):
        # Arrange
        container_name = self.get_resource_name()
        retry = ExponentialRetry(initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())

        callback = ResponseCallback(status=201, new_status=408).override_status

        # Act
        try:
            # The initial create will return 201, but we overwrite it and retry.
            # The retry will then get a 409 and return false.
            with self.assertRaises(ResourceExistsError):
                await service.create_container(container_name, raw_response_hook=callback)
        finally:
            await service.delete_container(container_name)

        # Assert

    @record
    def test_retry_on_timeout_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_retry_on_timeout_async())

    async def _test_retry_callback_and_retry_context_async(self):
        # Arrange
        container_name = self.get_resource_name()
        retry = LinearRetry(backoff=1)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())

        # Force the create call to 'timeout' with a 408
        callback = ResponseCallback(status=201, new_status=408).override_status

        def assert_exception_is_present_on_retry_context(**kwargs):
            self.assertIsNotNone(kwargs.get('response'))
            self.assertEqual(kwargs['response'].status_code, 408)


        # Act
        try:
            # The initial create will return 201, but we overwrite it and retry.
            # The retry will then get a 409 and return false.
            with self.assertRaises(ResourceExistsError):
                await service.create_container(
                    container_name, raw_response_hook=callback,
                    retry_hook=assert_exception_is_present_on_retry_context)
        finally:
            await service.delete_container(container_name)

    @record
    def test_retry_callback_and_retry_context_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_retry_callback_and_retry_context_async())

    async def _test_retry_on_socket_timeout_async(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        # Arrange
        container_name = self.get_resource_name()
        retry = LinearRetry(backoff=1)

        # make the connect timeout reasonable, but packet timeout truly small, to make sure the request always times out
        socket_timeout = 0.000000000001
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, connection_timeout=socket_timeout, transport=AiohttpTestTransport())

        assert service._client._client._pipeline._transport.connection_config.timeout == socket_timeout

        # Act
        try:
            with self.assertRaises(ServiceResponseError) as error:
                await service.create_container(container_name)
            # Assert
            # This call should succeed on the server side, but fail on the client side due to socket timeout
            self.assertTrue('read timeout' in str(error.exception), 'Expected socket timeout but got different exception.')

        finally:
            # we must make the timeout normal again to let the delete operation succeed
            try:
                await service.delete_container(container_name, connection_timeout=11)
            except:
                pass

    def test_retry_on_socket_timeout_async(self):
        pytest.skip("Error not raised on retry")
        if TestMode.need_recording_file(self.test_mode):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_retry_on_socket_timeout_async())

    async def _test_no_retry_async(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=NoRetry(), transport=AiohttpTestTransport())


        # Force the create call to 'timeout' with a 408
        callback = ResponseCallback(status=201, new_status=408).override_status

        # Act
        try:
            with self.assertRaises(HttpResponseError) as error:
                await service.create_container(container_name, raw_response_hook=callback)
            self.assertEqual(error.exception.response.status_code, 408)
            self.assertEqual(error.exception.reason, 'Created')

        finally:
            await service.delete_container(container_name)

    @record
    def test_no_retry_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_no_retry_async())

    async def _test_linear_retry_async(self):
        # Arrange
        container_name = self.get_resource_name()
        retry = LinearRetry(backoff=1)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())

        # Force the create call to 'timeout' with a 408
        callback = ResponseCallback(status=201, new_status=408).override_status

        # Act
        try:
            # The initial create will return 201, but we overwrite it and retry.
            # The retry will then get a 409 and return false.
            with self.assertRaises(ResourceExistsError):
                await service.create_container(container_name, raw_response_hook=callback)
        finally:
            await service.delete_container(container_name)

        # Assert

    @record
    def test_linear_retry_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_linear_retry_async())

    async def _test_exponential_retry_async(self):
        # Arrange
        container_name = self.get_resource_name()
        retry = ExponentialRetry(initial_backoff=1, increment_base=3, retry_total=3)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())

        try:
            container = await service.create_container(container_name)

            # Force the create call to 'timeout' with a 408
            callback = ResponseCallback(status=200, new_status=408)

            # Act
            with self.assertRaises(HttpResponseError):
                await container.get_container_properties(raw_response_hook=callback.override_status)

            # Assert the response was called the right number of times (1 initial request + 3 retries)
            self.assertEqual(callback.count, 1+3)
        finally:
            # Clean up
            await service.delete_container(container_name)

    @record
    def test_exponential_retry_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_exponential_retry_async())

    @record
    def test_exponential_retry_interval_async(self):
        # Arrange
        retry_policy = ExponentialRetry(initial_backoff=1, increment_base=3, random_jitter_range=3)
        context_stub = {}

        for i in range(10):
            # Act
            context_stub['count'] = 0
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 1
            self.assertTrue(0 <= backoff <= 4)

            # Act
            context_stub['count'] = 1
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 4(1+3^1)
            self.assertTrue(1 <= backoff <= 7)

            # Act
            context_stub['count'] = 2
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 10(1+3^2)
            self.assertTrue(7 <= backoff <= 13)

            # Act
            context_stub['count'] = 3
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 28(1+3^3)
            self.assertTrue(25 <= backoff <= 31)

    @record
    def test_linear_retry_interval_async(self):
        # Arrange
        context_stub = {}

        for i in range(10):
            # Act
            retry_policy = LinearRetry(backoff=1, random_jitter_range=3)
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 1
            self.assertTrue(0 <= backoff <= 4)

            # Act
            retry_policy = LinearRetry(backoff=5, random_jitter_range=3)
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 5
            self.assertTrue(2 <= backoff <= 8)

            # Act
            retry_policy = LinearRetry(backoff=15, random_jitter_range=3)
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 15
            self.assertTrue(12 <= backoff <= 18)

    async def _test_invalid_retry_async(self):
        # Arrange
        container_name = self.get_resource_name()
        retry = ExponentialRetry(initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())

        # Force the create call to fail by pretending it's a teapot
        callback = ResponseCallback(status=201, new_status=418).override_status

        # Act
        try:
            with self.assertRaises(HttpResponseError) as error:
                await service.create_container(container_name, raw_response_hook=callback)
            self.assertEqual(error.exception.response.status_code, 418)
            self.assertEqual(error.exception.reason, 'Created')
        finally:
            await service.delete_container(container_name)

    @record
    def test_invalid_retry_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_invalid_retry_async())

    async def _test_retry_with_deserialization_async(self):
        # Arrange
        container_name = self.get_resource_name(prefix='retry')
        retry = ExponentialRetry(initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())

        try:
            created = await service.create_container(container_name)

            # Act
            callback = ResponseCallback(status=200, new_status=408).override_first_status
            containers = service.list_containers(name_starts_with='retry', raw_response_hook=callback)

            # Assert
            listed = []
            async for c in containers:
                listed.append(c)
            self.assertTrue(len(listed) >= 1)
        finally:
            await service.delete_container(container_name)

    @record
    def test_retry_with_deserialization_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_retry_with_deserialization_async())

    async def _test_secondary_location_mode_async(self):
        # Arrange
        container_name = self.get_resource_name()
        retry = ExponentialRetry(initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())

        # Act
        try:
            container = await service.create_container(container_name)
            container.location_mode = LocationMode.SECONDARY

            # Override the response from secondary if it's 404 as that simply means
            # the container hasn't replicated. We're just testing we try secondary,
            # so that's fine.
            response_callback = ResponseCallback(status=404, new_status=200).override_first_status

            # Assert
            def request_callback(request):
                self.assertNotEqual(-1, request.http_request.url.find('-secondary'))

            request_callback = request_callback
            await container.get_container_properties(
                raw_request_hook=request_callback, raw_response_hook=response_callback)
        finally:
            # Delete will go to primary, so disable the request validation
            await service.delete_container(container_name)

    @record
    def test_secondary_location_mode_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_secondary_location_mode_async())

    async def _test_retry_to_secondary_with_put_async(self):
        # Arrange
        container_name = self.get_resource_name()
        retry = ExponentialRetry(retry_to_secondary=True, initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())

        # Act
        try:
            # Fail the first create attempt
            response_callback = ResponseCallback(status=201, new_status=408).override_first_status

            # Assert
            # Confirm that the create request does *not* get retried to secondary
            # This should actually throw InvalidPermissions if sent to secondary,
            # but validate the location_mode anyways.
            def retry_callback(location_mode=None, **kwargs):
                self.assertEqual(LocationMode.PRIMARY, location_mode)

            with self.assertRaises(ResourceExistsError):
                await service.create_container(
                    container_name, raw_response_hook=response_callback, retry_hook=retry_callback)

        finally:
            await service.delete_container(container_name)

    @record
    def test_retry_to_secondary_with_put_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_retry_to_secondary_with_put_async())

    async def _test_retry_to_secondary_with_get_async(self):
        # Arrange
        container_name = self.get_resource_name()
        retry = ExponentialRetry(retry_to_secondary=True, initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())

        # Act
        try:
            container = await service.create_container(container_name)
            response_callback = ResponseCallback(status=200, new_status=408).override_first_status

            # Assert
            # Confirm that the get request gets retried to secondary
            def retry_callback(retry_count=None, location_mode=None, **kwargs):
                # Only check this every other time, sometimes the secondary location fails due to delay
                if retry_count % 2 == 0:
                    self.assertEqual(LocationMode.SECONDARY, location_mode)

            await container.get_container_properties(
                raw_response_hook=response_callback, retry_hook=retry_callback)
        finally:
            await service.delete_container(container_name)

    @record
    def test_retry_to_secondary_with_get_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_retry_to_secondary_with_get_async())

    async def _test_location_lock_async(self):
        # Arrange
        retry = ExponentialRetry(retry_to_secondary=True, initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())

        # Act
        # Fail the first request and set the retry policy to retry to secondary
        response_callback = ResponseCallback(status=200, new_status=408).override_first_status
        #context = _OperationContext(location_lock=True)

        # Assert
        # Confirm that the first request gets retried to secondary
        # The given test account must be GRS
        def retry_callback(retry_count=None, location_mode=None, **kwargs):
            self.assertEqual(LocationMode.SECONDARY, location_mode)

        # Confirm that the second list request done with the same context sticks
        # to the final location of the first list request (aka secondary) despite
        # the client normally trying primary first
        requests = []
        def request_callback(request):
            if not requests:
                requests.append(request)
            else:
                self.assertNotEqual(-1, request.http_request.url.find('-secondary'))

        containers = service.list_containers(
            results_per_page=1, retry_hook=retry_callback)
        await containers.__anext__()
        await containers.__anext__()

    @record
    def test_location_lock_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_location_lock_async())

    async def _test_invalid_account_key_async(self):
        # Arrange
        container_name = self.get_resource_name()
        retry = ExponentialRetry(initial_backoff=1, increment_base=3, retry_total=3)
        service = self._create_storage_service(
            BlobServiceClient, self.settings, retry_policy=retry, transport=AiohttpTestTransport())
        service.credential.account_name = "dummy_account_name"
        service.credential.account_key = "dummy_account_key"

        # Shorten retries and add counter
        retry_counter = RetryCounter()
        retry_callback = retry_counter.simple_count

        # Act
        with self.assertRaises(ClientAuthenticationError):
            await service.create_container(container_name, retry_callback=retry_callback)

        # Assert
        # No retry should be performed since the signing error is fatal
        self.assertEqual(retry_counter.count, 0)

    @record
    def test_invalid_account_key_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_invalid_account_key_async())

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
