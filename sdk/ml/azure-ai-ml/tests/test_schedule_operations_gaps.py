import types
from types import SimpleNamespace
import pytest

from azure.ai.ml.constants._monitoring import (
    DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY,
    DEPLOYMENT_MODEL_INPUTS_NAME_KEY,
    DEPLOYMENT_MODEL_INPUTS_VERSION_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY,
    DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY,
    MonitorDatasetContext,
)
from azure.ai.ml.entities._inputs_outputs.input import Input
from azure.ai.ml.entities._monitoring.signals import BaselineDataRange, ReferenceData
from azure.ai.ml.operations._schedule_operations import (
    ScheduleOperations,
    ARM_ID_PREFIX,
    AZUREML_RESOURCE_PROVIDER,
    NAMED_RESOURCE_ID_FORMAT_WITH_PARENT,
    AzureMLResourceType,
    MonitorSignalType,
    ScheduleException,
)
from azure.ai.ml.operations import _schedule_operations as schedule_module
from azure.ai.ml.entities import MonitoringTarget
from azure.ai.ml._scope_dependent_operations import OperationScope, OperationConfig


class DummyTarget:
    def __init__(self, endpoint_deployment_id=None, model_id=None):
        self.endpoint_deployment_id = endpoint_deployment_id
        self.model_id = model_id


default_monitor_called = False


class DummyCreateMonitor:
    def __init__(self, monitoring_target, monitoring_signals):
        self.monitoring_target = monitoring_target
        self.monitoring_signals = monitoring_signals


class DummySchedule:
    def __init__(
        self,
        create_monitor=None,
        base_path='.',
        signals=None,
        target=None,
    ):
        if create_monitor is not None:
            self.create_monitor = create_monitor
            self._base_path = base_path
        else:
            if target is None:
                target = DummyTarget()
            self.create_monitor = DummyCreateMonitor(target, signals)
            self._base_path = 'base/path'
        self.default_monitor_called = False
        self.default_created = False

    def _create_default_monitor_definition(self):
        self.default_monitor_called = True
        self.default_created = True


class DummyJobOperations:
    def __init__(self):
        self.resolved_inputs = []
        self.resolved_inputs_multi = []

    def _resolve_job_input(self, input_data, base_path):
        self.resolved_inputs.append(('single', input_data, base_path))

    def _resolve_job_inputs(self, inputs, base_path):
        self.resolved_inputs.append(('multiple', inputs, base_path))
        self.resolved_inputs_multi.append(list(inputs))


class DummyDataAsset:
    def __init__(self, asset_type='dummy_type'):
        self.type = asset_type


class DummyDataOperations:
    def __init__(self, asset_type='dummy_type'):
        self.asset_type = asset_type
        self.assets = {}

    def register(self, name, version, type='uri_folder'):
        self.assets[(name, version)] = DummyDataAsset(type)

    def get(self, name, version=None):  # pylint:disable=unused-argument
        if self.assets and (name, version) in self.assets:
            return self.assets[(name, version)]
        return DummyDataAsset(asset_type=self.asset_type)


class DummyCollectionEntry:
    def __init__(self, data, enabled):
        self.data = data
        self.enabled = enabled


class DummyDataCollector:
    def __init__(self, model_inputs_id=None, model_outputs_id=None, app_traces_id=None, collections=None):
        # Support both styles: either direct collections dict or individual ids
        if isinstance(model_inputs_id, dict) and model_outputs_id is None and collections is None:
            self.collections = model_inputs_id
            return
        if collections is not None:
            self.collections = collections
            return
        self.collections = {
            'model_inputs': DummyCollectionEntry(model_inputs_id, 'true'),
            'model_outputs': DummyCollectionEntry(model_outputs_id, 'true'),
        }
        if app_traces_id is not None:
            self.collections['app_traces'] = DummyCollectionEntry(app_traces_id, 'true')


class DummyOnlineDeployment:
    def __init__(self, data_collector=None, tags=None):
        self.data_collector = data_collector
        self.tags = tags or {}


class DummyOnlineDeploymentOperations:
    def __init__(self, deployment):
        self._deployment = deployment

    def get(self, deployment_name, endpoint_name):  # pylint:disable=unused-argument
        return self._deployment


