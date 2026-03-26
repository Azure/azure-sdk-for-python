import pytest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

from azure.ai.ml.constants._common import ASSET_ID_FORMAT, AzureMLResourceType
from azure.ai.ml.entities import Environment
from azure.ai.ml.entities._assets import ModelPackage
from azure.ai.ml.entities._assets.workspace_asset_reference import WorkspaceAssetReference
from azure.ai.ml.exceptions import ValidationException
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, OperationsContainer
from azure.ai.ml.operations import _model_operations as model_module
from azure.ai.ml.operations._model_operations import ModelOperations


class _DummyModel:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties
        self.version = None
        self._auto_increment_version = False
        self.path = None
        self.type = None
        self._base_path = None

    def _to_rest_object(self):
        return SimpleNamespace()


def _make_model_operations(all_operations=None, registry_name=None):
    operation_scope = OperationScope('sub', 'rg', 'ws', registry_name=registry_name)
    operation_scope._workspace_location = None
    operation_scope._workspace_id = None
    operation_config = OperationConfig(show_progress=False, enable_telemetry=False)
    service_client = SimpleNamespace(
        model_versions=MagicMock(),
        model_containers=MagicMock(),
        workspaces=SimpleNamespace(get=MagicMock(return_value=SimpleNamespace(workspace_id='workspace-guid', location='eastus'))),
        resource_management_asset_reference=SimpleNamespace(begin_import_method=MagicMock()),
        _config=SimpleNamespace(credential=None),
    )
    datastore_operations = MagicMock()
    return ModelOperations(
        operation_scope,
        operation_config,
        service_client,
        datastore_operations,
        all_operations=all_operations,
        workspace_rg='rg',
        workspace_sub='sub',
    )


class _DummyPackageRequest:
    def __init__(self, env_version):
        self.inferencing_server = SimpleNamespace()
        self.base_environment_source = None
        self.target_environment_id = 'base-env'
        self.environment_version = env_version
        self._base_path = '.'

    def _to_rest_object(self):
        return self


def PackageResponse(target_environment_id):
    return type('PackageResponse', (), {'target_environment_id': target_environment_id})()


class _DummyWorkspaceOperation:
    def get(self, name):
        return SimpleNamespace(location='eastus', _workspace_id='workspace-id')


class _DummyEnvironmentOperation:
    def __init__(self):
        self.calls = []

    def get(self, name, version):
        self.calls.append((name, version))
        return f'env-{name}-{version}'


def _make_all_operations():
    return SimpleNamespace(all_operations={
        'workspaces': _DummyWorkspaceOperation(),
        AzureMLResourceType.ENVIRONMENT: _DummyEnvironmentOperation(),
    })


class _DummyOrchestrator:
    def __init__(self, operation_container, operation_scope, operation_config):
        self.operation_container = operation_container
        self.operation_scope = operation_scope
        self.operation_config = operation_config


def test_create_or_update_rejects_evaluator_request(monkeypatch):
    ops = _make_model_operations()
    model = _DummyModel('m', {'kind': 'evaluator'})
    monkeypatch.setattr(model_module, '_is_evaluator', lambda props: True)
    with pytest.raises(ValidationException) as exc_info:
        ops.create_or_update(model)
    assert 'Unable to create the evaluator' in str(exc_info.value)


def test_create_or_update_rejects_mismatched_evaluator_flags(monkeypatch):
    ops = _make_model_operations()
    model = _DummyModel('mismatch', {'kind': 'regular'})
    monkeypatch.setattr(model_module, '_is_evaluator', lambda props=None: bool(props and props.get('kind') == 'evaluator'))
    ops._get_model_properties = MagicMock(return_value={'kind': 'evaluator'})
    with pytest.raises(ValidationException) as exc_info:
        ops.create_or_update(model)
    assert 'Unable to create the model with name mismatch' in str(exc_info.value)


def test_get_requires_version_and_label_are_exclusive():
    ops = _make_model_operations()
    with pytest.raises(ValidationException) as exc_info:
        ops.get('name', version='1', label='latest')
    assert 'Cannot specify both version and label.' in str(exc_info.value)


def test_get_requires_version_or_label():
    ops = _make_model_operations()
    with pytest.raises(ValidationException) as exc_info:
        ops.get('name')
    assert 'Must provide either version or label' in str(exc_info.value)


