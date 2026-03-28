from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient, load_batch_endpoint
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.exceptions import ValidationException, MlException
from azure.core.exceptions import ResourceNotFoundError


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestBatchEndpointGaps(AzureRecordedTestCase):
    def test_invoke_with_nonexistent_deployment_name_raises_validation_exception(
        self, client: MLClient, rand_batch_name: Callable[[], str]
    ) -> None:
        """
        Covers: marker lines related to deployment name validation paths in _validate_deployment_name.
        Trigger strategy: create a batch endpoint, do not create any deployments, then call invoke with a
        deployment_name that does not exist to force a ValidationException from _validate_deployment_name.
        """
        endpoint_yaml = (
            "./tests/test_configs/endpoints/batch/simple_batch_endpoint.yaml"
        )
        name = rand_batch_name("name")

        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = name
        # create the batch endpoint
        obj = client.batch_endpoints.begin_create_or_update(endpoint=endpoint)
        obj = obj.result()
        assert obj is not None
        assert obj.name == name

        # Invoke with a deployment name that doesn't exist; this should raise a ValidationException
        with pytest.raises(ValidationException):
            client.batch_endpoints.invoke(
                endpoint_name=name, deployment_name="nonexistent_deployment"
            )

        # cleanup
        delete_res = client.batch_endpoints.begin_delete(name=name)
        delete_res = delete_res.result()
        try:
            client.batch_endpoints.get(name=name)
        except Exception as e:
            assert type(e) is ResourceNotFoundError
            return
        raise Exception(f"Batch endpoint {name} is supposed to be deleted.")

    def test_invoke_with_empty_input_path_raises_mlexception(
        self, client: MLClient, rand_batch_name: Callable[[], str]
    ) -> None:
        """
        Covers: marker lines related to _resolve_input raising MlException when input.path is empty.
        Trigger strategy: create a batch endpoint and call invoke with input=Input(path="") to trigger validation.
        """
        endpoint_yaml = (
            "./tests/test_configs/endpoints/batch/simple_batch_endpoint.yaml"
        )
        name = rand_batch_name("name")

        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = name
        # create the batch endpoint
        obj = client.batch_endpoints.begin_create_or_update(endpoint=endpoint)
        obj = obj.result()
        assert obj is not None
        assert obj.name == name

        empty_input = Input(type="uri_folder", path="")
        with pytest.raises(MlException):
            client.batch_endpoints.invoke(endpoint_name=name, input=empty_input)

        # cleanup
        delete_res = client.batch_endpoints.begin_delete(name=name)
        delete_res = delete_res.result()
        try:
            client.batch_endpoints.get(name=name)
        except Exception as e:
            assert type(e) is ResourceNotFoundError
            return
        raise Exception(f"Batch endpoint {name} is supposed to be deleted.")


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestBatchEndpointGaps_Generated(AzureRecordedTestCase):
    def test_list_jobs_returns_list(
        self, client: MLClient, rand_batch_name: Callable[[], str]
    ) -> None:
        endpoint_yaml = (
            "./tests/test_configs/endpoints/batch/simple_batch_endpoint.yaml"
        )
        endpoint_name = rand_batch_name("endpoint_name")
        endpoint = load_batch_endpoint(endpoint_yaml)
        endpoint.name = endpoint_name

        # create the batch endpoint
        client.batch_endpoints.begin_create_or_update(endpoint).result()

        # list_jobs should return a list (possibly empty)
        result = client.batch_endpoints.list_jobs(endpoint_name=endpoint_name)
        assert isinstance(result, list)

        # cleanup
        client.batch_endpoints.begin_delete(name=endpoint_name).result()
