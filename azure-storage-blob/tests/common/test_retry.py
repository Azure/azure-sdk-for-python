# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest

pytestmark = pytest.mark.skip

from azure.common import (
    AzureHttpError,
    AzureException,
)

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
# from azure.storage.common import (
#     LocationMode,
#     AzureSigningError,
# )
# from azure.storage.common.retry import (
#     LinearRetry,
#     ExponentialRetry,
#     no_retry,
# )
# from azure.storage.common.models import RetryContext
from tests.testcase import (
    StorageTestCase,
    record,
    ResponseCallback,
    RetryCounter,
)


# --Helper Classes---------------------------------------------------------------

class _OperationContext(object):
    def __init__(self, location_lock=False):
        self.location_lock = location_lock
        self.host_location = None


# --Test Class -----------------------------------------------------------------
class StorageRetryTest(StorageTestCase):
    def setUp(self):
        super(StorageRetryTest, self).setUp()

    def tearDown(self):
        return super(StorageRetryTest, self).tearDown()

    # --Test Cases --------------------------------------------
    @record
    def test_retry_on_server_error(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)

        # Force the create call to 'timeout' with a 408
        service.response_callback = ResponseCallback(status=201, new_status=500).override_status

        # Act
        try:
            created = service.create_container(container_name)
        finally:
            service.delete_container(container_name)

        # Assert
        # The initial create will return 201, but we overwrite it and retry.
        # The retry will then get a 409 and return false.
        self.assertFalse(created)

    @record
    def test_retry_on_timeout(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.retry = ExponentialRetry(initial_backoff=1, increment_base=2).retry

        service.response_callback = ResponseCallback(status=201, new_status=408).override_status

        # Act
        try:
            created = service.create_container(container_name)
        finally:
            service.delete_container(container_name)

        # Assert
        # The initial create will return 201, but we overwrite it and retry.
        # The retry will then get a 409 and return false.
        self.assertFalse(created)

    @record
    def test_retry_callback_and_retry_context(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.retry = LinearRetry(backoff=1).retry

        # Force the create call to 'timeout' with a 408
        service.response_callback = ResponseCallback(status=201, new_status=408).override_status

        def assert_exception_is_present_on_retry_context(retry_context):
            self.assertIsNotNone(retry_context.exception)

        service.retry_callback = assert_exception_is_present_on_retry_context

        # Act
        try:
            service.create_container(container_name)
        finally:
            service.response_callback = None
            service.delete_container(container_name)

    @record
    def test_retry_on_socket_timeout(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.retry = LinearRetry(backoff=1).retry

        # make the connect timeout reasonable, but packet timeout truly small, to make sure the request always times out
        service.socket_timeout = (11, 0.000000000001)

        # Act
        try:
            service.create_container(container_name)
        except AzureException as e:
            # Assert
            # This call should succeed on the server side, but fail on the client side due to socket timeout
            self.assertTrue('read timeout' in str(e), 'Expected socket timeout but got different exception.')
            pass
        finally:
            # we must make the timeout normal again to let the delete operation succeed
            service.socket_timeout = (11, 11)
            service.delete_container(container_name)

    @record
    def test_no_retry(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.retry = no_retry

        # Force the create call to 'timeout' with a 408
        service.response_callback = ResponseCallback(status=201, new_status=408).override_status

        # Act
        try:
            service.create_container(container_name)
            self.fail('The callback should force failure.')
        except AzureHttpError as e:
            # Assert
            # The call should not retry, and thus fail.
            self.assertEqual(408, e.status_code)
            self.assertEqual('Created\n', e.args[0])
        finally:
            service.delete_container(container_name)

    @record
    def test_linear_retry(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.retry = LinearRetry(backoff=1).retry

        # Force the create call to 'timeout' with a 408
        service.response_callback = ResponseCallback(status=201, new_status=408).override_status

        # Act
        try:
            created = service.create_container(container_name)
        finally:
            service.delete_container(container_name)

        # Assert
        # The initial create will return 201, but we overwrite it and retry.
        # The retry will then get a 409 and return false.
        self.assertFalse(created)

    @record
    def test_exponential_retry(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.create_container(container_name)
        service.retry = ExponentialRetry(initial_backoff=1, increment_base=3, max_attempts=3).retry

        # Force the create call to 'timeout' with a 408
        response_callback = ResponseCallback(status=200, new_status=408)
        service.response_callback = response_callback.override_status

        # Act
        with self.assertRaises(AzureHttpError):
            service.get_container_metadata(container_name)

        # Assert the response was called the right number of times (1 initial request + 3 retries)
        self.assertEqual(response_callback.count, 1+3)

        # Clean up
        service.response_callback = None
        service.delete_container(container_name)

    def test_exponential_retry_interval(self):
        # Arrange
        retry_policy = ExponentialRetry(initial_backoff=1, increment_base=3, random_jitter_range=3)
        context_stub = RetryContext()

        for i in range(10):
            # Act
            context_stub.count = 0
            backoff = retry_policy._backoff(context_stub)

            # Assert backoff interval is within +/- 3 of 1
            self.assertTrue(0 <= backoff <= 4)

            # Act
            context_stub.count = 1
            backoff = retry_policy._backoff(context_stub)

            # Assert backoff interval is within +/- 3 of 4(1+3^1)
            self.assertTrue(1 <= backoff <= 7)

            # Act
            context_stub.count = 2
            backoff = retry_policy._backoff(context_stub)

            # Assert backoff interval is within +/- 3 of 10(1+3^2)
            self.assertTrue(7 <= backoff <= 13)

            # Act
            context_stub.count = 3
            backoff = retry_policy._backoff(context_stub)

            # Assert backoff interval is within +/- 3 of 28(1+3^3)
            self.assertTrue(25 <= backoff <= 31)

    def test_linear_retry_interval(self):
        # Arrange
        context_stub = RetryContext()

        for i in range(10):
            # Act
            retry_policy = LinearRetry(backoff=1, random_jitter_range=3)
            backoff = retry_policy._backoff(context_stub)

            # Assert backoff interval is within +/- 3 of 1
            self.assertTrue(0 <= backoff <= 4)

            # Act
            retry_policy = LinearRetry(backoff=5, random_jitter_range=3)
            backoff = retry_policy._backoff(context_stub)

            # Assert backoff interval is within +/- 3 of 5
            self.assertTrue(2 <= backoff <= 8)

            # Act
            retry_policy = LinearRetry(backoff=15, random_jitter_range=3)
            backoff = retry_policy._backoff(context_stub)

            # Assert backoff interval is within +/- 3 of 15
            self.assertTrue(12 <= backoff <= 18)

    @record
    def test_invalid_retry(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.retry = ExponentialRetry(initial_backoff=1, increment_base=2).retry

        # Force the create call to fail by pretending it's a teapot
        service.response_callback = ResponseCallback(status=201, new_status=418).override_status

        # Act
        try:
            service.create_container(container_name)
            self.fail('The callback should force failure.')
        except AzureHttpError as e:
            # Assert
            self.assertEqual(418, e.status_code)
            self.assertEqual('Created\n', e.args[0])
        finally:
            service.delete_container(container_name)

    @record
    def test_retry_with_deserialization(self):
        # Arrange
        container_name = self.get_resource_name(prefix='retry')
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.retry = ExponentialRetry(initial_backoff=1, increment_base=2).retry

        try:
            created = service.create_container(container_name)

            # Act
            service.response_callback = ResponseCallback(status=200, new_status=408).override_first_status
            containers = service.list_containers(prefix='retry')

        finally:
            service.delete_container(container_name)

        # Assert
        self.assertTrue(len(list(containers)) >= 1)

    @record
    def test_secondary_location_mode(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.location_mode = LocationMode.SECONDARY
        service.retry = ExponentialRetry(initial_backoff=1, increment_base=2).retry

        # Act
        try:
            service.create_container(container_name)

            # Override the response from secondary if it's 404 as that simply means
            # the container hasn't replicated. We're just testing we try secondary,
            # so that's fine.
            service.response_callback = ResponseCallback(status=404, new_status=200).override_first_status

            # Assert
            def request_callback(request):
                if self.settings.IS_EMULATED:
                    self.assertNotEqual(-1, request.path.find('-secondary'))
                else:
                    self.assertNotEqual(-1, request.host.find('-secondary'))

            service.request_callback = request_callback
            service.get_container_metadata(container_name)
        finally:
            # Delete will go to primary, so disable the request validation
            service.request_callback = None
            service.delete_container(container_name)

    @record
    def test_retry_to_secondary_with_put(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.retry = ExponentialRetry(retry_to_secondary=True, initial_backoff=1, increment_base=2).retry

        # Act
        try:
            # Fail the first create attempt
            service.response_callback = ResponseCallback(status=201, new_status=408).override_first_status

            # Assert
            # Confirm that the create request does *not* get retried to secondary
            # This should actually throw InvalidPermissions if sent to secondary,
            # but validate the location_mode anyways.
            def retry_callback(retry_context):
                self.assertEqual(LocationMode.PRIMARY, retry_context.location_mode)

            service.retry_callback = retry_callback
            service.create_container(container_name)

        finally:
            service.response_callback = None
            service.retry_callback = None
            service.delete_container(container_name)

    @record
    def test_retry_to_secondary_with_get(self):
        # Arrange
        container_name = self.get_resource_name()
        service = self._create_storage_service(BlockBlobService, self.settings)
        service.retry = ExponentialRetry(retry_to_secondary=True, initial_backoff=1, increment_base=2).retry

        # Act
        try:
            service.create_container(container_name)
            service.response_callback = ResponseCallback(status=200, new_status=408).override_first_status

            # Assert
            # Confirm that the get request gets retried to secondary
            def retry_callback(retry_context):
                # Only check this every other time, sometimes the secondary location fails due to delay
                if retry_context.count % 2 == 1:
                    self.assertEqual(LocationMode.SECONDARY, retry_context.location_mode)

            service.retry_callback = retry_callback
            service.get_container_metadata(container_name)
        finally:
            service.response_callback = None
            service.retry_callback = None
            service.delete_container(container_name)

    @record
    def test_location_lock(self):
        # Arrange
        service = self._create_storage_service(BlockBlobService, self.settings)

        # Act
        # Fail the first request and set the retry policy to retry to secondary
        service.retry = ExponentialRetry(retry_to_secondary=True, initial_backoff=1, increment_base=2).retry
        service.response_callback = ResponseCallback(status=200, new_status=408).override_first_status
        context = _OperationContext(location_lock=True)

        # Assert
        # Confirm that the first request gets retried to secondary
        # The given test account must be GRS
        def retry_callback(retry_context):
            self.assertEqual(LocationMode.SECONDARY, retry_context.location_mode)

        service.retry_callback = retry_callback
        service._list_containers(prefix='lock', _context=context)

        # Confirm that the second list request done with the same context sticks 
        # to the final location of the first list request (aka secondary) despite 
        # the client normally trying primary first
        def request_callback(request):
            if self.settings.IS_EMULATED:
                self.assertNotEqual(-1, request.path.find('-secondary'))
            else:
                self.assertNotEqual(-1, request.host.find('-secondary'))

        service.request_callback = request_callback
        service._list_containers(prefix='lock', _context=context)

    def test_invalid_account_key(self):
        # Arrange
        container_name = self.get_resource_name()
        service = BlockBlobService(account_name="dummy_account_name", account_key="dummy_account_key")

        # Shorten retries and add counter
        service.retry = ExponentialRetry(initial_backoff=1, increment_base=3, max_attempts=3).retry
        retry_counter = RetryCounter()
        service.retry_callback = retry_counter.simple_count

        # Act
        with self.assertRaises(AzureSigningError):
            service.get_container_metadata(container_name)

        # Assert
        # No retry should be performed since the signing error is fatal
        self.assertEqual(retry_counter.count, 0)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
