import os
import tempfile
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import azure.ai.ml.operations._batch_endpoint_operations as batch_endpoint_module
from azure.ai.ml.constants._common import AzureMLResourceType, AssetTypes, InputTypes, AZUREML_REGEX_FORMAT, SHORT_URI_REGEX_FORMAT
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException, ValidationException, ValidationErrorType
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, OperationsContainer
import types


def _build_operations(batch_endpoints=None, batch_deployments=None):
    operation_scope = OperationScope('sub', 'rg', 'workspace')
    operation_config = OperationConfig(False, False)
    workspace_operations = MagicMock()
    workspace_operations.get.return_value = SimpleNamespace(location='eastus')
    container = OperationsContainer()
    container.add(AzureMLResourceType.WORKSPACE, workspace_operations)
    container.add(AzureMLResourceType.DATASTORE, MagicMock())
    if batch_endpoints is None:
        batch_endpoints = MagicMock()
    if batch_deployments is None:
        batch_deployments = MagicMock()
        batch_deployments.list.return_value = []
    service_client = SimpleNamespace(
        batch_endpoints=batch_endpoints,
        batch_deployments=batch_deployments,
    )
    requests_pipeline = MagicMock()
    return (
        batch_endpoint_module.BatchEndpointOperations(
            operation_scope,
            operation_config,
            service_client,
            container,
            credentials=None,
            service_client_09_2020_dataplanepreview=SimpleNamespace(batch_job_endpoint=MagicMock()),
            requests_pipeline=requests_pipeline,
        ),
        batch_endpoints,
        batch_deployments,
    )


class _FakeBatchEndpoint:
    def __init__(self):
        self.name = 'endpoint'

    def _to_rest_batch_endpoint(self, location):
        return {'location': location}


def test_begin_create_or_update_logs_validation_error(monkeypatch):
    ops, batch_endpoints, _ = _build_operations()
    validation_exception = ValidationException(
        message='validation failed',
        no_personal_data_message='validation failed',
        target=ErrorTarget.BATCH_ENDPOINT,
        error_category=ErrorCategory.USER_ERROR,
        error_type=ValidationErrorType.INVALID_VALUE,
    )
    batch_endpoints.begin_create_or_update.side_effect = validation_exception

    captured = {}

    def fake_log_and_raise_error(exc):
        captured['called'] = True
        raise exc

    monkeypatch.setattr(batch_endpoint_module, 'log_and_raise_error', fake_log_and_raise_error)

    with pytest.raises(ValidationException) as excinfo:
        ops.begin_create_or_update(_FakeBatchEndpoint())

    assert captured.get('called', False) is True
    assert excinfo.value is validation_exception


def test_resolve_input_empty_path_raises(monkeypatch):
    ops, _, _ = _build_operations()

    class DummyInput:
        def __init__(self, path, type):
            self.path = path
            self.type = type

    monkeypatch.setattr(batch_endpoint_module, 'Input', DummyInput)

    entry = batch_endpoint_module.Input(path='', type=AssetTypes.URI_FILE)

    with pytest.raises(MlException) as excinfo:
        ops._resolve_input(entry, os.getcwd())

    assert "Input path can't be empty for batch endpoint invoke" in str(excinfo.value)


def test_resolve_input_numeric_type_returns(monkeypatch):
    ops, _, _ = _build_operations()

    class DummyInput:
        def __init__(self, path, type):
            self.path = path
            self.type = type

    monkeypatch.setattr(batch_endpoint_module, 'Input', DummyInput)

    entry = batch_endpoint_module.Input(path='1', type=InputTypes.NUMBER)

    assert ops._resolve_input(entry, os.getcwd()) is None


def test_resolve_input_absolute_folder_appends_slash(monkeypatch):
    class DummyInput:
        def __init__(self, path, type):
            self.path = path
            self.type = type

    monkeypatch.setattr(batch_endpoint_module, 'Input', DummyInput)
    monkeypatch.setattr(
        batch_endpoint_module.BatchEndpointOperations,
        '_datastore_operations',
        property(lambda self: MagicMock()),
    )

    def fake_upload(scope, datastore, path):
        return 'https://mystorage/folder'

    monkeypatch.setattr(batch_endpoint_module, '_upload_and_generate_remote_uri', fake_upload)

    with tempfile.TemporaryDirectory() as tmp_dir:
        ops, _, _ = _build_operations()
        entry = batch_endpoint_module.Input(path=tmp_dir, type=AssetTypes.URI_FOLDER)
        ops._resolve_input(entry, os.getcwd())
        assert entry.path == 'https://mystorage/folder/'