class DummyOrchestrator:
    def __init__(self):
        self.calls = []
        self.assets = []

    def get_asset_arm_id(self, asset, azureml_type, register_asset=None):  # pylint:disable=unused-argument
        self.calls.append((asset, azureml_type, register_asset))
        self.assets.append(asset)
        return f'resolved:{asset}' if asset is not None else None


class DummyGenSignal:
    def __init__(self, signal_type, production_data=None, reference_data=None):
        self.type = signal_type
        self.production_data = production_data
        self.reference_data = reference_data


class DummyLlmData:
    def __init__(self, input_data, data_window):
        self.input_data = input_data
        self.data_window = data_window


class DummyBaselineDataRange:
    def __init__(self, lookback_window_size=None, lookback_window_offset=None):  # pylint:disable=unused-argument
        self.lookback_window_size = lookback_window_size
        self.lookback_window_offset = lookback_window_offset


class DummyInput:
    def __init__(self, path=None, type=None):  # pylint:disable=redefined-builtin
        self.path = path
        self.type = type


class DummyScheduleOperations(ScheduleOperations):
    '''Lightweight test subclass that bypasses the real constructor and
    exposes configurable private properties used by the tested methods.
    '''

    def __init__(self, subscription_id='sub-id', resource_group_name='rg-name', workspace_name='ws-name'):
        # Intentionally do not call super().__init__
        self._test_subscription_id = subscription_id
        self._test_resource_group_name = resource_group_name
        self._test_workspace_name = workspace_name
        self._test_online_deployment_operations = None
        self._test_job_operations = None
        self._test_data_operations = None
        self._orchestrators = None

    @property
    def _subscription_id(self):  # type: ignore[override]
        return self._test_subscription_id

    @property
    def _resource_group_name(self):  # type: ignore[override]
        return self._test_resource_group_name

    @property
    def _workspace_name(self):  # type: ignore[override]
        return self._test_workspace_name

    @property
    def _online_deployment_operations(self):  # type: ignore[override]
        return self._test_online_deployment_operations

    @_online_deployment_operations.setter
    def _online_deployment_operations(self, value):  # type: ignore[override]
        self._test_online_deployment_operations = value

    @property
    def _job_operations(self):  # type: ignore[override]
        return self._test_job_operations

    @_job_operations.setter
    def _job_operations(self, value):  # type: ignore[override]
        self._test_job_operations = value

    @property
    def _data_operations(self):  # type: ignore[override]
        return self._test_data_operations

    @_data_operations.setter
    def _data_operations(self, value):  # type: ignore[override]
        self._test_data_operations = value


def _create_schedule_ops_instance():
    return DummyScheduleOperations()


def test_process_and_get_endpoint_deployment_names_from_id_named_and_arm_paths(monkeypatch):
    ops = _create_schedule_ops_instance()

    # Non-ARM (named) path
    target_named = DummyTarget(endpoint_deployment_id=f'{ARM_ID_PREFIX}my-endpoint:my-deployment')

    def fake_is_arm(resource_id, parent_type, child_type):  # pylint:disable=unused-argument
        return False

    monkeypatch.setattr(schedule_module, 'is_ARM_id_for_parented_resource', fake_is_arm)

    endpoint_name, deployment_name = ops._process_and_get_endpoint_deployment_names_from_id(target_named)

    assert endpoint_name == 'my-endpoint'
    assert deployment_name == 'my-deployment'
    expected_arm = NAMED_RESOURCE_ID_FORMAT_WITH_PARENT.format(
        ops._subscription_id,
        ops._resource_group_name,
        AZUREML_RESOURCE_PROVIDER,
        ops._workspace_name,
        schedule_module.snake_to_camel(AzureMLResourceType.ONLINE_ENDPOINT),
        'my-endpoint',
        AzureMLResourceType.DEPLOYMENT,
        'my-deployment',
    )
    assert target_named.endpoint_deployment_id == expected_arm

    # ARM path
    arm_id_value = expected_arm

    def fake_is_arm_true(resource_id, parent_type, child_type):  # pylint:disable=unused-argument
        return True

    monkeypatch.setattr(schedule_module, 'is_ARM_id_for_parented_resource', fake_is_arm_true)

    class DummyAMLNamedArmId:
        def __init__(self, arm_id):  # pylint:disable=unused-argument
            self.parent_asset_name = 'parent-endpoint'
            self.asset_name = 'child-deployment'

    monkeypatch.setattr(schedule_module, 'AMLNamedArmId', DummyAMLNamedArmId)

    target_arm = DummyTarget(endpoint_deployment_id=arm_id_value)
    endpoint_name2, deployment_name2 = ops._process_and_get_endpoint_deployment_names_from_id(target_arm)

    assert endpoint_name2 == 'parent-endpoint'
    assert deployment_name2 == 'child-deployment'
    assert target_arm.endpoint_deployment_id == arm_id_value


