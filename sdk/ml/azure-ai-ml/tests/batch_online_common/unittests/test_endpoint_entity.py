import pytest
import yaml
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_batch_endpoint, load_online_endpoint
from azure.ai.ml.entities import BatchEndpoint, Endpoint, ManagedOnlineDeployment, OnlineEndpoint


@pytest.mark.production_experiences_test
@pytest.mark.unittest
class TestOnlineEndpointYAML:
    SIMPLE_ENDPOINT_WITH_BLUE_BAD = "tests/test_configs/endpoints/online/online_endpoint_create_aks_bad.yml"
    MINIMAL_ENDPOINT = "tests/test_configs/endpoints/online/online_endpoint_minimal.yaml"
    MINIMAL_DEPLOYMENT = "tests/test_configs/deployments/online/online_endpoint_deployment_k8s_minimum.yml"

    def test_specific_endpoint_load_and_dump(self) -> None:
        with open(TestOnlineEndpointYAML.MINIMAL_ENDPOINT, "r") as f:
            target = yaml.safe_load(f)

        def simple_online_endpoint_validation(endpoint):
            assert isinstance(endpoint, OnlineEndpoint)
            assert endpoint.name == target["name"]

        _ = verify_entity_load_and_dump(
            load_online_endpoint,
            simple_online_endpoint_validation,
            TestOnlineEndpointYAML.MINIMAL_ENDPOINT,
            test_dump_file_path=None,
        )

    def test_default_endpoint_load_to_online(self) -> None:
        with open(TestOnlineEndpointYAML.MINIMAL_ENDPOINT, "r") as f:
            target = yaml.safe_load(f)
        endpoint = load_online_endpoint(TestOnlineEndpointYAML.MINIMAL_ENDPOINT)
        assert isinstance(endpoint, OnlineEndpoint)
        assert endpoint.name == target["name"]

    def test_online_endpoint_to_rest_object_with_no_issue(self) -> None:
        endpoint = load_online_endpoint(TestOnlineEndpointYAML.MINIMAL_ENDPOINT)
        endpoint._to_rest_online_endpoint("westus2")


@pytest.mark.unittest
class TestBatchEndpointYAML:
    BATCH_ENDPOINT_WITH_BLUE = "tests/test_configs/endpoints/batch/batch_endpoint.yaml"

    def test_generic_endpoint_load_and_dump_2(self) -> None:
        with open(TestBatchEndpointYAML.BATCH_ENDPOINT_WITH_BLUE, "r") as f:
            target = yaml.safe_load(f)

        def simple_batch_endpoint_validation(endpoint):
            assert isinstance(endpoint, BatchEndpoint)
            assert endpoint.name == target["name"].lower()
            assert endpoint.description == target["description"]
            assert endpoint.auth_mode == target["auth_mode"]

        verify_entity_load_and_dump(
            load_batch_endpoint,
            simple_batch_endpoint_validation,
            TestBatchEndpointYAML.BATCH_ENDPOINT_WITH_BLUE,
            test_dump_file_path=None,
        )

    def test_to_rest_batch_endpoint(self) -> None:
        with open(TestBatchEndpointYAML.BATCH_ENDPOINT_WITH_BLUE, "r") as f:
            target = yaml.safe_load(f)
        endpoint = load_batch_endpoint(TestBatchEndpointYAML.BATCH_ENDPOINT_WITH_BLUE)
        rest_batch_endpoint = endpoint._to_rest_batch_endpoint("master")

        assert rest_batch_endpoint.tags
        assert len(rest_batch_endpoint.tags)
        assert rest_batch_endpoint.tags == target["tags"]

    def test_batch_endpoint_with_deployment_name_promoted_param_only(self) -> None:
        endpoint = BatchEndpoint(
            name="my-batch-endpoint",
            description="this is a sample batch endpoint",
            defaults={"deployment_name": "gg"},
            default_deployment_name="fff",
            # badParam="I should not break", until it is fixed in SDK
            tags={"foo": "bar"},
        )

        assert endpoint.defaults["deployment_name"] == "gg"

    def test_batch_endpoint_with_deployment_name_promoted_param_and_main_param(self) -> None:

        endpoint = BatchEndpoint(
            name="my-batch-endpoint",
            description="this is a sample batch endpoint",
            default_deployment_name="fff",
            # badParam="I should not break", until it is fixed in SDK
            tags={"foo": "bar"},
        )

        assert endpoint.defaults["deployment_name"] == "fff"

    def test_batch_endpoint_with_deployment_no_defaults(self) -> None:

        endpoint = BatchEndpoint(
            name="my-batch-endpoint",
            description="this is a sample batch endpoint",
            # badParam="I should not break", until it is fixed in SDK
            tags={"foo": "bar"},
        )

        assert endpoint.defaults is None
