# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from azure.ai.ml._local_endpoints.endpoint_stub import EndpointStub
from azure.ai.ml.entities._endpoint.online_endpoint import OnlineEndpoint
import pytest
import random
from pathlib import Path
from azure.ai.ml import load_online_endpoint


@pytest.fixture
def endpoint_name() -> str:
    return f"mir-test-{str(random.randint(1, 10000000))}"


@pytest.fixture
def endpoint_mir_yaml() -> str:
    return "tests/test_configs/deployments/online/simple_online_endpoint_mir.yaml"


@pytest.mark.unittest
class TestEndpoingStub:
    def test_endpoint_stub_e2e(self, endpoint_name, endpoint_mir_yaml):
        endpoint_stub = EndpointStub()
        endpoint = load_online_endpoint(endpoint_mir_yaml)
        endpoint.name = endpoint_name

        endpoint_stub.create_or_update(endpoint=endpoint)

        assert _get_expected_endpoint_file(endpoint_name).exists()

        data = endpoint_stub.invoke()
        assert "deployment create" in data

        returned_endpoint = endpoint_stub.get(endpoint_name)
        assert returned_endpoint == endpoint

        endpoints = endpoint_stub.list()
        assert len(endpoints) > 0
        assert _get_expected_endpoint_file(endpoint_name) in endpoints

        endpoint.tags.update({"newkey": "newval"})
        endpoint_stub.create_or_update(endpoint=endpoint)
        returned_endpoint = endpoint_stub.get(endpoint_name)
        assert returned_endpoint.tags.get("newkey") and returned_endpoint.tags.get("newkey") == "newval"

        endpoint_stub.delete(endpoint_name)
        returned_endpoint = endpoint_stub.get(endpoint_name)
        assert returned_endpoint is None
        assert _get_expected_endpoint_file(endpoint_name).exists() is False


def _get_expected_directory(endpoint_name: str) -> Path:
    return Path(Path.home(), ".azureml", "inferencing", endpoint_name)


def _get_expected_endpoint_file(endpoint_name: str) -> Path:
    return Path(_get_expected_directory(endpoint_name), f"{endpoint_name}.json")