def test_resolve_monitor_schedule_arm_id_generation_token_statistics_default_and_existing(monkeypatch):
    ops = _create_schedule_ops_instance()

    # Set up fake deployment with data collector and app_traces
    data_collector = DummyDataCollector(
        model_inputs_id='inputs-name:1',
        model_outputs_id='outputs-name:2',
        app_traces_id='traces-name:3',
    )
    deployment = DummyOnlineDeployment(data_collector=data_collector)
    ops._online_deployment_operations = DummyOnlineDeploymentOperations(deployment)
    job_ops = DummyJobOperations()
    ops._job_operations = job_ops
    data_ops = DummyDataOperations(asset_type='table')
    ops._data_operations = data_ops
    ops._orchestrators = DummyOrchestrator()

    # Monkeypatch monitoring-related classes to simple dummies
    monkeypatch.setattr(schedule_module, 'GenerationTokenStatisticsSignal', DummyGenSignal)
    monkeypatch.setattr(schedule_module, 'LlmData', DummyLlmData)
    monkeypatch.setattr(schedule_module, 'BaselineDataRange', DummyBaselineDataRange)
    monkeypatch.setattr(schedule_module, 'Input', DummyInput)

    # Also simplify AMLVersionedArmId to parse 'name:version'
    class DummyAMLVersionedArmId:
        def __init__(self, arm_id):
            name, version = arm_id.split(':')
            self.asset_name = name
            self.asset_version = version

    monkeypatch.setattr(schedule_module, 'AMLVersionedArmId', DummyAMLVersionedArmId)

    target = DummyTarget(endpoint_deployment_id=f'{ARM_ID_PREFIX}endpoint:deployment')

    # First signal: no production_data -> default created
    signal1 = DummyGenSignal(signal_type=MonitorSignalType.GENERATION_TOKEN_STATISTICS, production_data=None)

    # Second signal: has existing production_data -> path where default not created
    existing_input = DummyInput(path='existing', type='table')
    existing_llm_data = DummyLlmData(input_data=existing_input, data_window=None)
    signal2 = DummyGenSignal(
        signal_type=MonitorSignalType.GENERATION_TOKEN_STATISTICS,
        production_data=existing_llm_data,
    )

    monitoring_signals = {'sig1': signal1, 'sig2': signal2}
    create_monitor = DummyCreateMonitor(monitoring_target=target, monitoring_signals=monitoring_signals)
    schedule = DummySchedule(create_monitor=create_monitor)

    ops._resolve_monitor_schedule_arm_id(schedule)

    # signal1 should now have production_data created via DummyLlmData
    assert isinstance(signal1.production_data, DummyLlmData)
    assert isinstance(signal1.production_data.input_data, DummyInput)
    assert signal1.production_data.input_data.path.startswith('traces-name:3')

    # job_ops should have been called for both signals
    resolved_single_calls = [c for c in job_ops.resolved_inputs if c[0] == 'single']
    assert len(resolved_single_calls) == 2
    # Ensure that one of the calls used the default-created production_data from signal1
    paths = {input_data.path for _, input_data, _ in resolved_single_calls}
    assert 'traces-name:3' in next(iter(paths)) or any('traces-name:3' in p for p in paths)


def test_resolve_monitor_schedule_arm_id_raises_when_no_monitoring_signals_and_no_data_collector():
    ops = _create_schedule_ops_instance()

    # No endpoint_deployment_id and no model_id -> mdc flags remain False
    target = DummyTarget(endpoint_deployment_id=None, model_id=None)
    create_monitor = DummyCreateMonitor(monitoring_target=target, monitoring_signals=None)
    schedule = DummySchedule(create_monitor=create_monitor)
    ops._job_operations = DummyJobOperations()
    ops._data_operations = DummyDataOperations()
    ops._online_deployment_operations = DummyOnlineDeploymentOperations(DummyOnlineDeployment())
    ops._orchestrators = DummyOrchestrator()

    with pytest.raises(ScheduleException) as exc_info:
        ops._resolve_monitor_schedule_arm_id(schedule)

    message = str(exc_info.value)
    assert 'monitoring_signals is None' in message or 'monitoring_signals' in message