def test_get_resolves_label(monkeypatch):
    ops = _make_model_operations()
    resolver = MagicMock(return_value='resolved-model')
    monkeypatch.setattr(model_module, '_resolve_label_to_asset', resolver)
    result = ops.get('name', label='latest')
    assert result == 'resolved-model'
    resolver.assert_called_once_with(ops, 'name', 'latest')


def test_package_returns_package_out_when_skip_to_rest():
    ops = _make_model_operations()
    package_request = _DummyPackageRequest('1')
    package_out = PackageResponse(target_environment_id='env-id')
    begin_mock = MagicMock()
    begin_mock.return_value.result.return_value = package_out
    ops._model_versions_operation.begin_package = begin_mock
    result = ops.package('model', '1', package_request, skip_to_rest=True)
    assert result is package_out
    begin_mock.assert_called_once()


def test_package_resolves_environment_with_regex(monkeypatch):
    monkeypatch.setattr(model_module, 'OperationOrchestrator', _DummyOrchestrator)
    all_ops = _make_all_operations()
    ops = _make_model_operations(all_operations=all_ops)
    package_request = _DummyPackageRequest('5')
    package_out = PackageResponse(target_environment_id='azureml://locations/e/workspaces/w/environments/env/versions/5')
    begin_mock = MagicMock()
    begin_mock.return_value.result.return_value = package_out
    ops._model_versions_operation.begin_package = begin_mock
    result = ops.package('model', '1', package_request)
    assert result == 'env-env-5'
    env_operation = all_ops.all_operations[AzureMLResourceType.ENVIRONMENT]
    assert env_operation.calls == [('env', '5')]


def test_package_parses_arm_id_when_regex_missing(monkeypatch):
    monkeypatch.setattr(model_module, 'OperationOrchestrator', _DummyOrchestrator)
    monkeypatch.setattr(model_module, 'AMLVersionedArmId', lambda arm_id: SimpleNamespace(asset_name='arm-id', asset_version='7'))
    all_ops = _make_all_operations()
    ops = _make_model_operations(all_operations=all_ops)
    package_request = _DummyPackageRequest('5')
    package_out = PackageResponse(target_environment_id='fallback-id')
    package_out.additional_properties = {'targetEnvironmentId': 'azureml://locations/e/workspaces/w/environments/arm/versions/not-a-number'}
    begin_mock = MagicMock()
    begin_mock.return_value.result.return_value = package_out
    ops._model_versions_operation.begin_package = begin_mock
    result = ops.package('model', '1', package_request)
    assert result == 'env-arm-id-7'
    env_operation = all_ops.all_operations[AzureMLResourceType.ENVIRONMENT]
    assert env_operation.calls == [('arm-id', '7')]


def test_share_calls_create_or_update_with_workspace_asset_reference():
    operation_scope = OperationScope(
        subscription_id="sub",
        resource_group_name="rg",
        workspace_name="workspace-name",
    )
    operation_config = OperationConfig(show_progress=False, enable_telemetry=False)
    service_client = MagicMock()
    service_client.model_versions = MagicMock()
    service_client.model_containers = MagicMock()
    workspace_details = MagicMock(workspace_id="guid-123", location="eastus")
    service_client.workspaces.get.return_value = workspace_details
    datastore_operations = MagicMock()
    model_ops = ModelOperations(
        operation_scope=operation_scope,
        operation_config=operation_config,
        service_client=service_client,
        datastore_operations=datastore_operations,
    )
    expected_model = MagicMock()
    model_ops.create_or_update = MagicMock(return_value=expected_model)

    @contextmanager
    def dummy_registry_client(registry_name):
        yield

    model_ops._set_registry_client = dummy_registry_client

    result = model_ops.share(
        name="model-name",
        version="1",
        share_with_name="shared-name",
        share_with_version="2",
        registry_name="dest-registry",
    )

    assert result == expected_model
    service_client.workspaces.get.assert_called_once_with(
        resource_group_name="rg", workspace_name="workspace-name"
    )
    created_asset = model_ops.create_or_update.call_args[0][0]
    assert isinstance(created_asset, WorkspaceAssetReference)
    assert created_asset.name == "shared-name"
    assert created_asset.version == "2"
    expected_asset_id = ASSET_ID_FORMAT.format(
        workspace_details.location,
        workspace_details.workspace_id,
        AzureMLResourceType.MODEL,
        "model-name",
        "1",
    )
    assert created_asset.asset_id == expected_asset_id


