import json
from pathlib import Path
from typing import Callable

import pytest

from azure.ai.ml import MLClient
from azure.ai.ml._local_endpoints import LocalEndpointMode
from azure.ai.ml.exceptions import (
    DockerEngineNotAvailableError,
    InvalidLocalEndpointError,
    LocalEndpointNotFoundError,
)
import random


@pytest.fixture
def randstr():
    """Simple randstr fixture for unit tests that generates random strings without recording infrastructure."""
    def _generate(variable_name: str) -> str:
        return f"test_{random.randint(1, 1000000000000)}"
    return _generate


@pytest.mark.unittest
class TestLocalEndpointHelperGaps:
    def test_create_or_update_with_none_raises_invalid_local_endpoint(
        self, client: MLClient
    ) -> None:
        with pytest.raises((InvalidLocalEndpointError, TypeError)):
            client.online_endpoints.begin_create_or_update(endpoint=None, local=True)

    def test_get_nonexistent_local_endpoint_raises(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        name = randstr("get_ep")
        with pytest.raises((LocalEndpointNotFoundError, DockerEngineNotAvailableError)):
            client.online_endpoints.get(name=name, local=True)

    def test_list_local_endpoints_returns_iterable(self, client: MLClient) -> None:
        try:
            result = client.online_endpoints.list(local=True)
            assert hasattr(result, "__iter__")
        except (DockerEngineNotAvailableError,):
            pytest.skip("Docker daemon not accessible")
        except Exception as e:
            if "docker" in str(e).lower() or "connection" in str(e).lower():
                pytest.skip("Docker daemon not accessible")
            raise

    def test_delete_nonexistent_local_endpoint_raises(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        name = randstr("del_ep")
        with pytest.raises((LocalEndpointNotFoundError, DockerEngineNotAvailableError)):
            client.online_endpoints.begin_delete(name=name, local=True)

    def test_invoke_nonexistent_local_endpoint_raises(
        self, client: MLClient, randstr: Callable[[str], str], tmp_path: Path
    ) -> None:
        request_file = tmp_path / "request.json"
        request_file.write_text(json.dumps({"data": [1]}))
        name = randstr("invoke_ep")
        with pytest.raises((LocalEndpointNotFoundError, DockerEngineNotAvailableError)):
            client.online_endpoints.invoke(
                endpoint_name=name,
                request_file=str(request_file),
                local=True,
            )

    def test_local_helper_create_or_update_none_raises(
        self, client: MLClient
    ) -> None:
        helper = client.online_deployments._local_deployment_helper
        with pytest.raises(InvalidLocalEndpointError):
            helper.create_or_update(
                deployment=None,
                local_endpoint_mode=LocalEndpointMode.VSCodeDevContainer,
            )

    def test_local_helper_get_nonexistent_raises(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        helper = client.online_deployments._local_deployment_helper
        ep_name = randstr("helper_get_ep")
        dep_name = randstr("helper_get_dep")
        with pytest.raises((LocalEndpointNotFoundError, DockerEngineNotAvailableError)):
            helper.get(endpoint_name=ep_name, deployment_name=dep_name)

    def test_local_helper_delete_nonexistent_raises(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        helper = client.online_deployments._local_deployment_helper
        ep_name = randstr("helper_del_ep")
        dep_name = randstr("helper_del_dep")
        with pytest.raises((LocalEndpointNotFoundError, DockerEngineNotAvailableError)):
            helper.delete(name=ep_name, deployment_name=dep_name)

    def test_get_deployment_logs_nonexistent_raises(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        ep_name = randstr("logs_ep")
        dep_name = randstr("logs_dep")
        with pytest.raises((LocalEndpointNotFoundError, DockerEngineNotAvailableError)):
            client.online_deployments.get_logs(
                endpoint_name=ep_name,
                name=dep_name,
                lines=10,
                local=True,
            )

    def test_list_local_deployments_returns_iterable(
        self, client: MLClient, randstr: Callable[[str], str]
    ) -> None:
        ep_name = randstr("list_dep_ep")
        try:
            result = client.online_deployments.list(
                endpoint_name=ep_name, local=True
            )
        except (DockerEngineNotAvailableError, LocalEndpointNotFoundError):
            return  # No local endpoints to list — acceptable
        assert hasattr(result, "__iter__")