class DummyFADProductionData:
    def __init__(self, input_data=None, data_context=None, data_window=None):  # pylint: disable=unused-argument
        self.input_data = input_data
        self.data_context = data_context
        self.data_window = data_window
        self.pre_processing_component = 'pre_comp_prod'


class DummyRefData:
    def __init__(self, input_data=None):
        self.input_data = input_data
        self.pre_processing_component = 'pre_comp_ref'


class DummyAMLVersionedArmId:
    def __init__(self, arm_id):  # pylint: disable=unused-argument
        # arm_id format is not important for tests; just set deterministic name/version
        self.asset_name = 'asset_name'
        self.asset_version = '1'


def _create_schedule_ops(job_ops=None, data_ops=None, online_ops=None, orchestrator=None):
    ops = DummyScheduleOperations()
    ops._operation_scope = types.SimpleNamespace(resource_group_name=ops._resource_group_name)
    ops._job_operations = job_ops or DummyJobOperations()
    ops._data_operations = data_ops or DummyDataOperations()
    ops._online_deployment_operations = online_ops
    ops._orchestrators = orchestrator or DummyOrchestrator()

    # avoid exercising real ARM id logic in these tests
    def fake_process(self, target):  # pylint: disable=unused-argument
        return 'endpoint', 'deployment'

    ops._process_and_get_endpoint_deployment_names_from_id = types.MethodType(fake_process, ops)
    return ops


def test_feature_attr_drift_default_production_data_created_and_inputs_resolved(monkeypatch):
    monkeypatch.setattr(schedule_module, 'AMLVersionedArmId', DummyAMLVersionedArmId)
    monkeypatch.setattr(schedule_module, 'Input', DummyInput)
    monkeypatch.setattr(schedule_module, 'BaselineDataRange', DummyBaselineDataRange)
    monkeypatch.setattr(schedule_module, 'FADProductionData', DummyFADProductionData)

    data_ops = DummyDataOperations()
    data_ops.register('asset_name', '1', 'uri_folder')

    collections = {
        'model_inputs': DummyCollectionEntry('/subscriptions/sub/.../model_inputs', enabled='true'),
        'model_outputs': DummyCollectionEntry('/subscriptions/sub/.../model_outputs', enabled='true'),
    }
    data_collector = DummyDataCollector(collections)
    online_dep = DummyOnlineDeployment(data_collector=data_collector)
    online_ops = DummyOnlineDeploymentOperations(online_dep)

    job_ops = DummyJobOperations()
    orchestrator = DummyOrchestrator()

    ops = _create_schedule_ops(job_ops=job_ops, data_ops=data_ops, online_ops=online_ops, orchestrator=orchestrator)

    target = DummyTarget(endpoint_deployment_id='endpoint:deployment')

    signal = types.SimpleNamespace()
    signal.type = schedule_module.MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT
    signal.production_data = None
    signal.reference_data = DummyRefData(input_data=DummyInput(path='ref_path'))

    schedule = DummySchedule(signals={'sig1': signal}, target=target)

    schedule_module.ScheduleOperations._resolve_monitor_schedule_arm_id(ops, schedule)  # type: ignore[arg-type]

    assert isinstance(signal.production_data, list)
    assert len(signal.production_data) == 2
    assert len(job_ops.resolved_inputs) == 3
    assert isinstance(signal.reference_data.pre_processing_component, str)
    assert signal.reference_data.pre_processing_component.startswith('resolved:')
    for prod_data in signal.production_data:
        assert prod_data.pre_processing_component.startswith('resolved:')


