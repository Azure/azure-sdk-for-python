from pathlib import Path
import types
import collections
from types import SimpleNamespace
from unittest.mock import MagicMock
from typing import Optional

import pytest
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, OperationsContainer
from azure.ai.ml.constants._common import DEFAULT_COMPONENT_VERSION, DEFAULT_LABEL_NAME, AzureMLResourceType
from azure.ai.ml.entities import Component
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent
from azure.ai.ml.exceptions import ValidationException, ErrorTarget, ComponentException
from azure.ai.ml._utils._asset_utils import IgnoreFile
from azure.ai.ml.entities._component.code import ComponentCodeMixin

from azure.ai.ml.operations._component_operations import ComponentOperations
from azure.ai.ml.operations._component_operations import _get_latest, _archive_or_restore
import azure.ai.ml.operations._component_operations as component_ops_mod


class DummyServiceClient:
    def __init__(self):
        self.component_versions = object()
        self.component_containers = object()


def _create_component_operations(workspace_name="test-ws", registry_name=None):
    operation_scope = OperationScope(
        subscription_id="sub-id",
        resource_group_name="rg-name",
        workspace_name=workspace_name,
        registry_name=registry_name,
    )
    operation_config = OperationConfig(show_progress=False, enable_telemetry=False)
    service_client = DummyServiceClient()
    all_operations = OperationsContainer()
    preflight_operation = None
    return ComponentOperations(
        operation_scope=operation_scope,
        operation_config=operation_config,
        service_client=service_client,
        all_operations=all_operations,
        preflight_operation=preflight_operation,
    )


def _build_component_operations_for_resolve_dependencies():
    scope = OperationScope("sub", "rg", "ws")
    config = OperationConfig(show_progress=False, enable_telemetry=False)
    service_client = SimpleNamespace(
        component_versions=MagicMock(),
        component_containers=MagicMock(),
    )
    operations_container = OperationsContainer()
    for resource_type in (
        AzureMLResourceType.COMPONENT,
        AzureMLResourceType.CODE,
        AzureMLResourceType.ENVIRONMENT,
        AzureMLResourceType.WORKSPACE,
        AzureMLResourceType.JOB,
    ):
        operations_container.add(resource_type, MagicMock())
    return ComponentOperations(scope, config, service_client, operations_container)


def test_resolve_dependencies_for_component_short_circuits_for_automl(monkeypatch):
    component_ops = _build_component_operations_for_resolve_dependencies()

    class _StubAutoMLComponent:
        pass

    monkeypatch.setattr(
        "azure.ai.ml.operations._component_operations.AutoMLComponent",
        _StubAutoMLComponent,
    )

    stub_component = _StubAutoMLComponent()
    result = component_ops._resolve_dependencies_for_component(
        stub_component,
        resolver=lambda value, azureml_type=None: value,
    )
    assert result is None


def test_resolve_dependencies_for_component_invalid_type_raises(monkeypatch):
    component_ops = _build_component_operations_for_resolve_dependencies()

    class _StubAutoMLComponent:
        pass

    monkeypatch.setattr(
        "azure.ai.ml.operations._component_operations.AutoMLComponent",
        _StubAutoMLComponent,
    )

    with pytest.raises(ValidationException) as exc_info:
        component_ops._resolve_dependencies_for_component(
            object(),
            resolver=lambda value, azureml_type=None: value,
        )
    assert "Non supported component type" in str(exc_info.value)


def test_resolve_pipeline_component_jobs_unsupported_job_raises(monkeypatch):
    component_ops = _build_component_operations_for_resolve_dependencies()
    component = PipelineComponent(name="pipeline", version="1")
    component._jobs = {"bad_job": object()}
    component._base_path = "base"
    unsupported_job = component._jobs["bad_job"]

    monkeypatch.setattr(
        ComponentOperations,
        "_resolve_inputs_for_pipeline_component_jobs",
        lambda self, jobs, base_path: None,
    )
    monkeypatch.setattr(
        ComponentOperations,
        "_divide_nodes_to_resolve_into_layers",
        lambda self, component_arg, extra_operations: [[("bad_job", unsupported_job)]],
    )
    monkeypatch.setattr(
        ComponentOperations,
        "_get_client_key",
        lambda self: "dummy-client",
    )

    class _StubCachedResolver:
        def __init__(self, resolver, client_key):
            self._resolver = resolver
            self._client_key = client_key

        def register_node_for_lazy_resolution(self, node):
            pass

        def resolve_nodes(self):
            pass

    monkeypatch.setattr(
        "azure.ai.ml.operations._component_operations.CachedNodeResolver",
        _StubCachedResolver,
    )

    with pytest.raises(ComponentException) as exc_info:
        component_ops._resolve_dependencies_for_pipeline_component_jobs(
            component,
            resolver=lambda value, azureml_type=None: value,
        )
    assert "Non supported job type in Pipeline" in str(exc_info.value)