def test_package_parses_target_environment_id_pattern_and_resolves_environment():
    operation_scope = OperationScope(
        subscription_id="sub",
        resource_group_name="rg",
        workspace_name="workspace",
        workspace_id="workspace-id",
        workspace_location="location",
    )
    operation_config = OperationConfig(show_progress=False, enable_telemetry=False)
    service_client = MagicMock()
    service_client.model_versions = MagicMock()
    service_client.model_containers = MagicMock()
    datastore_operations = MagicMock()
    environment_operation = MagicMock()
    expected_environment = MagicMock(spec=Environment)
    environment_operation.get.return_value = expected_environment
    operations_container = OperationsContainer()
    operations_container.add(AzureMLResourceType.ENVIRONMENT, environment_operation)
    model_ops = ModelOperations(
        operation_scope=operation_scope,
        operation_config=operation_config,
        service_client=service_client,
        datastore_operations=datastore_operations,
        all_operations=operations_container,
    )
    package_request = MagicMock(spec=ModelPackage)
    package_request.inferencing_server = MagicMock(code_configuration=None)
    package_request.base_environment_source = None
    package_request.target_environment_id = "target-environment"
    package_request.environment_version = "1"
    package_request._base_path = "base"
    rest_package_request = MagicMock()
    rest_package_request.target_environment_id = "azureml://locations/location/workspaces/workspace-id/environments/parsed-env/versions/5"
    package_request._to_rest_object.return_value = rest_package_request
    package_out = type("PackageResponse", (), {})()
    package_out.target_environment_id = rest_package_request.target_environment_id
    begin_package_result = MagicMock()
    begin_package_result.result.return_value = package_out
    model_ops._model_versions_operation.begin_package.return_value = begin_package_result

    result = model_ops.package("mymodel", "v1", package_request)

    assert result == expected_environment
    environment_operation.get.assert_called_once_with(name="parsed-env", version="5")


def test_package_handles_registry_package_response_and_control_plane_fetch(monkeypatch):
    operation_scope = OperationScope(
        subscription_id="sub-a",
        resource_group_name="original-rg",
        workspace_name="workspace",
        registry_name="registry-target",
        workspace_id="workspace-id",
        workspace_location="location",
    )
    operation_config = OperationConfig(show_progress=False, enable_telemetry=False)
    service_client = MagicMock()
    service_client.model_versions = MagicMock()
    service_client.model_containers = MagicMock()
    datastore_operations = MagicMock()
    control_plane_client = MagicMock()
    control_plane_client._config = MagicMock()
    control_plane_client._config.subscription_id = "original-sub"
    env_rest = MagicMock()
    control_plane_client.environment_versions.get.return_value = env_rest
    expected_environment = MagicMock()
    monkeypatch.setattr(
        "azure.ai.ml.operations._model_operations.Environment._from_rest_object",
        lambda rest: expected_environment,
    )
    model_ops = ModelOperations(
        operation_scope=operation_scope,
        operation_config=operation_config,
        service_client=service_client,
        datastore_operations=datastore_operations,
        control_plane_client=control_plane_client,
        workspace_rg="fetched-rg",
        workspace_sub="fetched-sub",
    )
    package_request = MagicMock(spec=ModelPackage)
    package_request.inferencing_server = MagicMock(code_configuration=None)
    package_request.base_environment_source = None
    package_request.target_environment_id = "target-env"
    package_request.environment_version = "2"
    package_request._base_path = "base"
    rest_package_request = MagicMock()
    rest_package_request.target_environment_id = "azureml://locations/location/workspaces/workspace-id/environments/target-env/versions/2"
    package_request._to_rest_object.return_value = rest_package_request
    class PackageResponse:
        pass
    package_out = PackageResponse()
    package_out.additional_properties = {"targetEnvironmentId": "fallback-id"}
    begin_package_result = MagicMock()
    begin_package_result.result.return_value = package_out
    model_ops._model_versions_operation.begin_package.return_value = begin_package_result

    class FakeArmId:
        def __init__(self, arm_id):
            self.asset_name = "fallback-env"
            self.asset_version = "42"

    monkeypatch.setattr(
        "azure.ai.ml.operations._model_operations.AMLVersionedArmId",
        FakeArmId,
    )

    result = model_ops.package("mymodel", "v1", package_request)

    assert result == expected_environment
    control_plane_client.environment_versions.get.assert_called_once_with(
        name="fallback-env",
        version="42",
        workspace_name="workspace",
        **{
            "resource_group_name": "fetched-rg",
        },
    )
    assert control_plane_client._config.subscription_id == "fetched-sub"
    assert model_ops._scope_kwargs["resource_group_name"] == "original-rg"