def test_feature_attr_drift_raises_when_no_data_collector_and_no_production(monkeypatch):
    monkeypatch.setattr(schedule_module, 'Input', DummyInput)
    monkeypatch.setattr(schedule_module, 'BaselineDataRange', DummyBaselineDataRange)
    monkeypatch.setattr(schedule_module, 'FADProductionData', DummyFADProductionData)

    ops = _create_schedule_ops()

    # no endpoint_deployment_id, so mdc flags remain False
    target = DummyTarget(endpoint_deployment_id=None)

    signal = types.SimpleNamespace()
    signal.type = schedule_module.MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT
    signal.production_data = None
    signal.reference_data = None

    schedule = DummySchedule(signals={'sig_err': signal}, target=target)

    with pytest.raises(schedule_module.ScheduleException) as ex:
        schedule_module.ScheduleOperations._resolve_monitor_schedule_arm_id(ops, schedule)  # type: ignore[arg-type]

    assert 'production data must be provided' in str(ex.value)


def test_non_feature_signal_uses_resolve_job_inputs_and_updates_preprocessing():
    job_ops = DummyJobOperations()
    orchestrator = DummyOrchestrator()
    ops = _create_schedule_ops(job_ops=job_ops, orchestrator=orchestrator)

    target = DummyTarget()

    prod = types.SimpleNamespace()
    prod.input_data = DummyInput(path='prod_path')
    prod.pre_processing_component = 'comp_prod'

    ref = types.SimpleNamespace()
    ref.input_data = DummyInput(path='ref_path')
    ref.pre_processing_component = 'comp_ref'

    signal = types.SimpleNamespace()
    signal.type = schedule_module.MonitorSignalType.DATA_QUALITY
    signal.production_data = prod
    signal.reference_data = ref

    schedule = DummySchedule(signals={'dq': signal}, target=target)

    schedule_module.ScheduleOperations._resolve_monitor_schedule_arm_id(ops, schedule)  # type: ignore[arg-type]

    assert len(job_ops.resolved_inputs_multi) == 1
    resolved_inputs = job_ops.resolved_inputs_multi[0]
    assert resolved_inputs[0] is prod.input_data
    assert resolved_inputs[1] is ref.input_data

    assert prod.pre_processing_component == 'resolved:comp_prod'
    assert ref.pre_processing_component == 'resolved:comp_ref'


def test_process_and_get_endpoint_deployment_names_uses_arm_id_when_arm_id(monkeypatch):
    ops = _create_schedule_ops_instance()
    arm_id_value = '/subscriptions/sub/providers/Microsoft.MachineLearningServices/workspaces/ws/onlineEndpoints/parent-endpoint/deployments/child-deployment'

    def fake_is_arm(resource_id, parent_type, child_type):  # pylint:disable=unused-argument
        return resource_id == arm_id_value

    monkeypatch.setattr(schedule_module, 'is_ARM_id_for_parented_resource', fake_is_arm)

    class DummyAMLNamedArmId:
        def __init__(self, arm_id):  # pylint:disable=unused-argument
            self.parent_asset_name = 'parent-endpoint'
            self.asset_name = 'child-deployment'

    monkeypatch.setattr(schedule_module, 'AMLNamedArmId', DummyAMLNamedArmId)

    target = MonitoringTarget(endpoint_deployment_id=arm_id_value)
    endpoint_name, deployment_name = ops._process_and_get_endpoint_deployment_names_from_id(target)
    assert endpoint_name == 'parent-endpoint'
    assert deployment_name == 'child-deployment'
    assert target.endpoint_deployment_id == arm_id_value


def test_process_and_get_endpoint_deployment_names_parses_named_id(monkeypatch):
    ops = DummyScheduleOperations(subscription_id='sub', resource_group_name='rg', workspace_name='ws')

    def fake_is_arm(resource_id, parent_type, child_type):  # pylint:disable=unused-argument
        return False

    monkeypatch.setattr(schedule_module, 'is_ARM_id_for_parented_resource', fake_is_arm)

    target = MonitoringTarget(endpoint_deployment_id='endpoint:deployment')
    endpoint_name, deployment_name = ops._process_and_get_endpoint_deployment_names_from_id(target)
    assert endpoint_name == 'endpoint'
    assert deployment_name == 'deployment'
    assert target.endpoint_deployment_id.startswith('/subscriptions/sub/')
    assert '/workspaces/ws/onlineEndpoints/endpoint/deployments/deployment' in target.endpoint_deployment_id


