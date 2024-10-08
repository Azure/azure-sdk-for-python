# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
import pytest
from unittest import mock

from aiohttp.client_exceptions import ServerTimeoutError
from aiohttp.streams import StreamReader
from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    IncompleteReadError,
    HttpResponseError,
    ResourceExistsError,
    ServiceResponseError
)
from azure.core.pipeline.transport import AioHttpTransport
from azure.storage.blob import LocationMode
from azure.storage.blob._shared.authentication import AzureSigningError
from azure.storage.blob._shared.policies_async import ExponentialRetry, LinearRetry
from azure.storage.blob.aio import BlobClient, BlobServiceClient

from devtools_testutils import ResponseCallback, RetryCounter
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer


class TimeoutAioHttpTransport(AioHttpTransport):
    """Transport to test read timeout"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = 0

    async def send(self, request, **config):
        self.count += 1
        timeout_error = ServerTimeoutError("Timeout on reading data from socket")
        raise ServiceResponseError(timeout_error, error=timeout_error) from timeout_error


# --Test Class -----------------------------------------------------------------
class TestStorageRetryAsync(AsyncStorageRecordedTestCase):

    def _create_storage_service(self, service_class, account, key, connection_string=None, **kwargs):
        if connection_string:
            service = service_class.from_connection_string(connection_string, **kwargs)
        else:
            service = service_class(self.account_url(account, "blob"), credential=key, **kwargs)
        return service

    # --Test Cases --------------------------------------------
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_retry_on_server_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        container_name = self.get_resource_name('utcontainer')
        service = self._create_storage_service(BlobServiceClient, storage_account_name, storage_account_key)

        # Force the create call to 'timeout' with a 408
        callback = ResponseCallback(status=201, new_status=500).override_status

        # Act
        try:
            # The initial create will return 201, but we overwrite it and retry.
            # The retry will then get a 409 and return false.
            with pytest.raises(ResourceExistsError):
                await service.create_container(container_name, raw_response_hook=callback)
        finally:
            await service.delete_container(container_name)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_retry_on_timeout(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        container_name = self.get_resource_name('utcontainer')
        retry = ExponentialRetry(initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, storage_account_name, storage_account_key, retry_policy=retry)

        callback = ResponseCallback(status=201, new_status=408).override_status

        # Act
        try:
            # The initial create will return 201, but we overwrite it and retry.
            # The retry will then get a 409 and return false.
            with pytest.raises(ResourceExistsError):
                await service.create_container(container_name, raw_response_hook=callback)
        finally:
            await service.delete_container(container_name)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_retry_callback_and_retry_context(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        container_name = self.get_resource_name('utcontainer')
        retry = LinearRetry(backoff=1)
        service = self._create_storage_service(
            BlobServiceClient, storage_account_name, storage_account_key, retry_policy=retry)

        # Force the create call to 'timeout' with a 408
        callback = ResponseCallback(status=201, new_status=408).override_status

        def assert_exception_is_present_on_retry_context(**kwargs):
            assert kwargs.get('response') is not None
            assert kwargs['response'].status_code == 408

        # Act
        try:
            # The initial create will return 201, but we overwrite it and retry.
            # The retry will then get a 409 and return false.
            with pytest.raises(ResourceExistsError):
                await service.create_container(
                    container_name, raw_response_hook=callback,
                    retry_hook=assert_exception_is_present_on_retry_context)
        finally:
            await service.delete_container(container_name)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_retry_on_socket_timeout(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        container_name = self.get_resource_name('utcontainer')
        blob_name = self.get_resource_name('blob')
        # Upload a blob that can be downloaded to test read timeout
        service = self._create_storage_service(BlobServiceClient, storage_account_name, storage_account_key)
        container = await service.create_container(container_name)
        await container.upload_blob(blob_name, b'Hello World', overwrite=True)

        retry = LinearRetry(backoff=1, random_jitter_range=1)
        timeout_transport = TimeoutAioHttpTransport()
        timeout_service = self._create_storage_service(
            BlobServiceClient,
            storage_account_name,
            storage_account_key,
            retry_policy=retry,
            transport=timeout_transport)
        blob = timeout_service.get_blob_client(container_name, blob_name)

        # Act
        try:
            with pytest.raises(AzureError):
                await blob.download_blob()
            # Assert
            # 3 retries + 1 original == 4
            assert timeout_transport.count == 4

        finally:
            # Recreate client with normal timeouts
            service = self._create_storage_service(BlobServiceClient, storage_account_name, storage_account_key)
            service.delete_container(container_name)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_no_retry(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        container_name = self.get_resource_name('utcontainer')
        service = self._create_storage_service(
            BlobServiceClient, storage_account_name, storage_account_key, retry_total=0)


        # Force the create call to 'timeout' with a 408
        callback = ResponseCallback(status=201, new_status=408).override_status

        # Act
        try:
            with pytest.raises(HttpResponseError) as error:
                await service.create_container(container_name, raw_response_hook=callback)
            assert error.value.status_code == 408
            assert error.value.reason == 'Created'

        finally:
            await service.delete_container(container_name)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_linear_retry(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        container_name = self.get_resource_name('utcontainer')
        retry = LinearRetry(backoff=1)
        service = self._create_storage_service(
            BlobServiceClient, storage_account_name, storage_account_key, retry_policy=retry)

        # Force the create call to 'timeout' with a 408
        callback = ResponseCallback(status=201, new_status=408).override_status

        # Act
        try:
            # The initial create will return 201, but we overwrite it and retry.
            # The retry will then get a 409 and return false.
            with pytest.raises(ResourceExistsError):
                await service.create_container(container_name, raw_response_hook=callback)
        finally:
            await service.delete_container(container_name)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_exponential_retry(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        container_name = self.get_resource_name('utcontainer')
        retry = ExponentialRetry(initial_backoff=1, increment_base=3, retry_total=3)
        service = self._create_storage_service(
            BlobServiceClient, storage_account_name, storage_account_key, retry_policy=retry)

        try:
            container = await service.create_container(container_name)

            # Force the create call to 'timeout' with a 408
            callback = ResponseCallback(status=200, new_status=408)

            # Act
            with pytest.raises(HttpResponseError):
                await container.get_container_properties(raw_response_hook=callback.override_status)

            # Assert the response was called the right number of times (1 initial request + 3 retries)
            assert callback.count == 1+3
        finally:
            # Clean up
            await service.delete_container(container_name)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_exponential_retry_interval(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        retry_policy = ExponentialRetry(initial_backoff=1, increment_base=3, random_jitter_range=3)
        context_stub = {}

        for i in range(10):
            # Act
            context_stub['count'] = 0
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 1
            assert 0 <= backoff <= 4

            # Act
            context_stub['count'] = 1
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 4(1+3^1)
            assert 1 <= backoff <= 7

            # Act
            context_stub['count'] = 2
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 10(1+3^2)
            assert 7 <= backoff <= 13

            # Act
            context_stub['count'] = 3
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 28(1+3^3)
            assert 25 <= backoff <= 31

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_linear_retry_interval(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        context_stub = {}

        for i in range(10):
            # Act
            retry_policy = LinearRetry(backoff=1, random_jitter_range=3)
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 1
            assert 0 <= backoff <= 4

            # Act
            retry_policy = LinearRetry(backoff=5, random_jitter_range=3)
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 5
            assert 2 <= backoff <= 8

            # Act
            retry_policy = LinearRetry(backoff=15, random_jitter_range=3)
            backoff = retry_policy.get_backoff_time(context_stub)

            # Assert backoff interval is within +/- 3 of 15
            assert 12 <= backoff <= 18

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_invalid_retry(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        container_name = self.get_resource_name('utcontainer')
        retry = ExponentialRetry(initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, storage_account_name, storage_account_key, retry_policy=retry)

        # Force the create call to fail by pretending it's a teapot
        callback = ResponseCallback(status=201, new_status=418).override_status

        # Act
        try:
            with pytest.raises(HttpResponseError) as error:
                await service.create_container(container_name, raw_response_hook=callback)
            assert error.value.status_code == 418
            assert error.value.reason == 'Created'
        finally:
            await service.delete_container(container_name)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_retry_with_deserialization(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        container_name = self.get_resource_name('retry')
        retry = ExponentialRetry(initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, storage_account_name, storage_account_key, retry_policy=retry)

        try:
            created = await service.create_container(container_name)

            # Act
            callback = ResponseCallback(status=200, new_status=408).override_first_status
            containers = service.list_containers(name_starts_with='retry', raw_response_hook=callback)

            # Assert
            listed = []
            async for c in containers:
                listed.append(c)
            assert len(listed) >= 1
        finally:
            await service.delete_container(container_name)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_retry_secondary(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        """Secondary location test.

        This test is special, since in practical term, we don't have time to wait
        for the georeplication to be done (can take a loooooong time).
        So for the purpose of this test, we fake a 408 on the primary request,
        and then we check we do a 408. AND DONE.
        It's not really perfect, since we didn't tested it would work on
        a real geo-location.

        Might be changed to live only as loooooong test with a polling on
        the current geo-replication status.
        """
        # Arrange
        # Fail the first request and set the retry policy to retry to secondary
        # The given test account must be GRS
        class MockTransport(AioHttpTransport):
            CALL_NUMBER = 1
            ENABLE = False
            async def send(self, request, **kwargs):
                if MockTransport.ENABLE:
                    if MockTransport.CALL_NUMBER == 2:
                        if request.method != 'PUT':
                            assert '-secondary' in request.url
                        # Here's our hack
                        # Replace with primary so the test works even
                        # if secondary is not ready
                        request.url = request.url.replace('-secondary', '')

                response = await super(MockTransport, self).send(request, **kwargs)

                if MockTransport.ENABLE:
                    assert response.status_code in [200, 201, 409]
                    if MockTransport.CALL_NUMBER == 1:
                        response.status_code = 408
                    elif MockTransport.CALL_NUMBER == 2:
                        if response.status_code == 409:  # We can't really retry on PUT
                            response.status_code = 201
                    else:
                        pytest.fail("This test is not supposed to do more calls")
                    MockTransport.CALL_NUMBER += 1
                return response

        retry = ExponentialRetry(retry_to_secondary=True, initial_backoff=1, increment_base=2)
        service = self._create_storage_service(
            BlobServiceClient, storage_account_name, storage_account_key, retry_policy=retry,
            transport=MockTransport())

        # Act
        MockTransport.ENABLE = True

        # Assert

        # Try put
        def put_retry_callback(retry_count=None, location_mode=None, **kwargs):
            # This call should be called once, with the decision to try secondary
            put_retry_callback.called = True
            if MockTransport.CALL_NUMBER == 1:
                assert LocationMode.PRIMARY == location_mode
            elif MockTransport.CALL_NUMBER == 2:
                assert LocationMode.PRIMARY == location_mode
            else:
                pytest.fail("This test is not supposed to retry more than once")
        put_retry_callback.called = False

        container = service.get_container_client('containername')
        created = await container.create_container(retry_hook=put_retry_callback)
        assert put_retry_callback.called

        def retry_callback(retry_count=None, location_mode=None, **kwargs):
            # This call should be called once, with the decision to try secondary
            retry_callback.called = True
            if MockTransport.CALL_NUMBER == 1:
                assert LocationMode.SECONDARY == location_mode
            elif MockTransport.CALL_NUMBER == 2:
                assert LocationMode.SECONDARY == location_mode
            else:
                pytest.fail("This test is not supposed to retry more than once")
        retry_callback.called = False

        # Try list
        MockTransport.CALL_NUMBER = 1
        retry_callback.called = False
        containers = service.list_containers(
            results_per_page=1, retry_hook=retry_callback)
        await containers.__anext__()
        assert retry_callback.called

        # Try get
        MockTransport.CALL_NUMBER = 1
        retry_callback.called = False
        await container.get_container_properties(retry_hook=retry_callback)
        assert retry_callback.called

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_invalid_account_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        container_name = self.get_resource_name('utcontainer')
        retry = ExponentialRetry(initial_backoff=1, increment_base=3, retry_total=3)
        service = self._create_storage_service(
            BlobServiceClient, storage_account_name, storage_account_key, retry_policy=retry)
        service.credential.account_name = "dummy_account_name"
        service.credential.account_key = "dummy_account_key"

        # Shorten retries and add counter
        retry_counter = RetryCounter()
        retry_callback = retry_counter.simple_count

        # Act
        with pytest.raises(ClientAuthenticationError):
            await service.create_container(container_name, retry_callback=retry_callback)

        # Assert
        # No retry should be performed since the signing error is fatal
        assert retry_counter.count == 0

    @staticmethod
    def _count_wrapper(counter, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            counter[0] += 1
            return func(*args, **kwargs)
        return wrapper

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_streaming_retry(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        """Test that retry mechanisms are working when streaming data."""
        container_name = self.get_resource_name('utcontainer') 
        retry = LinearRetry(backoff = 0.1, random_jitter_range=0)

        service = self._create_storage_service(
            BlobServiceClient, storage_account_name, storage_account_key, retry_policy=retry)
        container = service.get_container_client(container_name)
        await container.create_container()
        assert await container.exists()
        blob_name = "myblob"
        await container.upload_blob(blob_name, b"abcde")

        stream_reader_read_mock = mock.MagicMock()
        future = asyncio.Future()
        future.set_exception(IncompleteReadError())
        stream_reader_read_mock.return_value = future
        with mock.patch.object(StreamReader, "read", stream_reader_read_mock), pytest.raises(HttpResponseError):
            blob = container.get_blob_client(blob=blob_name)
            count = [0]
            blob._pipeline._transport.send = self._count_wrapper(count, blob._pipeline._transport.send)
            await blob.download_blob()
        assert stream_reader_read_mock.call_count == count[0] == 3

    @BlobPreparer()
    async def test_invalid_storage_account_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = "a"

        # Arrange
        blob_client = self._create_storage_service(
            BlobClient,
            storage_account_name,
            storage_account_key,
            container_name="foo",
            blob_name="bar"
        )

        retry_counter = RetryCounter()
        retry_callback = retry_counter.simple_count

        # Act
        with pytest.raises(AzureSigningError) as e:
            await blob_client.get_blob_properties(retry_hook=retry_callback)

        # Assert
        assert ("This is likely due to an invalid shared key. Please check your shared key and try again." in
                e.value.message)
        assert retry_counter.count == 0

# ------------------------------------------------------------------------------