def test_resolve_input_relative_path_transforms_to_validation_error(monkeypatch):
    class DummyInput:
        def __init__(self, path, type):
            self.path = path
            self.type = type

    monkeypatch.setattr(batch_endpoint_module, 'Input', DummyInput)
    monkeypatch.setattr(
        batch_endpoint_module.BatchEndpointOperations,
        '_datastore_operations',
        property(lambda self: MagicMock()),
    )

    def fake_upload(*args, **kwargs):
        raise RuntimeError('boom')

    monkeypatch.setattr(batch_endpoint_module, '_upload_and_generate_remote_uri', fake_upload)

    ops, _, _ = _build_operations()

    entry = batch_endpoint_module.Input(path='relative/path', type=AssetTypes.URI_FOLDER)

    with pytest.raises(ValidationException) as excinfo:
        ops._resolve_input(entry, os.getcwd())

    exception_text = str(excinfo.value)
    assert 'RuntimeError' in exception_text
    assert 'boom' in exception_text
    assert 'Supported input path value are' in exception_text


def _make_batch_endpoint_operations():
    operations = batch_endpoint_module.BatchEndpointOperations.__new__(batch_endpoint_module.BatchEndpointOperations)
    operations._operation_scope = object()
    operations._operation_config = object()
    operations._all_operations = types.SimpleNamespace(
        all_operations={AzureMLResourceType.DATASTORE: object()}
    )
    return operations


def test_resolve_input_registered_short_uri_returns(monkeypatch):
    operations = _make_batch_endpoint_operations()
    entry = Input(path="dummy:short", type=AssetTypes.URI_FILE)
    original_path = entry.path

    def fake_match(pattern, string, *args, **kwargs):
        if pattern == batch_endpoint_module.SHORT_URI_REGEX_FORMAT:
            return object()
        return None

    monkeypatch.setattr(batch_endpoint_module.re, "match", fake_match)
    monkeypatch.setattr(batch_endpoint_module, "is_private_preview_enabled", lambda: False)

    operations._resolve_input(entry, ".")
    assert entry.path == original_path


def test_resolve_input_registered_private_preview_returns(monkeypatch):
    operations = _make_batch_endpoint_operations()
    entry = Input(path="prefix@resource", type=AssetTypes.URI_FILE)
    original_path = entry.path

    def fake_match(pattern, string, *args, **kwargs):
        if pattern == batch_endpoint_module.AZUREML_REGEX_FORMAT:
            return object()
        return None

    monkeypatch.setattr(batch_endpoint_module.re, "match", fake_match)
    monkeypatch.setattr(batch_endpoint_module, "is_private_preview_enabled", lambda: True)

    operations._resolve_input(entry, ".")
    assert entry.path == original_path


def test_resolve_input_registered_datastore_path_uses_orchestrator(monkeypatch):
    operations = _make_batch_endpoint_operations()
    entry = Input(path="registry:asset", type=AssetTypes.URI_FILE)

    monkeypatch.setattr(batch_endpoint_module.re, "match", lambda *args, **kwargs: None)
    monkeypatch.setattr(batch_endpoint_module, "is_private_preview_enabled", lambda: False)
    monkeypatch.setattr(batch_endpoint_module, "remove_aml_prefix", lambda value: value.replace("registry:", ""))

    class _FakeOperationOrchestrator:
        def __init__(self, all_operations, operation_scope, operation_config):
            self.all_operations = all_operations
            self.operation_scope = operation_scope
            self.operation_config = operation_config

        def get_asset_arm_id(self, path, asset_type):
            assert asset_type == AzureMLResourceType.DATA
            return f"arm://{path}"

    monkeypatch.setattr(batch_endpoint_module, "OperationOrchestrator", _FakeOperationOrchestrator)

    operations._resolve_input(entry, ".")
    assert entry.path == "arm://asset"


def test_resolve_input_relative_path_uploads_folder_suffix(monkeypatch, tmp_path):
    operations = _make_batch_endpoint_operations()
    entry = Input(path="folder", type=AssetTypes.URI_FOLDER)

    monkeypatch.setattr(
        batch_endpoint_module,
        "_upload_and_generate_remote_uri",
        lambda scope, datastore_ops, path: "https://storage/container",
    )

    operations._resolve_input(entry, str(tmp_path))
    assert entry.path == "https://storage/container/"