def _make_schedule_ops():
    schedule_ops = ScheduleOperations.__new__(ScheduleOperations)
    schedule_ops._operation_scope = types.SimpleNamespace(
        subscription_id='subs',
        resource_group_name='rg',
        workspace_name='ws',
    )
    schedule_ops._operation_config = types.SimpleNamespace(show_progress=False, enable_telemetry=False)
    return schedule_ops


def test_process_endpoint_deployment_for_named_resource(monkeypatch):
    schedule_ops = _make_schedule_ops()
    target = DummyTarget()
    target.endpoint_deployment_id = 'endpointX:deploymentY'

    monkeypatch.setattr(
        'azure.ai.ml.operations._schedule_operations.is_ARM_id_for_parented_resource',
        lambda *_: False,
    )

    endpoint_name, deployment_name = schedule_ops._process_and_get_endpoint_deployment_names_from_id(target)

    assert endpoint_name == 'endpointX'
    assert deployment_name == 'deploymentY'
    expected_formatted_id = NAMED_RESOURCE_ID_FORMAT_WITH_PARENT.format(
        schedule_ops._subscription_id,
        schedule_ops._resource_group_name,
        AZUREML_RESOURCE_PROVIDER,
        schedule_ops._workspace_name,
        schedule_module.snake_to_camel(AzureMLResourceType.ONLINE_ENDPOINT),
        'endpointX',
        AzureMLResourceType.DEPLOYMENT,
        'deploymentY',
    )
    assert target.endpoint_deployment_id == expected_formatted_id


def test_process_endpoint_deployment_for_arm_id(monkeypatch):
    schedule_ops = _make_schedule_ops()
    target = DummyTarget()
    original_id = (
        '/subscriptions/foo/resourceGroups/bar/providers/Microsoft.MachineLearningServices'
        '/workspaces/baz/onlineEndpoints/endpointAlpha/deployments/deployBeta'
    )
    target.endpoint_deployment_id = original_id

    monkeypatch.setattr(
        'azure.ai.ml.operations._schedule_operations.is_ARM_id_for_parented_resource',
        lambda *_: True,
    )

    class StubNamedArmId:
        def __init__(self, arm_id):
            self.parent_asset_name = 'endpointAlpha'
            self.asset_name = 'deployBeta'

    monkeypatch.setattr(
        'azure.ai.ml.operations._schedule_operations.AMLNamedArmId',
        StubNamedArmId,
    )

    endpoint_name, deployment_name = schedule_ops._process_and_get_endpoint_deployment_names_from_id(target)

    assert endpoint_name == 'endpointAlpha'
    assert deployment_name == 'deployBeta'
    assert target.endpoint_deployment_id == original_id


class GeneratedDummyJobOperations:
    def __init__(self):
        self.resolved_inputs = []
        self.resolved_job_inputs = []

    def _resolve_job_input(self, input_obj, base_path):
        self.resolved_inputs.append((input_obj, base_path))

    def _resolve_job_inputs(self, inputs, base_path):
        self.resolved_job_inputs.append((inputs, base_path))


class GeneratedDummyDataOperations:
    def get(self, name, version):
        return SimpleNamespace(type=f'Type({name},{version})')


class GeneratedDummyOnlineDeploymentOperations:
    def __init__(self, deployment):
        self._deployment = deployment

    def get(self, deployment_name, endpoint_name):
        return self._deployment


def _generated_build_operations_container(job_ops, online_ops, data_ops):
    class Container:
        def get_operation(self, resource_type, _type_check):
            if resource_type == AzureMLResourceType.JOB:
                return job_ops
            if resource_type == AzureMLResourceType.ONLINE_DEPLOYMENT:
                return online_ops
            if resource_type == AzureMLResourceType.DATA:
                return data_ops
            raise KeyError(resource_type)

    return Container()


class GeneratedDummyOrchestrator:
    def get_asset_arm_id(self, asset, azureml_type=None, register_asset=None):
        if asset:
            return asset
        return f'{azureml_type}-arm'


class GeneratedDummyMonitorDefinition:
    def __init__(self, target, monitoring_signals):
        self.monitoring_target = target
        self.monitoring_signals = monitoring_signals


class GeneratedDummySchedule:
    def __init__(self, target, monitoring_signals):
        self.create_monitor = GeneratedDummyMonitorDefinition(target, monitoring_signals)
        self._base_path = '/base'

    def _create_default_monitor_definition(self):
        self.default_created = True


