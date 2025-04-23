import os
from datetime import datetime

import pytest

from azure.ai.ml import load_capability_host
from azure.ai.ml._restclient.v2025_01_01_preview.models._models_py3 import CapabilityHost as RestCapabilityHost
from azure.ai.ml._restclient.v2025_01_01_preview.models._models_py3 import (
    CapabilityHostProperties as RestCapabilityHostProperties,
)
from azure.ai.ml.entities._workspace._ai_workspaces.capability_host import CapabilityHost


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestCapabilityHostEntity:
    def test_capability_host_hub_schema(self) -> None:
        capability_host = load_capability_host(
            source="./tests/test_configs/workspace/ai_workspaces/test_capability_host_hub.yml"
        )
        assert capability_host is not None
        assert capability_host.name == "test_capability_host_hub"
        assert capability_host.description == "Capability host in hub for unit tests"
        assert capability_host.capability_host_kind == "Agents"
        assert capability_host.ai_services_connections is not None and len(capability_host.ai_services_connections) == 0
        assert capability_host.storage_connections is not None and len(capability_host.storage_connections) == 0
        assert (
            capability_host.vector_store_connections is not None and len(capability_host.vector_store_connections) == 0
        )

    def test_capability_host_project_schema(self) -> None:
        capability_host = load_capability_host(
            source="./tests/test_configs/workspace/ai_workspaces/test_capability_host_project.yml"
        )
        assert capability_host is not None
        assert capability_host.name == "test_capability_host_project"
        assert capability_host.description == "Capability host in project for unit tests"
        assert capability_host.capability_host_kind == "Agents"
        assert (
            capability_host.ai_services_connections is not None
            and len(capability_host.ai_services_connections) == 1
            and capability_host.ai_services_connections[0] == "aiservice_connection_1"
        )
        assert (
            capability_host.storage_connections is not None
            and len(capability_host.storage_connections) == 1
            and capability_host.storage_connections[0] == "storage_connection_1"
        )
        assert (
            capability_host.vector_store_connections is not None
            and len(capability_host.vector_store_connections) == 1
            and capability_host.vector_store_connections[0] == "vector_store_connection_1"
        )
        assert (
            capability_host.thread_storage_connections is not None
            and len(capability_host.thread_storage_connections) == 1
            and capability_host.thread_storage_connections[0] == "thread_storage_connection_1"
        )

    def test_capability_host_constructor(self) -> None:
        capability_host = CapabilityHost(
            name="test_capability_host",
            description="Capability host for unit tests",
            capability_host_kind="Agents",
            ai_services_connections=["aiservice_connection_1"],
            storage_connections=["storage_connection_1"],
            vector_store_connections=["vector_store_connection_1"],
        )

        assert capability_host.name == "test_capability_host"
        assert capability_host.description == "Capability host for unit tests"
        assert capability_host.capability_host_kind == "Agents"
        assert (
            capability_host.ai_services_connections is not None
            and len(capability_host.ai_services_connections) == 1
            and capability_host.ai_services_connections[0] == "aiservice_connection_1"
        )
        assert (
            capability_host.storage_connections is not None
            and len(capability_host.storage_connections) == 1
            and capability_host.storage_connections[0] == "storage_connection_1"
        )
        assert (
            capability_host.vector_store_connections is not None
            and len(capability_host.vector_store_connections) == 1
            and capability_host.vector_store_connections[0] == "vector_store_connection_1"
        )

    def test_from_rest_object(self) -> None:
        properties = RestCapabilityHostProperties(
            description="description test",
            ai_services_connections=["aiservice_connection_1"],
            storage_connections=["storage_connection_1"],
            vector_store_connections=["vector_store_connection_1"],
            capability_host_kind="Agents",
        )
        rest_capability_host = RestCapabilityHost(
            properties=properties,
        )
        capability_host = CapabilityHost._from_rest_object(rest_capability_host)

        assert isinstance(capability_host, CapabilityHost)
        assert capability_host.description == "description test"
        assert capability_host.capability_host_kind == "Agents"
        assert (
            capability_host.ai_services_connections is not None
            and len(capability_host.ai_services_connections) == 1
            and capability_host.ai_services_connections[0] == "aiservice_connection_1"
        )
        assert (
            capability_host.storage_connections is not None
            and len(capability_host.storage_connections) == 1
            and capability_host.storage_connections[0] == "storage_connection_1"
        )
        assert (
            capability_host.vector_store_connections is not None
            and len(capability_host.vector_store_connections) == 1
            and capability_host.vector_store_connections[0] == "vector_store_connection_1"
        )

    def test_to_rest_object_for_hub(self) -> None:
        capability_host = load_capability_host(
            source="./tests/test_configs/workspace/ai_workspaces/test_capability_host_hub.yml"
        )
        rest_capability_host = CapabilityHost._to_rest_object(capability_host)

        assert isinstance(rest_capability_host, RestCapabilityHost)
        assert rest_capability_host.properties is not None
        assert rest_capability_host.properties.description == "Capability host in hub for unit tests"
        assert rest_capability_host.properties.capability_host_kind == "Agents"
        assert (
            rest_capability_host.properties.ai_services_connections is None
            or len(rest_capability_host.properties.ai_services_connections) == 0
        )
        assert (
            rest_capability_host.properties.storage_connections is None
            or len(rest_capability_host.properties.storage_connections) == 0
        )
        assert (
            rest_capability_host.properties.vector_store_connections is None
            or len(rest_capability_host.properties.vector_store_connections) == 0
        )

    def test_to_rest_object_for_project(self) -> None:
        capability_host = load_capability_host(
            source="./tests/test_configs/workspace/ai_workspaces/test_capability_host_project.yml"
        )
        rest_capability_host = CapabilityHost._to_rest_object(capability_host)

        assert isinstance(rest_capability_host, RestCapabilityHost)
        assert rest_capability_host.properties is not None
        assert rest_capability_host.properties.description == "Capability host in project for unit tests"
        assert rest_capability_host.properties.capability_host_kind == "Agents"
        assert (
            rest_capability_host.properties.ai_services_connections is not None
            and len(rest_capability_host.properties.ai_services_connections) == 1
            and rest_capability_host.properties.ai_services_connections[0] == "aiservice_connection_1"
        )
        assert (
            rest_capability_host.properties.storage_connections is not None
            and len(rest_capability_host.properties.storage_connections) == 1
            and rest_capability_host.properties.storage_connections[0] == "storage_connection_1"
        )
        assert (
            rest_capability_host.properties.vector_store_connections is not None
            and len(rest_capability_host.properties.vector_store_connections) == 1
            and rest_capability_host.properties.vector_store_connections[0] == "vector_store_connection_1"
        )

    def test_dump(self) -> None:
        capability_host = load_capability_host(
            source="./tests/test_configs/workspace/ai_workspaces/test_capability_host_project.yml"
        )
        epoch_timestamp = int(datetime.now().timestamp())  # Current Unix timestamp as an integer
        dump_file_name = f"./tests/test_configs/workspace/ai_workspaces/test_capability_host_dump_{epoch_timestamp}.yml"
        CapabilityHost.dump(capability_host, dest=dump_file_name)

        assert os.path.exists(dump_file_name)
        # Read the file content
        with open(dump_file_name, "r") as file:
            file_content = file.read()

        # Assert the file content
        assert "test_capability_host" in file_content
        assert "Capability host in project for unit tests" in file_content
        assert "Agents" in file_content
        assert "aiservice_connection_1" in file_content
        assert "storage_connection_1" in file_content
        assert "vector_store_connection_1" in file_content

        os.remove(dump_file_name)