class FakeOperationOrchestrator:
    def __init__(self, operation_container, operation_scope, operation_config):
        self.operation_container = operation_container
        self.operation_scope = operation_scope
        self.operation_config = operation_config

    def get_asset_arm_id(self, *args, **kwargs):
        return "asset-id"


class FakeModelPackage:
    def __init__(self, target_environment_id, environment_version):
        self.inferencing_server = SimpleNamespace(code_configuration=None)
        self.base_environment_source = None
        self._base_path = None
        self.target_environment_id = target_environment_id
        self.environment_version = environment_version

    def _to_rest_object(self):
        return self


class FakePoller:
    def __init__(self, result):
        self._result = result

    def result(self):
        return self._result


class FakeModelVersionsOperation:
    def __init__(self, package_out):
        self.package_out = package_out

    def begin_package(self, **kwargs):
        return FakePoller(self.package_out)


class PackageResponse:
    def __init__(self, target_environment_id):
        self.target_environment_id = target_environment_id


@pytest.fixture(autouse=True)
def patch_operation_orchestrator(monkeypatch):
    monkeypatch.setattr("azure.ai.ml.operations._model_operations.OperationOrchestrator", FakeOperationOrchestrator)


def test_package_response_registry_branch_retrieves_environment(monkeypatch):
    monkeypatch.setattr(Environment, "_from_rest_object", lambda rest_obj: "control_plane_environment")
    package_out = PackageResponse(
        "azureml://locations/eastus/workspaces/ws-id/environments/pkg-env/versions/2"
    )
    fake_model_versions = FakeModelVersionsOperation(package_out)
    service_client = SimpleNamespace(
        model_versions=fake_model_versions,
        model_containers=SimpleNamespace(),
        _config=SimpleNamespace(credential="credential"),
    )
    operation_scope = OperationScope(
        subscription_id="sub_id",
        resource_group_name="resource_group",
        workspace_name="workspace",
        registry_name="registry",
        workspace_id="ws-id",
        workspace_location="eastus",
    )
    operation_config = OperationConfig(show_progress=False, enable_telemetry=False)
    control_plane_client = SimpleNamespace(
        _config=SimpleNamespace(subscription_id="original"),
        environment_versions=SimpleNamespace(
            get=lambda name, version, workspace_name, **kwargs: "control_plane_rest"
        ),
    )
    model_operations = ModelOperations(
        operation_scope=operation_scope,
        operation_config=operation_config,
        service_client=service_client,
        datastore_operations=object(),
        all_operations=OperationsContainer(),
        control_plane_client=control_plane_client,
        workspace_rg="workspace_rg",
        workspace_sub="workspace_sub",
    )
    fake_package = FakeModelPackage(target_environment_id="pkg-env", environment_version="2")
    result = model_operations.package(
        name="model",
        version="1",
        package_request=fake_package,
    )
    assert result == "control_plane_environment"
    assert model_operations._scope_kwargs["resource_group_name"] == "resource_group"
    assert control_plane_client._config.subscription_id == "workspace_sub"


def test_package_response_workspace_branch_uses_environment_operation():
    package_out = PackageResponse(
        "azureml://locations/north/workspaces/ws-id/environments/pkg-env/versions/3"
    )
    fake_model_versions = FakeModelVersionsOperation(package_out)
    service_client = SimpleNamespace(
        model_versions=fake_model_versions,
        model_containers=SimpleNamespace(),
        _config=SimpleNamespace(credential="credential"),
    )
    operation_scope = OperationScope(
        subscription_id="sub_id",
        resource_group_name="resource_group",
        workspace_name="workspace",
        workspace_id="ws-id",
        workspace_location="north",
    )
    operation_config = OperationConfig(show_progress=False, enable_telemetry=False)
    operations_container = OperationsContainer()
    fake_environment_operation = SimpleNamespace(get=Mock(return_value="workspace_environment"))
    operations_container.all_operations[AzureMLResourceType.ENVIRONMENT] = fake_environment_operation
    model_operations = ModelOperations(
        operation_scope=operation_scope,
        operation_config=operation_config,
        service_client=service_client,
        datastore_operations=object(),
        all_operations=operations_container,
    )
    fake_package = FakeModelPackage(target_environment_id="pkg-env", environment_version="3")
    result = model_operations.package(
        name="model",
        version="1",
        package_request=fake_package,
    )
    assert result == "workspace_environment"
    fake_environment_operation.get.assert_called_once_with(name="pkg-env", version="3")