class GeneratedDummySignal:
    def __init__(self, signal_type):
        self.type = signal_type
        self.production_data = None
        self.reference_data = None


def _generated_build_schedule_operations(online_deployment):
    schedule_ops = object.__new__(ScheduleOperations)
    schedule_ops._operation_scope = types.SimpleNamespace(subscription_id='sub', resource_group_name='rg', workspace_name='ws')
    schedule_ops._kwargs = {}
    schedule_ops._service_client_kwargs = {}
    schedule_ops._orchestrators = GeneratedDummyOrchestrator()
    job_ops = GeneratedDummyJobOperations()
    data_ops = GeneratedDummyDataOperations()
    schedule_ops._all_operations = _generated_build_operations_container(
        job_ops, GeneratedDummyOnlineDeploymentOperations(online_deployment), data_ops
    )
    return schedule_ops, job_ops


def _generated_build_endpoint_deployment(tags):
    return SimpleNamespace(tags=tags, data_collector=None)


def _generated_build_target():
    return SimpleNamespace(endpoint_deployment_id='endpoint:deployment', model_id=None)


def test_data_drift_without_collector_raises_schedule_exception():
    tags = {
        DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY: 'false',
        DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY: 'false',
        DEPLOYMENT_MODEL_INPUTS_NAME_KEY: 'model_in',
        DEPLOYMENT_MODEL_INPUTS_VERSION_KEY: 'v1',
        DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY: 'model_out',
        DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY: 'v2',
    }
    deployment = _generated_build_endpoint_deployment(tags)
    schedule_ops, _ = _generated_build_schedule_operations(deployment)
    target = _generated_build_target()
    signal = GeneratedDummySignal(schedule_module.MonitorSignalType.DATA_DRIFT)
    schedule = GeneratedDummySchedule(target, {'data_drift': signal})

    with pytest.raises(schedule_module.ScheduleException) as exc_info:
        schedule_ops._resolve_monitor_schedule_arm_id(schedule)

    assert 'A target and baseline dataset must be provided' in str(exc_info.value)


def test_data_drift_with_input_collector_populates_defaults():
    tags = {
        DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY: 'true',
        DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY: 'false',
        DEPLOYMENT_MODEL_INPUTS_NAME_KEY: 'model_in',
        DEPLOYMENT_MODEL_INPUTS_VERSION_KEY: 'v1',
        DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY: 'model_out',
        DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY: 'v2',
    }
    deployment = _generated_build_endpoint_deployment(tags)
    schedule_ops, job_ops = _generated_build_schedule_operations(deployment)
    target = _generated_build_target()
    signal = GeneratedDummySignal(schedule_module.MonitorSignalType.DATA_DRIFT)
    schedule = GeneratedDummySchedule(target, {'data_drift': signal})

    schedule_ops._resolve_monitor_schedule_arm_id(schedule)

    expected_input_path = f'{tags[DEPLOYMENT_MODEL_INPUTS_NAME_KEY]}:{tags[DEPLOYMENT_MODEL_INPUTS_VERSION_KEY]}'
    assert signal.production_data.input_data.path == expected_input_path
    assert signal.reference_data.input_data.path == expected_input_path
    inputs, base_path = job_ops.resolved_job_inputs[-1]
    assert base_path == '/base'
    assert inputs[0].path == expected_input_path
    assert inputs[1].path == expected_input_path


def test_prediction_drift_with_output_collector_populates_defaults():
    tags = {
        DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY: 'false',
        DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY: 'true',
        DEPLOYMENT_MODEL_INPUTS_NAME_KEY: 'model_in',
        DEPLOYMENT_MODEL_INPUTS_VERSION_KEY: 'v1',
        DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY: 'model_out',
        DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY: 'v2',
    }
    deployment = _generated_build_endpoint_deployment(tags)
    schedule_ops, job_ops = _generated_build_schedule_operations(deployment)
    target = _generated_build_target()
    signal = GeneratedDummySignal(schedule_module.MonitorSignalType.PREDICTION_DRIFT)
    schedule = GeneratedDummySchedule(target, {'prediction_drift': signal})

    schedule_ops._resolve_monitor_schedule_arm_id(schedule)

    expected_output_path = f'{tags[DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY]}:{tags[DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY]}'
    assert signal.production_data.input_data.path == expected_output_path
    assert signal.reference_data.input_data.path == expected_output_path
    inputs, base_path = job_ops.resolved_job_inputs[-1]
    assert base_path == '/base'
    assert inputs[0].path == expected_output_path
    assert inputs[1].path == expected_output_path


