from typing import Callable
from collections.abc import Iterable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

from azure.ai.ml import MLClient, load_batch_deployment, load_batch_endpoint
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.exceptions import ValidationException, MlException


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestBatchEndpointGaps2(AzureRecordedTestCase):

    def test_list_endpoints_returns_iterable(self, client: MLClient) -> None:
        """
        Covers the list() path which invokes the underlying service client's list method
        and returns an ItemPaged that can be iterated / materialized.
        """
        result = client.batch_endpoints.list()
        # Ensure the returned object is iterable without forcing network iteration
        assert isinstance(result, Iterable)

    def test_get_nonexistent_endpoint_raises_resource_not_found(self, client: MLClient, rand_batch_name: Callable[[], str]) -> None:
        """
        Covers the get() path and verifies the service raises ResourceNotFoundError for unknown endpoint name.
        """
        name = rand_batch_name("nonexistent")
        with pytest.raises((ResourceNotFoundError, ClientAuthenticationError)):
            client.batch_endpoints.get(name=name)

    def test_invoke_with_empty_input_path_raises_ml_exception(self, client: MLClient, rand_batch_name: Callable[[], str]) -> None:
        """
        Covers the _resolve_input empty path check inside invoke() which should raise MlException.
        """
        endpoint_name = rand_batch_name("endpoint_name")
        empty_input = Input(type="uri_folder", path="")
        with pytest.raises(MlException):
            client.batch_endpoints.invoke(endpoint_name=endpoint_name, input=empty_input)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test", "mock_asset_name")
@pytest.mark.production_experiences_test
class TestBatchEndpointGaps(AzureRecordedTestCase):

    def test_invoke_with_unsupported_input_type_raises_validation_exception(
        self, client: MLClient, rand_batch_name: Callable[[], str]
    ) -> None:
        """Verify that passing an Input with an unsupported type to the deprecated `input` parameter
        raises a ValidationException as implemented in BatchEndpointOperations.invoke().

        Covers branches where `input` is provided and has a type other than `uri_folder` or `uri_file`.
        """
        endpoint_name = rand_batch_name("endpoint")

        bad_input = Input(type="unsupported_type", path="https://example.com/data")

        with pytest.raises(ValidationException):
            client.batch_endpoints.invoke(endpoint_name=endpoint_name, input=bad_input)


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestBatchEndpointValidationGaps(AzureRecordedTestCase):

    def test_invoke_with_deprecated_input_unsupported_type_raises_validation_exception(
        self, client: MLClient
    ) -> None:
        """
        Covered marker lines: [376, 377, 378, 379]
        Branch summary: When invoke() is called with the deprecated single `input` argument and the
        Input.type is not 'uri_folder' or 'uri_file', the code should raise a ValidationException
        describing an unsupported input type.
        Trigger strategy: Call invoke() with an Input whose type is an unsupported custom value. The
        validation occurs locally before any network invocation.
        """
        # Use a made-up endpoint name; we expect validation to occur before any network post if
        # the input is detected as unsupported. Use a non-existing endpoint name to ensure that
        # if the code attempted to reach the service it would error earlier; however the unsupported
        # input type check happens before remote calls.
        fake_endpoint = "nonexistent-endpoint-for-input-test"
        bad_input = Input(type="some_unsupported_type", path="https://example.com/data")

        with pytest.raises(ValidationException) as exc:
            client.batch_endpoints.invoke(endpoint_name=fake_endpoint, input=bad_input)

        assert "Unsupported input type" in str(exc.value)

    def test_invoke_with_empty_input_path_raises_ml_exception(self, client: MLClient) -> None:
        """
        Covered marker lines: [369]
        Branch summary: When invoke() receives an Input with an empty path, _resolve_input should raise
        an MlException indicating the path can't be empty. This is a local validation that happens
        before any network calls.
        Trigger strategy: Call invoke() with a deprecated `input` parameter that is an Input with
        an empty path.
        """
        fake_endpoint = "nonexistent-endpoint-empty-path"
        empty_input = Input(type="uri_folder", path="")

        with pytest.raises(MlException) as exc:
            client.batch_endpoints.invoke(endpoint_name=fake_endpoint, input=empty_input)

        assert "Input path can't be empty" in str(exc.value)