def test_resolve_input_relative_path_validation_exception(monkeypatch, tmp_path):
    operations = _make_batch_endpoint_operations()
    entry = Input(path="folder", type=AssetTypes.URI_FILE)

    def raising(*args, **kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(batch_endpoint_module, "_upload_and_generate_remote_uri", raising)

    with pytest.raises(ValidationException) as exc_info:
        operations._resolve_input(entry, str(tmp_path))

    assert exc_info.value.error_type == ValidationErrorType.INVALID_VALUE


def test_resolve_input_relative_path_ml_exception_is_propagated(monkeypatch, tmp_path):
    operations = _make_batch_endpoint_operations()
    entry = Input(path="folder", type=AssetTypes.URI_FILE)

    def raising(*args, **kwargs):
        raise MlException(
            message="fail",
            no_personal_data_message="fail",
            target=ErrorTarget.BATCH_ENDPOINT,
        )

    monkeypatch.setattr(batch_endpoint_module, "_upload_and_generate_remote_uri", raising)

    with pytest.raises(MlException):
        operations._resolve_input(entry, str(tmp_path))


def _make_operations():
    operations, _, _ = _build_operations()
    return operations


def test_resolve_input_short_uri_skips_upload():
    operations = _make_operations()
    entry = Input(path='datastore:/artifact', type=AssetTypes.URI_FOLDER)

    def fake_match(pattern, string):
        if pattern == SHORT_URI_REGEX_FORMAT and string == entry.path:
            return object()
        return None

    with patch('azure.ai.ml.operations._batch_endpoint_operations.re.match', side_effect=fake_match):
        operations._resolve_input(entry, base_path='.')
    assert entry.path == 'datastore:/artifact'


def test_resolve_input_private_preview_short_circuits():
    operations = _make_operations()
    entry = Input(path='@private/asset', type=AssetTypes.URI_FOLDER)

    def fake_match(pattern, string):
        if pattern == AZUREML_REGEX_FORMAT:
            return object()
        return None

    with patch('azure.ai.ml.operations._batch_endpoint_operations.re.match', side_effect=fake_match):
        with patch(
            'azure.ai.ml.operations._batch_endpoint_operations.is_private_preview_enabled', return_value=True
        ):
            operations._resolve_input(entry, base_path='.')
    assert entry.path == '@private/asset'


def test_resolve_input_registered_datastore_converts_to_arm_id():
    operations = _make_operations()
    entry = Input(path='datastore:asset', type=AssetTypes.URI_FOLDER)
    orchestrator_instance = MagicMock()
    orchestrator_instance.get_asset_arm_id.return_value = 'arm://asset'

    def fake_match(pattern, string):
        return None

    with patch('azure.ai.ml.operations._batch_endpoint_operations.re.match', side_effect=fake_match):
        with patch(
            'azure.ai.ml.operations._batch_endpoint_operations.is_private_preview_enabled', return_value=False
        ):
            with patch(
                'azure.ai.ml.operations._batch_endpoint_operations.remove_aml_prefix', return_value='asset'
            ):
                with patch(
                    'azure.ai.ml.operations._batch_endpoint_operations.OperationOrchestrator',
                    return_value=orchestrator_instance,
                ):
                    operations._resolve_input(entry, base_path='.')
    orchestrator_instance.get_asset_arm_id.assert_called_once_with('asset', AzureMLResourceType.DATA)
    assert entry.path == 'arm://asset'


def test_resolve_input_relative_path_uploads_and_appends_slash():
    operations = _make_operations()
    entry = Input(path='relative/folder', type=AssetTypes.URI_FOLDER)
    with patch(
        'azure.ai.ml.operations._batch_endpoint_operations._upload_and_generate_remote_uri',
        return_value='https://upload/result',
    ):
        operations._resolve_input(entry, base_path='.')
    assert entry.path == 'https://upload/result/'


def test_resolve_input_relative_path_upload_error_wraps_validation_exception():
    operations = _make_operations()
    entry = Input(path='relative/folder', type=AssetTypes.URI_FOLDER)

    def raise_error(*args, **kwargs):
        raise RuntimeError('boom')

    with patch(
        'azure.ai.ml.operations._batch_endpoint_operations._upload_and_generate_remote_uri',
        side_effect=raise_error,
    ):
        with pytest.raises(ValidationException) as exc_info:
            operations._resolve_input(entry, base_path='.')
    assert 'RuntimeError' in str(exc_info.value)


class DummyInput:
    def __init__(self, path, type):
        self.path = path
        self.type = type


class FakeRe:
    def __init__(self, matcher):
        self._matcher = matcher

    def match(self, pattern, string):
        return self._matcher(pattern, string)


from azure.ai.ml.operations._batch_endpoint_operations import BatchEndpointOperations


def _make_batch_operations():
    service_client_10 = MagicMock()
    service_client_10.batch_endpoints = MagicMock()
    service_client_10.batch_deployments = MagicMock()
    service_client_09 = MagicMock()
    service_client_09.batch_job_endpoint = MagicMock()
    requests_pipeline = MagicMock()
    operation_scope = OperationScope("sub", "rg", "ws")
    operation_config = OperationConfig(False, False)
    container = OperationsContainer()
    container.add(AzureMLResourceType.DATASTORE, MagicMock())
    container.add(AzureMLResourceType.WORKSPACE, MagicMock())
    return BatchEndpointOperations(
        operation_scope,
        operation_config,
        service_client_10,
        container,
        requests_pipeline=requests_pipeline,
        service_client_09_2020_dataplanepreview=service_client_09,
    )


def test_resolve_input_short_uri_skips_operations(monkeypatch):
    operations = _make_batch_operations()
    monkeypatch.setattr(batch_endpoint_module, "Input", DummyInput)
    matcher = lambda pattern, string: pattern == batch_endpoint_module.SHORT_URI_REGEX_FORMAT
    monkeypatch.setattr(batch_endpoint_module, "re", FakeRe(matcher))
    entry = DummyInput("short:data", "uri_file")
    operations._resolve_input(entry, base_path=".")
    assert entry.path == "short:data"


def test_resolve_input_long_uri_skips_operations(monkeypatch):
    operations = _make_batch_operations()
    monkeypatch.setattr(batch_endpoint_module, "Input", DummyInput)
    matcher = lambda pattern, string: pattern == batch_endpoint_module.LONG_URI_REGEX_FORMAT
    monkeypatch.setattr(batch_endpoint_module, "re", FakeRe(matcher))
    entry = DummyInput("long:data", "uri_folder")
    operations._resolve_input(entry, base_path=".")
    assert entry.path == "long:data"


def test_resolve_input_private_preview_short_circuits(monkeypatch):
    operations = _make_batch_operations()
    monkeypatch.setattr(batch_endpoint_module, "Input", DummyInput)
    monkeypatch.setattr(batch_endpoint_module, "is_private_preview_enabled", lambda: True)

    def matcher(pattern, string):
        return pattern == batch_endpoint_module.AZUREML_REGEX_FORMAT

    monkeypatch.setattr(batch_endpoint_module, "re", FakeRe(matcher))
    entry = DummyInput("preview:data", "uri_folder")
    operations._resolve_input(entry, base_path=".")
    assert entry.path == "preview:data"


def test_resolve_input_datastore_registered_asset(monkeypatch):
    operations = _make_batch_operations()
    monkeypatch.setattr(batch_endpoint_module, "Input", DummyInput)
    monkeypatch.setattr(batch_endpoint_module, "re", FakeRe(lambda pattern, string: False))
    monkeypatch.setattr(batch_endpoint_module, "is_private_preview_enabled", lambda: False)
    monkeypatch.setattr(batch_endpoint_module, "remove_aml_prefix", lambda value: value.replace("azureml://", ""))

    class DummyOrchestrator:
        def __init__(self, all_operations, operation_scope, operation_config):
            self.calls = (all_operations, operation_scope, operation_config)

        def get_asset_arm_id(self, path, asset_type):
            return f"arm_id://{path}"

    monkeypatch.setattr(batch_endpoint_module, "OperationOrchestrator", DummyOrchestrator)
    entry = DummyInput("azureml://datastore/asset", "uri_folder")
    operations._resolve_input(entry, base_path=".")
    assert entry.path == "arm_id://datastore/asset"


def test_resolve_input_relative_folder_upload(monkeypatch, tmp_path):
    operations = _make_batch_operations()
    monkeypatch.setattr(batch_endpoint_module, "Input", DummyInput)
    monkeypatch.setattr(batch_endpoint_module, "re", FakeRe(lambda pattern, string: False))

    def fake_upload(scope, datastore_ops, path):
        return "https://storage/location"

    monkeypatch.setattr(batch_endpoint_module, "_upload_and_generate_remote_uri", fake_upload)
    entry = DummyInput("relative/path", AssetTypes.URI_FOLDER)
    operations._resolve_input(entry, base_path=str(tmp_path))
    assert entry.path == "https://storage/location/"


def test_resolve_input_relative_upload_raises_validation(monkeypatch, tmp_path):
    operations = _make_batch_operations()
    monkeypatch.setattr(batch_endpoint_module, "Input", DummyInput)
    monkeypatch.setattr(batch_endpoint_module, "re", FakeRe(lambda pattern, string: False))

    def raising_upload(*args, **kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(batch_endpoint_module, "_upload_and_generate_remote_uri", raising_upload)
    entry = DummyInput("relative/error", "uri_folder")
    with pytest.raises(ValidationException) as excinfo:
        operations._resolve_input(entry, base_path=str(tmp_path))
    assert "ValueError" in str(excinfo.value)
    assert "Met" in str(excinfo.value)