def test_prediction_drift_without_output_collector_raises_schedule_exception():
    tags = {
        DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY: 'false',
        DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY: 'false',
        DEPLOYMENT_MODEL_INPUTS_NAME_KEY: 'model_in',
        DEPLOYMENT_MODEL_INPUTS_VERSION_KEY: 'v1',
        DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY: 'model_out',
        DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY: 'v2',
    }
    deployment = _generated_build_endpoint_deployment(tags)
    schedule_ops, _ = _generated_build_schedule_operations(deployment)
    target = _generated_build_target()
    signal = GeneratedDummySignal(schedule_module.MonitorSignalType.PREDICTION_DRIFT)
    schedule = GeneratedDummySchedule(target, {'prediction_drift': signal})

    with pytest.raises(schedule_module.ScheduleException) as exc_info:
        schedule_ops._resolve_monitor_schedule_arm_id(schedule)

    assert 'A target and baseline dataset must be provided' in str(exc_info.value)


def test_feature_attribution_with_input_collector_populates_production_list():
    tags = {
        DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY: 'true',
        DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY: 'true',
        DEPLOYMENT_MODEL_INPUTS_NAME_KEY: 'model_in',
        DEPLOYMENT_MODEL_INPUTS_VERSION_KEY: 'v1',
        DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY: 'model_out',
        DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY: 'v2',
    }
    deployment = _generated_build_endpoint_deployment(tags)
    schedule_ops, job_ops = _generated_build_schedule_operations(deployment)
    target = _generated_build_target()
    signal = GeneratedDummySignal(schedule_module.MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT)
    signal.reference_data = ReferenceData(
        input_data=Input(path='ref_target:1', type='ref-type'),
        data_context=MonitorDatasetContext.MODEL_OUTPUTS,
        data_window=BaselineDataRange(lookback_window_size='default', lookback_window_offset='default'),
    )
    schedule = GeneratedDummySchedule(target, {'feature_attr': signal})

    schedule_ops._resolve_monitor_schedule_arm_id(schedule)

    assert isinstance(signal.production_data, list)
    assert len(signal.production_data) == 2
    paths = [prod.input_data.path for prod in signal.production_data]
    assert paths == [
        f'{tags[DEPLOYMENT_MODEL_INPUTS_NAME_KEY]}:{tags[DEPLOYMENT_MODEL_INPUTS_VERSION_KEY]}',
        f'{tags[DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY]}:{tags[DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY]}',
    ]
    assert len(job_ops.resolved_inputs) == 3
    assert job_ops.resolved_inputs[-1][0].path == 'ref_target:1'


def test_feature_attribution_without_output_collector_raises_schedule_exception():
    tags = {
        DEPLOYMENT_MODEL_INPUTS_COLLECTION_KEY: 'false',
        DEPLOYMENT_MODEL_OUTPUTS_COLLECTION_KEY: 'false',
        DEPLOYMENT_MODEL_INPUTS_NAME_KEY: 'model_in',
        DEPLOYMENT_MODEL_INPUTS_VERSION_KEY: 'v1',
        DEPLOYMENT_MODEL_OUTPUTS_NAME_KEY: 'model_out',
        DEPLOYMENT_MODEL_OUTPUTS_VERSION_KEY: 'v2',
    }
    deployment = _generated_build_endpoint_deployment(tags)
    schedule_ops, _ = _generated_build_schedule_operations(deployment)
    target = _generated_build_target()
    signal = GeneratedDummySignal(schedule_module.MonitorSignalType.FEATURE_ATTRIBUTION_DRIFT)
    schedule = GeneratedDummySchedule(target, {'feature_attr': signal})

    with pytest.raises(schedule_module.ScheduleException) as exc_info:
        schedule_ops._resolve_monitor_schedule_arm_id(schedule)

    assert 'A production data must be provided' in str(exc_info.value)
