import inspect
import json
import sys
import types
from types import SimpleNamespace

import pytest

import azure.ai.ml.entities._indexes.data_index_func as data_index_func
import azure.ai.ml.entities._indexes.data_index_func as data_index_func_module
from azure.ai.ml.constants._component import LLMRAGComponentUri
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._common import DataIndexTypes
from azure.ai.ml.entities._indexes import utils as indexes_utils
from azure.ai.ml.entities._indexes.data_index_func import (
    _build_data_index,
    index_data,
    data_index_incremental_update_hosted,
    get_component_obj,
    _resolve_connection_id,
    DataIndex,
    DataIndexTypes as DataIndexTypesAlias,
    data_index_faiss,
    data_index_hosted,
    optional_pipeline_input_provided,
    use_automatic_compute,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.constants import AssetTypes as AssetTypesAlias
from azure.ai.ml.exceptions import ValidationException


def test_data_index_func_module_importable():
    assert data_index_func is not None


def test_data_index_func_has_docstring():
    # Module-level docstring may be absent; when present, it must be a string.
    assert (data_index_func.__doc__ is None) or isinstance(data_index_func.__doc__, str)


def test_data_index_func_has_public_members():
    public_members = [name for name in dir(data_index_func) if not name.startswith("_")]
    assert len(public_members) > 0


def test_data_index_func_all_is_consistent_if_present():
    if hasattr(data_index_func, "__all__"):
        exported = set(data_index_func.__all__)
        for name in exported:
            assert hasattr(data_index_func, name)
    else:
        pytest.skip("__all__ not defined on data_index_func module")


@pytest.mark.parametrize("name", [
    "build_data_index_function" if hasattr(data_index_func, "build_data_index_function") else None,
    "DataIndexFunction" if hasattr(data_index_func, "DataIndexFunction") else None,
])
def test_selected_symbols_are_callable_or_class(name):
    if name is None:
        pytest.skip("Symbol not present in this version of data_index_func module")
    obj = getattr(data_index_func, name)
    assert inspect.isfunction(obj) or inspect.isclass(obj)


class DummyConnections:
    def __init__(self, connection_to_return=None):
        self.connection_to_return = connection_to_return
        self.last_requested_name = None

    def get(self, name):
        self.last_requested_name = name
        return self.connection_to_return


class DummyConnectionObject:
    def __init__(self, id_value):
        self.id = id_value


class DummyRegistryComponents:
    def __init__(self, result):
        self._result = result
        self.last_name = None
        self.last_kwargs = None

    def get(self, name, **kwargs):
        self.last_name = name
        self.last_kwargs = kwargs
        return self._result


class DummyRegistryMLClient:
    def __init__(self, subscription_id=None, resource_group_name=None, credential=None, registry_name=None):
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self._credential = credential
        self.registry_name = registry_name
        self.components = DummyRegistryComponents(result="dummy_component_from_registry")


def install_dummy_azure_ai_ml_module_with_mlclient_and_loader(mlclient_cls, load_component_func=None):
    azure_module = sys.modules.setdefault("azure", types.ModuleType("azure"))
    ai_module = sys.modules.setdefault("azure.ai", types.ModuleType("azure.ai"))
    ml_module = sys.modules.setdefault("azure.ai.ml", types.ModuleType("azure.ai.ml"))
    ai_module.ml = ml_module
    setattr(ml_module, "MLClient", mlclient_cls)
    if load_component_func is not None:
        setattr(ml_module, "load_component", load_component_func)


def install_dummy_arm_id_utils_module(asset_name_value="conn_name"):
    module_name = "azure.ai.ml._utils._arm_id_utils"
    parent_azure = sys.modules.setdefault("azure", types.ModuleType("azure"))
    parent_ai = sys.modules.setdefault("azure.ai", types.ModuleType("azure.ai"))
    parent_ml = sys.modules.setdefault("azure.ai.ml", types.ModuleType("azure.ai.ml"))
    parent_utils = sys.modules.setdefault("azure.ai.ml._utils", types.ModuleType("azure.ai.ml._utils"))
    setattr(parent_ai, "ml", parent_ml)
    sys.modules["azure.ai.ml._utils"] = parent_utils
    arm_module = types.ModuleType(module_name)

    class AMLNamedArmId:
        def __init__(self, arm_id):
            self.arm_id = arm_id
            self.asset_name = asset_name_value

    arm_module.AMLNamedArmId = AMLNamedArmId
    sys.modules[module_name] = arm_module


class DummyDataIndexForBuild:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_build_data_index_none_returns_none():
    assert _build_data_index(None) is None


def test_build_data_index_passes_through_dataindex_instance(monkeypatch):
    monkeypatch.setattr(data_index_func, "DataIndex", DummyDataIndexForBuild)
    di = DummyDataIndexForBuild(a=1)
    result = _build_data_index(di)
    assert result is di


def test_build_data_index_dict_creates_dataindex(monkeypatch):
    created = {}

    class RecordingDummyDataIndex:
        def __init__(self, **kwargs):
            created.update(kwargs)
            self.kwargs = kwargs

    monkeypatch.setattr(data_index_func, "DataIndex", RecordingDummyDataIndex)
    io_dict = {"foo": "bar", "num": 3}
    result = _build_data_index(io_dict)
    assert isinstance(result, RecordingDummyDataIndex)
    assert created == io_dict


def test_build_data_index_invalid_type_raises_validation_exception():
    with pytest.raises(ValidationException) as exc_info:
        _build_data_index([1, 2, 3])
    assert "data_index only support dict and DataIndex" in str(exc_info.value)


class DummyConfiguredComponent:
    def __init__(self, tag):
        self.tag = tag
        self.properties = {}


class DummyDataIndexForIndexData:
    def __init__(self, index_type, name="idx-name"):
        class Index:
            def __init__(self, t):
                self.type = t

        self.index = Index(index_type)
        self.name = name


def test_index_data_routes_to_faiss_and_sets_properties(monkeypatch):
    called = {}

    def fake_data_index_faiss(ml_client, data_index, *args, **kwargs):
        called["fn"] = "faiss"
        called["type"] = data_index.index.type
        return DummyConfiguredComponent("faiss")

    monkeypatch.setattr(data_index_func, "data_index_faiss", fake_data_index_faiss)
    monkeypatch.setattr(data_index_func, "DataIndex", DummyDataIndexForIndexData)

    di = DummyDataIndexForIndexData(index_type=data_index_func.DataIndexTypes.FAISS, name="my-index")
    result = index_data(data_index=di)

    assert isinstance(result, DummyConfiguredComponent)
    assert called["fn"] == "faiss"
    assert result.properties["azureml.mlIndexAssetName"] == "my-index"
    assert result.properties["azureml.mlIndexAssetKind"] == di.index.type
    assert result.properties["azureml.mlIndexAssetSource"] == "Data Asset"


def test_index_data_routes_to_incremental_update_for_acs(monkeypatch):
    calls = {"faiss": 0, "inc": 0, "hosted": 0}

    def fake_faiss(ml_client, data_index, *args, **kwargs):
        calls["faiss"] += 1
        return DummyConfiguredComponent("faiss")

    def fake_inc(ml_client, data_index, *args, **kwargs):
        calls["inc"] += 1
        return DummyConfiguredComponent("inc")

    def fake_hosted(ml_client, data_index, *args, **kwargs):
        calls["hosted"] += 1
        return DummyConfiguredComponent("hosted")

    monkeypatch.setattr(data_index_func, "data_index_faiss", fake_faiss)
    monkeypatch.setattr(data_index_func, "data_index_incremental_update_hosted", fake_inc)
    monkeypatch.setattr(data_index_func, "data_index_hosted", fake_hosted)
    monkeypatch.setattr(data_index_func, "DataIndex", DummyDataIndexForIndexData)

    di = DummyDataIndexForIndexData(index_type=data_index_func.DataIndexTypes.ACS, name="acs-index")
    result = index_data(data_index=di, incremental_update=True)

    assert isinstance(result, DummyConfiguredComponent)
    assert result.tag == "inc"
    assert calls == {"faiss": 0, "inc": 1, "hosted": 0}


def test_index_data_routes_to_hosted_for_acs_without_incremental(monkeypatch):
    calls = {"faiss": 0, "inc": 0, "hosted": 0}

    def fake_faiss(ml_client, data_index, *args, **kwargs):
        calls["faiss"] += 1
        return DummyConfiguredComponent("faiss")

    def fake_inc(ml_client, data_index, *args, **kwargs):
        calls["inc"] += 1
        return DummyConfiguredComponent("inc")

    def fake_hosted(ml_client, data_index, *args, **kwargs):
        calls["hosted"] += 1
        return DummyConfiguredComponent("hosted")

    monkeypatch.setattr(data_index_func, "data_index_faiss", fake_faiss)
    monkeypatch.setattr(data_index_func, "data_index_incremental_update_hosted", fake_inc)
    monkeypatch.setattr(data_index_func, "data_index_hosted", fake_hosted)
    monkeypatch.setattr(data_index_func, "DataIndex", DummyDataIndexForIndexData)

    di = DummyDataIndexForIndexData(index_type=data_index_func.DataIndexTypes.ACS, name="acs-index")
    result = index_data(data_index=di)

    assert isinstance(result, DummyConfiguredComponent)
    assert result.tag == "hosted"
    assert calls == {"faiss": 0, "inc": 0, "hosted": 1}


def test_index_data_unsupported_type_raises_value_error(monkeypatch):
    monkeypatch.setattr(data_index_func, "data_index_faiss", lambda *args, **kwargs: None)
    monkeypatch.setattr(data_index_func, "data_index_incremental_update_hosted", lambda *a, **k: None)
    monkeypatch.setattr(data_index_func, "data_index_hosted", lambda *a, **k: None)
    monkeypatch.setattr(data_index_func, "DataIndex", DummyDataIndexForIndexData)

    di = DummyDataIndexForIndexData(index_type="UNSUPPORTED", name="bad-index")
    with pytest.raises(ValueError) as exc_info:
        index_data(data_index=di)
    assert "Unsupported index type" in str(exc_info.value)


class DummySource:
    def __init__(
        self,
        input_type,
        path,
        input_glob,
        chunk_size,
        chunk_overlap,
        citation_url,
        has_regex,
    ):
        class InputData:
            def __init__(self, t, p):
                self.type = t
                self.path = p

        self.input_data = InputData(input_type, path)
        self.input_glob = input_glob
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.citation_url = citation_url
        if has_regex:
            class Regex:
                def _to_dict(self):
                    return {"pattern": "x"}

            self.citation_url_replacement_regex = Regex()
        else:
            self.citation_url_replacement_regex = None


class DummyPipelineInputForOptional:
    def __init__(self, data=None):
        self._data = data


def test_optional_pipeline_input_provided_variants():
    assert optional_pipeline_input_provided(None) is False

    empty_input = DummyPipelineInputForOptional()
    assert optional_pipeline_input_provided(empty_input) is False

    filled_input = DummyPipelineInputForOptional(data="value")
    assert optional_pipeline_input_provided(filled_input) is True


def test_use_automatic_compute_sets_resources_and_returns_component():
    class DummyComponent:
        def __init__(self):
            self.calls = []

        def set_resources(self, instance_count=None, instance_type=None, properties=None):
            self.calls.append(
                {
                    "instance_count": instance_count,
                    "instance_type": instance_type,
                    "properties": properties,
                }
            )
            return self

    comp = DummyComponent()
    returned = use_automatic_compute(comp, instance_count=3, instance_type="Standard_DS3_v2")

    assert returned is comp
    assert len(comp.calls) == 1
    call = comp.calls[0]
    assert call["instance_count"] == 3
    assert call["instance_type"] == "Standard_DS3_v2"
    assert call["properties"] == {"compute_specification": {"automatic": True}}


class _DummyPipelineInput:
    def __init__(self, data):
        self._data = data


def test_optional_pipeline_input_provided_detects_values():
    assert not optional_pipeline_input_provided(None)
    assert not optional_pipeline_input_provided(_DummyPipelineInput(None))
    assert optional_pipeline_input_provided(_DummyPipelineInput("value"))


class _StubComponent:
    def __init__(self):
        self.resources = None
        self.last_resources = None

    def set_resources(self, instance_count=None, instance_type=None, properties=None):
        resources = {
            "instance_count": instance_count,
            "instance_type": instance_type,
            "properties": properties,
        }
        self.resources = resources
        self.last_resources = resources
        return self


def test_use_automatic_compute_applies_resources():
    component = _StubComponent()
    result = use_automatic_compute(component, instance_count=2, instance_type="auto-type")
    assert result is component
    assert component.resources["instance_count"] == 2
    assert component.resources["instance_type"] == "auto-type"
    assert component.resources["properties"] == {"compute_specification": {"automatic": True}}


def test_get_component_obj_returns_non_str_component():
    sentinel = object()
    assert get_component_obj(None, sentinel) is sentinel


def test_get_component_obj_loads_local_component(monkeypatch):
    loaded = {}

    def fake_load_component(source):
        loaded["source"] = source
        return "local"

    monkeypatch.setattr("azure.ai.ml.load_component", fake_load_component)
    result = get_component_obj(object(), "local/path")
    assert result == "local"
    assert loaded["source"] == "local/path"


def test_get_component_obj_fetches_from_registry(monkeypatch):
    class FakeMLClient:
        last_created = None

        def __init__(self, subscription_id, resource_group_name, credential, registry_name):
            self.subscription_id = subscription_id
            self.resource_group_name = resource_group_name
            self.credential = credential
            self.registry_name = registry_name
            FakeMLClient.last_created = self
            self.components = self
            self.last_get = None

        def get(self, name, **kwargs):
            self.last_get = (name, kwargs)
            return "registry-obj"

    monkeypatch.setattr("azure.ai.ml.MLClient", FakeMLClient)
    ml_caller = type("CallerClient", (), {"subscription_id": "sub", "resource_group_name": "rg", "_credential": "cred"})()
    uri = "azureml://registries/reg/components/mycomp/versions/v1"
    result = get_component_obj(ml_caller, uri)
    assert result == "registry-obj"
    assert FakeMLClient.last_created.registry_name == "reg"
    assert FakeMLClient.last_created.last_get == ("mycomp", {"version": "v1"})


def test_resolve_connection_id_returns_none_for_missing(monkeypatch):
    class FakeArmId:
        def __init__(self, connection):
            self.asset_name = "missing"

    class FakeConnections:
        def get(self, name):
            assert name == "missing"
            return None

    class FakeClient:
        connections = FakeConnections()

    monkeypatch.setattr("azure.ai.ml._utils._arm_id_utils.AMLNamedArmId", FakeArmId)
    assert _resolve_connection_id(FakeClient(), "some") is None


def test_resolve_connection_id_returns_id(monkeypatch):
    class FakeArmId:
        def __init__(self, connection):
            self.asset_name = "present"

    class FakeConnection:
        id = "conn-id"

    class FakeConnections:
        def get(self, name):
            assert name == "present"
            return FakeConnection()

    class FakeClient:
        connections = FakeConnections()

    monkeypatch.setattr("azure.ai.ml._utils._arm_id_utils.AMLNamedArmId", FakeArmId)
    assert _resolve_connection_id(FakeClient(), "value") == "conn-id"


def test_resolve_connection_id_returns_none_for_no_connection():
    assert _resolve_connection_id(object(), None) is None


class _DummyArmId:
    def __init__(self, identifier):
        self.asset_name = f"parsed-{identifier}"


class _DummyConnections:
    def __init__(self, mapping):
        self._mapping = mapping

    def get(self, name):
        return self._mapping.get(name)


class _DummyRegistryClient:
    def __init__(self, subscription_id, resource_group_name, credential, registry_name, capture):
        capture["subscription_id"] = subscription_id
        capture["resource_group_name"] = resource_group_name
        capture["credential"] = credential
        capture["registry_name"] = registry_name
        self.components = self
        self.capture = capture

    def get(self, component_name, **kwargs):
        self.capture["component_name"] = component_name
        self.capture["identifier_kwargs"] = kwargs
        return f"{component_name}-loaded-{kwargs}"


def test_optional_pipeline_input_varied_states():
    assert not data_index_func.optional_pipeline_input_provided(None)
    assert not data_index_func.optional_pipeline_input_provided(_DummyPipelineInput(None))
    assert data_index_func.optional_pipeline_input_provided(_DummyPipelineInput("value"))


def test_use_automatic_compute_applies_resources():
    component = _StubComponent()
    result = data_index_func.use_automatic_compute(component, instance_count=5, instance_type="small")
    assert result is component
    assert component.last_resources["instance_count"] == 5
    assert component.last_resources["instance_type"] == "small"
    assert component.last_resources["properties"] == {"compute_specification": {"automatic": True}}


def test_get_component_obj_returns_non_string_directly():
    sentinel = object()
    assert data_index_func.get_component_obj(None, sentinel) is sentinel


def test_get_component_obj_loads_local_component(monkeypatch):
    captured = {}

    def fake_load_component(source):
        captured["source"] = source
        return "local-component"

    monkeypatch.setattr("azure.ai.ml.load_component", fake_load_component)
    result = data_index_func.get_component_obj(None, "components/component.yml")
    assert result == "local-component"
    assert captured["source"] == "components/component.yml"


def test_get_component_obj_fetches_registry_component(monkeypatch):
    capture = {}

    def fake_ml_client(subscription_id, resource_group_name, credential, registry_name):
        return _DummyRegistryClient(subscription_id, resource_group_name, credential, registry_name, capture)

    monkeypatch.setattr("azure.ai.ml.MLClient", fake_ml_client)
    MlClientType = type(
        "MlClient",
        (),
        {
            "subscription_id": "sub-id",
            "resource_group_name": "rg",
            "_credential": "cred",
        },
    )
    ml_client = MlClientType()
    uri = "azureml://registries/my-reg/components/my-comp/versions/v1"
    result = data_index_func.get_component_obj(ml_client, uri)
    assert capture["registry_name"] == "my-reg"
    assert capture["component_name"] == "my-comp"
    assert capture["identifier_kwargs"] == {"version": "v1"}
    assert result == "my-comp-loaded-{'version': 'v1'}"


def test_resolve_connection_id_handles_variants(monkeypatch):
    monkeypatch.setattr("azure.ai.ml._utils._arm_id_utils.AMLNamedArmId", _DummyArmId)
    ml_client_missing = type("MlClientMissing", (), {"connections": _DummyConnections({})})()
    assert data_index_func._resolve_connection_id(ml_client_missing, None) is None
    assert data_index_func._resolve_connection_id(ml_client_missing, "missing") is None

    ml_client_found = type(
        "MlClientFound",
        (),
        {"connections": _DummyConnections({"parsed-present": type("Conn", (), {"id": "found-id"})()})},
    )()
    assert data_index_func._resolve_connection_id(ml_client_found, "present") == "found-id"



class _Batch1DummyComponent:
    def __init__(self):
        self.captured_resources = None

    def set_resources(self, **kwargs):
        self.captured_resources = kwargs
        return self


def test_optional_pipeline_input_provided_variants_additional():
    assert optional_pipeline_input_provided(None) is False
    assert optional_pipeline_input_provided(_DummyPipelineInput(None)) is False
    assert optional_pipeline_input_provided(_DummyPipelineInput("value")) is True


def test_use_automatic_compute_sets_automatic_resources_additional():
    component = _Batch1DummyComponent()
    returned = use_automatic_compute(component, instance_count=3, instance_type="Standard_A1")
    assert returned is component
    assert component.captured_resources == {
        "instance_count": 3,
        "instance_type": "Standard_A1",
        "properties": {"compute_specification": {"automatic": True}},
    }


def test_get_component_obj_returns_same_object_when_not_string_additional():
    sentinel = object()
    assert get_component_obj(None, sentinel) is sentinel


def test_get_component_obj_loads_local_component_additional(monkeypatch):
    captured = {}

    def fake_load_component(source=None):
        captured["source"] = source
        return "local-component"

    monkeypatch.setattr("azure.ai.ml.load_component", fake_load_component)
    result = get_component_obj(None, "local/component.yml")
    assert result == "local-component"
    assert captured["source"] == "local/component.yml"


def test_get_component_obj_resolves_registry_component_additional(monkeypatch):
    captured = {}

    class _FakeRegistryClient:
        def __init__(self, subscription_id=None, resource_group_name=None, credential=None, registry_name=None):
            captured["registry_name"] = registry_name
            self.components = self

        def get(self, component_name, **kwargs):
            captured["component_name"] = component_name
            captured["kwargs"] = kwargs
            return "registry-component"

    monkeypatch.setattr("azure.ai.ml.MLClient", _FakeRegistryClient)
    ml_client = type("Client", (), {
        "subscription_id": "subid",
        "resource_group_name": "rg",
        "_credential": "cred",
    })()
    component_uri = "azureml://registries/some-registry/components/test-component/versions/v1"
    result = get_component_obj(ml_client, component_uri)
    assert result == "registry-component"
    assert captured["registry_name"] == "some-registry"
    assert captured["component_name"] == "test-component"
    assert captured["kwargs"] == {"version": "v1"}


def test_resolve_connection_id_returns_expected_values(monkeypatch):
    class _DummyAMLNamedArmId:
        def __init__(self, arm_id):
            self.asset_name = arm_id

    monkeypatch.setattr("azure.ai.ml._utils._arm_id_utils.AMLNamedArmId", _DummyAMLNamedArmId)

    class _DummyMLClient:
        def __init__(self):
            self.connections = self
            self.connection_calls = []

        def get(self, name):
            self.connection_calls.append(name)
            if name == "missing":
                return None
            return type("Connection", (), {"id": f"id-{name}"})

    ml_client = _DummyMLClient()
    assert _resolve_connection_id(ml_client, None) is None
    assert _resolve_connection_id(ml_client, "missing") is None
    assert _resolve_connection_id(ml_client, "present") == "id-present"
    assert ml_client.connection_calls == ["missing", "present"]
