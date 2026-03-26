import json
import pytest
from types import SimpleNamespace

from azure.ai.ml.entities._deployment.deployment_template import DeploymentTemplate


class DummySettings:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _to_dict(self):
        return self.__dict__


class DummyEnvWithId:
    def __init__(self, id_value):
        self.id = id_value


class DummyEnvWithName:
    def __init__(self, name_value):
        self.name = name_value


class _StubRequestSettings:
    def __init__(self, request_timeout_ms=None):
        self.request_timeout_ms = request_timeout_ms


class _StubProbeSettings:
    def __init__(self, initial_delay=None, period=None, timeout=None):
        self.initial_delay = initial_delay
        self.period = period
        self.timeout = timeout


class DummyDictConvertible:
    def __init__(self, data):
        self._data = data

    def _to_dict(self):
        return self._data


def test_dump_with_all_optional_fields_and_environment_string():
    request_settings = DummySettings(a=1, b="two")
    liveness_probe = DummySettings(x=10)
    readiness_probe = DummySettings(y=20)

    template = DeploymentTemplate(
        name="test-template",
        version="1.0",
        description="a description",
        environment="env-string",
        request_settings=request_settings,
        liveness_probe=liveness_probe,
        readiness_probe=readiness_probe,
        instance_count=3,
        instance_type="Standard_DS3_v2",
        model="model-id",
        code_configuration={"code": "config"},
        environment_variables={"ENV_VAR": "value"},
        app_insights_enabled=True,
    )

    result = template.dump()

    assert result["name"] == "test-template"
    assert result["version"] == "1.0"
    assert result["description"] == "a description"
    assert result["environment"] == "env-string"
    assert result["request_settings"] == request_settings.__dict__
    assert result["liveness_probe"] == liveness_probe.__dict__
    assert result["readiness_probe"] == readiness_probe.__dict__
    assert result["instance_count"] == 3
    assert result["instance_type"] == "Standard_DS3_v2"
    assert result["model"] == "model-id"
    assert result["code_configuration"] == {"code": "config"}
    assert result["environment_variables"] == {"ENV_VAR": "value"}
    assert result["app_insights_enabled"] is True


def test_dump_without_description_and_environment_object_with_id():
    env_obj = DummyEnvWithId("env-id-123")

    template = DeploymentTemplate(
        name="no-desc-template",
        version="2.0",
        environment=env_obj,
        instance_count=0,
    )

    result = template.dump()

    assert "description" not in result
    assert result["environment"] == "env-id-123"
    assert result["name"] == "no-desc-template"
    assert result["version"] == "2.0"
    assert result["instance_count"] == 0
    assert "app_insights_enabled" not in result


def test_dump_environment_object_with_name_only():
    env_obj = DummyEnvWithName("env-name-only")

    template = DeploymentTemplate(
        name="name-env-template",
        version="3.0",
        environment=env_obj,
    )

    result = template.dump()

    assert result["environment"] == "env-name-only"
    assert result["name"] == "name-env-template"
    assert result["version"] == "3.0"


def test_to_rest_object_with_stage_deployment_type_environment_id_and_allowed_instance_types_string():
    template = DeploymentTemplate(
        name="rest-deployment",
        version="1",
        stage="Active",
        deployment_template_type="standard",
        environment="ignored-env",
        allowed_instance_types="Standard_DS1_v2 Standard_DS2_v2",
    )

    template.environment_id = "env-id-999"
    template.tags = {"team": "ml"}

    rest_obj = template._to_rest_object()

    assert rest_obj["name"] == "rest-deployment"
    assert rest_obj["version"] == "1"
    assert rest_obj["stage"] == "Active"
    assert rest_obj["deploymentTemplateType"] == "standard"
    assert rest_obj["environmentId"] == "env-id-999"
    assert rest_obj["tags"] == {"team": "ml"}
    assert rest_obj["allowedInstanceTypes"] == ["Standard_DS1_v2", "Standard_DS2_v2"]


def test_to_rest_object_with_allowed_instance_types_list_and_environment_string():
    template = DeploymentTemplate(
        name="rest-deployment-list",
        version="1",
        environment="env-string-123",
        allowed_instance_types=["Standard_F4s_v2", "Standard_F8s_v2"],
    )

    rest_obj = template._to_rest_object()

    assert rest_obj["environmentId"] == "env-string-123"
    assert rest_obj["allowedInstanceTypes"] == ["Standard_F4s_v2", "Standard_F8s_v2"]


def test_to_rest_object_and_to_dict_with_other_allowed_instance_types_and_scoring():
    template = DeploymentTemplate(
        name="rest-deployment-mixed",
        version="1",
        allowed_instance_types=123,
        scoring_path="/score",
        scoring_port=8080,
        instance_count=0,
        instance_type="Standard_DS3_v2",
    )

    rest_obj = template._to_rest_object()

    assert rest_obj["defaultInstanceType"] == "Standard_DS3_v2"
    assert rest_obj["instanceCount"] == 0
    assert rest_obj["scoringPath"] == "/score"
    assert rest_obj["scoringPort"] == 8080
    assert rest_obj["allowedInstanceTypes"] == ["123"]

    dict_obj = template._to_dict()

    assert dict_obj["name"] == "rest-deployment-mixed"
    assert dict_obj["version"] == "1"
    assert dict_obj["defaultInstanceType"] == "Standard_DS3_v2"
    assert dict_obj["instanceCount"] == 0
    assert dict_obj["scoringPath"] == "/score"
    assert dict_obj["scoringPort"] == 8080
    assert dict_obj["allowedInstanceTypes"] == 123


def test_dump_with_all_optional_fields_and_environment_string_generated():
    template = DeploymentTemplate(
        name="test-name",
        version="1",
        description="a description",
        environment="env-id",
        request_settings=DummySettings(timeout=100),
        liveness_probe=DummySettings(interval=5),
        readiness_probe=DummySettings(interval=10),
        instance_count=0,
        instance_type="Standard_DS3_v2",
        model="model-id",
        code_configuration={"path": "./code"},
        environment_variables={"A": "1"},
        app_insights_enabled=False,
    )

    result = template.dump()

    assert result["name"] == "test-name"
    assert result["version"] == "1"
    assert result["description"] == "a description"
    assert result["environment"] == "env-id"
    assert result["request_settings"] == {"timeout": 100}
    assert result["liveness_probe"] == {"interval": 5}
    assert result["readiness_probe"] == {"interval": 10}
    assert result["instance_count"] == 0
    assert result["instance_type"] == "Standard_DS3_v2"
    assert result["model"] == "model-id"
    assert result["code_configuration"] == {"path": "./code"}
    assert result["environment_variables"] == {"A": "1"}
    assert result["app_insights_enabled"] is False


def test_dump_without_description_and_environment_object_with_id_generated():
    env = DummyEnvWithId("env-resource-id")
    template = DeploymentTemplate(
        name="test-no-desc",
        version="2",
        environment=env,
        request_settings=DummySettings(x=1),
        liveness_probe=DummySettings(y=2),
        readiness_probe=DummySettings(z=3),
        instance_count=5,
    )

    result = template.dump()

    assert "description" not in result
    assert result["environment"] == "env-resource-id"
    assert result["request_settings"] == {"x": 1}
    assert result["liveness_probe"] == {"y": 2}
    assert result["readiness_probe"] == {"z": 3}
    assert result["instance_count"] == 5
    assert "instance_type" not in result
    assert "model" not in result
    assert "code_configuration" not in result
    assert "environment_variables" not in result
    assert "app_insights_enabled" not in result


def test_dump_environment_object_with_name_only_generated():
    env = DummyEnvWithName("env-name")
    template = DeploymentTemplate(
        name="name",
        version="3",
        environment=env,
    )

    result = template.dump()

    assert result["environment"] == "env-name"


def test_to_rest_object_with_stage_deployment_type_environment_id_and_allowed_instance_types_string_generated():
    template = DeploymentTemplate(
        name="rest1",
        version="1.0",
        description="desc",
        environment="env-string",
        environment_variables={"K": "V"},
        allowed_instance_types="Standard_DS1_v2 Standard_DS2_v2",
        instance_type="Standard_DS3_v2",
        instance_count=2,
        scoring_path="/score",
        scoring_port=5001,
        model="model-1",
        code_configuration={"code": "path"},
        app_insights_enabled=True,
        deployment_template_type="Online",
        stage="Active",
        type="customType",
    )
    template.tags = {"t1": "v1"}
    template.environment_id = "env-from-id"
    template.model_mount_path = "/mnt/model"
    template.request_settings = DummySettings(a=1)
    template.liveness_probe = DummySettings(b=2)
    template.readiness_probe = DummySettings(c=3)

    rest_obj = template._to_rest_object()

    assert rest_obj["name"] == "rest1"
    assert rest_obj["version"] == "1.0"
    assert rest_obj["type"] == "customType"
    assert rest_obj["description"] == "desc"
    assert rest_obj["stage"] == "Active"
    assert rest_obj["deploymentTemplateType"] == "Online"
    assert rest_obj["tags"] == {"t1": "v1"}
    assert rest_obj["environmentId"] == "env-from-id"
    assert rest_obj["environmentVariables"] == {"K": "V"}
    assert rest_obj["modelMountPath"] == "/mnt/model"
    assert rest_obj["requestSettings"] == {"a": 1}
    assert rest_obj["livenessProbe"] == {"b": 2}
    assert rest_obj["readinessProbe"] == {"c": 3}
    assert rest_obj["defaultInstanceType"] == "Standard_DS3_v2"
    assert rest_obj["instanceCount"] == 2
    assert rest_obj["scoringPath"] == "/score"
    assert rest_obj["scoringPort"] == 5001
    assert rest_obj["model"] == "model-1"
    assert rest_obj["codeConfiguration"] == {"code": "path"}
    assert rest_obj["appInsightsEnabled"] is True
    assert rest_obj["allowedInstanceTypes"] == ["Standard_DS1_v2", "Standard_DS2_v2"]


def test_to_rest_object_with_allowed_instance_types_list_and_environment_string_generated():
    template = DeploymentTemplate(
        name="rest2",
        version="2.0",
        environment="env-str-2",
        environment_variables={"A": "B"},
        allowed_instance_types=["Standard_F4s_v2", "Standard_F8s_v2"],
        instance_type="Standard_F2s_v2",
        instance_count=0,
        scoring_path="/score2",
        scoring_port=6000,
    )
    template.request_settings = DummySettings(x=10)

    rest_obj = template._to_rest_object()

    assert rest_obj["environmentId"] == "env-str-2"
    assert rest_obj["environmentVariables"] == {"A": "B"}
    assert rest_obj["defaultInstanceType"] == "Standard_F2s_v2"
    assert rest_obj["instanceCount"] == 0
    assert rest_obj["scoringPath"] == "/score2"
    assert rest_obj["scoringPort"] == 6000
    assert rest_obj["requestSettings"] == {"x": 10}
    assert rest_obj["allowedInstanceTypes"] == ["Standard_F4s_v2", "Standard_F8s_v2"]


def test_to_rest_object_and_to_dict_with_other_allowed_instance_types_and_scoring_generated():
    template = DeploymentTemplate(
        name="rest3",
        version="3.0",
        instance_type="Standard_X1",
        instance_count=3,
        scoring_path="/path3",
        scoring_port=7000,
        allowed_instance_types=123,
    )

    rest_obj = template._to_rest_object()
    dict_obj = template._to_dict()

    assert rest_obj["defaultInstanceType"] == "Standard_X1"
    assert rest_obj["instanceCount"] == 3
    assert rest_obj["scoringPath"] == "/path3"
    assert rest_obj["scoringPort"] == 7000
    assert rest_obj["allowedInstanceTypes"] == ["123"]

    assert dict_obj["defaultInstanceType"] == "Standard_X1"
    assert dict_obj["instanceCount"] == 3
    assert dict_obj["scoringPath"] == "/path3"
    assert dict_obj["scoringPort"] == 7000
    assert dict_obj["allowedInstanceTypes"] == 123


def test_request_timeout_getter_various_cases():
    template = DeploymentTemplate(name="rt", version="1")

    assert template.request_timeout is None

    class DummyReqNoAttr:
        def __init__(self, value):
            self.request_timeout_ms = value

    template.request_settings = DummyReqNoAttr("1000")
    assert template.request_timeout == "1000"

    template.request_settings = DummyReqNoAttr(5000)
    assert template.request_timeout == 5

    template.request_settings = DummyReqNoAttr(0)
    assert template.request_timeout is None


def test_request_timeout_setter_creates_and_updates_settings():
    template = DeploymentTemplate(name="rt2", version="1")

    template.request_timeout = 7
    assert template.request_settings.request_timeout_ms == 7000
    assert template.request_timeout == 7

    template.request_timeout = 3
    assert template.request_settings.request_timeout_ms == 3000
    assert template.request_timeout == 3


def test_liveness_probe_properties_create_and_update():
    template = DeploymentTemplate(name="live", version="1")

    assert template.liveness_probe_initial_delay is None
    assert template.liveness_probe_period is None
    assert template.liveness_probe_timeout is None

    template.liveness_probe_initial_delay = 10
    assert template.liveness_probe_initial_delay == 10

    template.liveness_probe_period = 5
    assert template.liveness_probe_period == 5

    template.liveness_probe_timeout = 2
    assert template.liveness_probe_timeout == 2

    template.liveness_probe_initial_delay = 15
    assert template.liveness_probe_initial_delay == 15

    class DummyProbeNoAttr:
        pass

    template.liveness_probe = DummyProbeNoAttr()
    assert template.liveness_probe_initial_delay is None


def test_readiness_probe_properties_create_and_update():
    template = DeploymentTemplate(name="ready", version="1")

    assert template.readiness_probe_initial_delay is None
    assert template.readiness_probe_period is None
    assert template.readiness_probe_timeout is None

    template.readiness_probe_initial_delay = 8
    assert template.readiness_probe_initial_delay == 8

    template.readiness_probe_period = 4
    assert template.readiness_probe_period == 4

    template.readiness_probe_timeout = 1
    assert template.readiness_probe_timeout == 1

    template.readiness_probe_initial_delay = 12
    assert template.readiness_probe_initial_delay == 12

    class DummyProbeNoAttr:
        pass

    template.readiness_probe = DummyProbeNoAttr()
    assert template.readiness_probe_period is None


def test_from_rest_object_parses_string_fields_and_sets_metadata():
    rest_obj = {
        "id": "rest-id",
        "model": "my-model",
        "code_configuration": {"code": "cfg"},
        "app_insights_enabled": True,
        "template": "tmpl",
        "code_id": "code123",
        "additional_properties": {"name": "add_name", "version": "2.0"},
        "properties": {
            "name": None,
            "version": None,
            "description": "desc",
            "tags": "{\"k\": \"v\"}",
            "environmentId": "env-id",
            "environmentVariables": "{'a': 'b'}",
            "requestSettings": {},
            "livenessProbe": {},
            "readinessProbe": {},
            "instanceCount": "3",
            "defaultInstanceType": "Standard_DS3_v2",
            "deploymentTemplateType": "Managed",
            "allowedInstanceTypes": "['A', 'B']",
            "scoringPort": "8080",
            "scoringPath": "/score",
            "modelMountPath": "/mnt",
            "stage": "Active",
            "type": "restType",
        },
    }

    template = DeploymentTemplate._from_rest_object(rest_obj)

    assert template.name == "add_name"
    assert template.version == "2.0"
    assert template.description == "desc"
    assert template.tags == {"k": "v"}
    assert template.environment == "env-id"
    assert template.environment_variables == {"a": "b"}
    assert template.instance_count == 3
    assert template.default_instance_type == "Standard_DS3_v2"
    assert template.deployment_template_type == "Managed"
    assert template.allowed_instance_types == ["A", "B"]
    assert template.scoring_port == 8080
    assert template.scoring_path == "/score"
    assert template.model_mount_path == "/mnt"
    assert template.stage == "Active"
    assert template.type == "restType"

    assert template._from_service is True
    assert template.environment_id == "env-id"
    assert template.template == "tmpl"
    assert template.code_id == "code123"

    original = template._original_immutable_fields
    assert original["environment_id"] == "env-id"
    assert original["environment_variables"] == {"a": "b"}
    assert original["instance_count"] == 3
    assert original["default_instance_type"] == "Standard_DS3_v2"
    assert original["deployment_template_type"] == "Managed"
    assert original["allowed_instance_types"] == ["A", "B"]
    assert original["scoring_port"] == 8080
    assert original["scoring_path"] == "/score"
    assert original["model_mount_path"] == "/mnt"
    assert original["stage"] == "Active"
    assert original["type"] == "restType"


def test_from_rest_object_handles_invalid_allowed_instance_types_string():
    rest_obj = {
        "properties": {
            "name": "n1",
            "version": "1.0",
            "allowedInstanceTypes": "not a python literal",
        }
    }

    template = DeploymentTemplate._from_rest_object(rest_obj)

    assert template.name == "n1"
    assert template.version == "1.0"
    assert template.allowed_instance_types is None
    assert template._original_immutable_fields["allowed_instance_types"] is None


def test_to_dict_includes_metadata_and_capabilities():
    template = DeploymentTemplate(
        name="meta-tmpl",
        version="1",
        environment="env-meta",
        environment_variables={"X": "1"},
    )
    template.created_by = "user1"
    template.created_time = "2024-01-01T00:00:00Z"
    template.modified_time = "2024-01-02T00:00:00Z"
    template.capabilities = ["cap1"]
    template.model_mount_path = "/mnt/meta"
    template.request_settings = DummySettings(req="v")
    template.liveness_probe = DummySettings(live=True)
    template.readiness_probe = DummySettings(ready=True)

    dct = template._to_dict()

    assert dct["createdBy"] == "user1"
    assert dct["createdTime"] == "2024-01-01T00:00:00Z"
    assert dct["modifiedTime"] == "2024-01-02T00:00:00Z"
    assert dct["capabilities"] == ["cap1"]
    assert dct["environmentVariables"] == {"X": "1"}
    assert dct["modelMountPath"] == "/mnt/meta"
    assert dct["requestSettings"]["req"] == "v"
    assert dct["livenessProbe"]["live"] is True
    assert dct["readinessProbe"]["ready"] is True

    template.capabilities = []
    dct2 = template._to_dict()
    assert dct2["capabilities"] == []


def test_str_and_repr_use_to_dict_json():
    template = DeploymentTemplate(
        name="str-tmpl",
        version="1",
        stage="Active",
        deployment_template_type="Online",
        environment="env-str",
        environment_variables={"Y": "2"},
        instance_count=2,
        instance_type="Standard_DS1",
        scoring_path="/score",
        scoring_port=7000,
    )

    dict_repr = template._to_dict()

    s = str(template)
    r = repr(template)

    loaded_s = json.loads(s)
    loaded_r = json.loads(r)

    assert loaded_s == dict_repr
    assert loaded_r == dict_repr
    assert r == s


def test_request_timeout_without_settings_returns_none():
    template = DeploymentTemplate(name="template", version="1")
    assert template.request_timeout is None


@pytest.mark.parametrize(
    "value,expected",
    [
        ("3000", "3000"),
        (4500, 4),
        (0, None),
    ],
)
def test_request_timeout_handles_various_request_settings_values(value, expected):
    template = DeploymentTemplate(name="template", version="1")
    template.request_settings = SimpleNamespace(request_timeout_ms=value)
    assert template.request_timeout == expected


def test_request_timeout_setter_creates_and_updates(monkeypatch):
    monkeypatch.setattr(
        "azure.ai.ml.entities._deployment.deployment_template.OnlineRequestSettings",
        _StubRequestSettings,
    )
    template = DeploymentTemplate(name="template", version="1")
    template.request_timeout = 3
    assert isinstance(template.request_settings, _StubRequestSettings)
    assert template.request_settings.request_timeout_ms == 3000

    template.request_settings = SimpleNamespace(request_timeout_ms=1000)
    template.request_timeout = 2
    assert template.request_settings.request_timeout_ms == 2000


def test_liveness_probe_initial_delay_getter_and_setter(monkeypatch):
    monkeypatch.setattr(
        "azure.ai.ml.entities._deployment.deployment_template.ProbeSettings",
        _StubProbeSettings,
    )
    template = DeploymentTemplate(name="template", version="1")
    assert template.liveness_probe_initial_delay is None

    template.liveness_probe_initial_delay = 5
    assert isinstance(template.liveness_probe, _StubProbeSettings)
    assert template.liveness_probe.initial_delay == 5

    template.liveness_probe_initial_delay = 9
    assert template.liveness_probe.initial_delay == 9


def test_liveness_probe_period_getter_and_setter(monkeypatch):
    monkeypatch.setattr(
        "azure.ai.ml.entities._deployment.deployment_template.ProbeSettings",
        _StubProbeSettings,
    )
    template = DeploymentTemplate(name="template", version="1")
    assert template.liveness_probe_period is None

    template.liveness_probe_period = 10
    assert template.liveness_probe.period == 10
    assert template.liveness_probe_period == 10

    template.liveness_probe_period = 20
    assert template.liveness_probe.period == 20


def test_liveness_probe_timeout_getter_and_setter(monkeypatch):
    monkeypatch.setattr(
        "azure.ai.ml.entities._deployment.deployment_template.ProbeSettings",
        _StubProbeSettings,
    )
    template = DeploymentTemplate(name="template", version="1")
    assert template.liveness_probe_timeout is None

    template.liveness_probe_timeout = 12
    assert template.liveness_probe.timeout == 12
    assert template.liveness_probe_timeout == 12

    template.liveness_probe_timeout = 18
    assert template.liveness_probe.timeout == 18


def test_readiness_probe_initial_delay_getter_and_setter(monkeypatch):
    monkeypatch.setattr(
        "azure.ai.ml.entities._deployment.deployment_template.ProbeSettings",
        _StubProbeSettings,
    )
    template = DeploymentTemplate(name="template", version="1")
    assert template.readiness_probe_initial_delay is None

    template.readiness_probe_initial_delay = 7
    assert isinstance(template.readiness_probe, _StubProbeSettings)
    assert template.readiness_probe.initial_delay == 7

    template.readiness_probe_initial_delay = 14
    assert template.readiness_probe.initial_delay == 14


def test_readiness_probe_period_and_timeout_behaviors(monkeypatch):
    monkeypatch.setattr(
        "azure.ai.ml.entities._deployment.deployment_template.ProbeSettings",
        _StubProbeSettings,
    )
    template = DeploymentTemplate(name="template", version="1")
    assert template.readiness_probe_period is None
    assert template.readiness_probe_timeout is None

    template.readiness_probe_period = 4
    template.readiness_probe_timeout = 8
    assert template.readiness_probe.period == 4
    assert template.readiness_probe.timeout == 8
    assert template.readiness_probe_period == 4
    assert template.readiness_probe_timeout == 8

    template.readiness_probe_period = 6
    template.readiness_probe_timeout = 10
    assert template.readiness_probe.period == 6
    assert template.readiness_probe.timeout == 10

def test_to_rest_object_includes_optional_fields():
    template = DeploymentTemplate(name="template", version="1")
    template.stage = "Archived"
    template.deployment_template_type = "custom"
    template.tags = {"tier": "prod"}
    template.environment_id = "env-id"
    template.environment = "ignored"
    template.model_mount_path = "/model"
    template.request_settings = DummyDictConvertible({"timeout": 100})
    template.liveness_probe = DummyDictConvertible({"initialDelaySeconds": 5})
    template.readiness_probe = DummyDictConvertible({"timeoutSeconds": 7})
    template.instance_type = "standard"
    template.instance_count = 3
    template.scoring_path = "/score"
    template.scoring_port = 8080
    template.model = "my-model"
    template.code_configuration = {"code": "repository"}
    template.app_insights_enabled = False
    result = template._to_rest_object()
    assert result["stage"] == "Archived"
    assert result["deploymentTemplateType"] == "custom"
    assert result["tags"] == {"tier": "prod"}
    assert result["environmentId"] == "env-id"
    assert result["modelMountPath"] == "/model"
    assert result["requestSettings"] == {"timeout": 100}
    assert result["livenessProbe"] == {"initialDelaySeconds": 5}
    assert result["readinessProbe"] == {"timeoutSeconds": 7}
    assert result["defaultInstanceType"] == "standard"
    assert result["instanceCount"] == 3
    assert result["scoringPath"] == "/score"
    assert result["scoringPort"] == 8080
    assert result["model"] == "my-model"
    assert result["codeConfiguration"] == {"code": "repository"}
    assert result["appInsightsEnabled"] is False

def test_to_rest_object_allowed_instance_types_variants():
    template = DeploymentTemplate(name="template", version="1")
    template.allowed_instance_types = "small medium"
    result = template._to_rest_object()
    assert result["allowedInstanceTypes"] == ["small", "medium"]
    template.allowed_instance_types = ["x-large"]
    result = template._to_rest_object()
    assert result["allowedInstanceTypes"] == ["x-large"]
    template.allowed_instance_types = 5
    result = template._to_rest_object()
    assert result["allowedInstanceTypes"] == ["5"]

def test_to_dict_includes_metadata_and_environment_fallback():
    template = DeploymentTemplate(name="template", version="1")
    template.environment = "env-str"
    template.tags = {"team": "ml"}
    template.stage = "Active"
    template.deployment_template_type = "stage"
    template.created_by = "creator"
    template.created_time = "created-time"
    template.modified_time = "modified-time"
    template.capabilities = ["cap1"]
    template.environment_variables = {"ENV": "value"}
    template.model_mount_path = "/mnt"
    template.request_settings = DummyDictConvertible({"timeout": 100})
    template.liveness_probe = DummyDictConvertible({"threshold": 1})
    template.readiness_probe = DummyDictConvertible({"threshold": 2})
    template.allowed_instance_types = ["A", "B"]
    template.instance_type = "standard"
    template.instance_count = 2
    template.scoring_path = "/score"
    template.scoring_port = 9001
    result = template._to_dict()
    assert result["stage"] == "Active"
    assert result["deploymentTemplateType"] == "stage"
    assert result["tags"] == {"team": "ml"}
    assert result["environmentId"] == "env-str"
    assert result["createdBy"] == "creator"
    assert result["createdTime"] == "created-time"
    assert result["modifiedTime"] == "modified-time"
    assert result["capabilities"] == ["cap1"]
    assert result["environmentVariables"] == {"ENV": "value"}
    assert result["modelMountPath"] == "/mnt"
    assert result["requestSettings"] == {"timeout": 100}
    assert result["livenessProbe"] == {"threshold": 1}
    assert result["readinessProbe"] == {"threshold": 2}
    assert result["allowedInstanceTypes"] == ["A", "B"]
    assert result["defaultInstanceType"] == "standard"
    assert result["instanceCount"] == 2
    assert result["scoringPath"] == "/score"
    assert result["scoringPort"] == 9001

def test_to_rest_object_includes_stage_and_template_type_and_allowed_instance_types():
    template = DeploymentTemplate(
        name="tpl",
        version="1.0",
        stage="Archived",
        deployment_template_type="custom",
    )
    template.environment_id = "env-123"
    template.environment = "should-not-appear"
    template.allowed_instance_types = "typeA typeB"
    template.environment_variables = {"ENV": "VALUE"}
    template.request_settings = DummyDictConvertible({"timeout": 100})
    template.model_mount_path = "/model"
    template.model = "model123"
    template.code_configuration = {"entry_script": "score.py"}
    template.app_insights_enabled = True

    result = template._to_rest_object()

    assert result["stage"] == "Archived"
    assert result["deploymentTemplateType"] == "custom"
    assert result["environmentId"] == "env-123"
    assert result["environmentVariables"] == {"ENV": "VALUE"}
    assert result["requestSettings"] == {"timeout": 100}
    assert result["modelMountPath"] == "/model"
    assert result["model"] == "model123"
    assert result["codeConfiguration"] == {"entry_script": "score.py"}
    assert result["appInsightsEnabled"] is True
    assert result["allowedInstanceTypes"] == ["typeA", "typeB"]

def test_to_rest_object_uses_environment_when_environment_id_missing():
    template = DeploymentTemplate(name="tpl", version="2.0")
    template.environment = "env-fallback"

    result = template._to_rest_object()

    assert "stage" not in result
    assert result["environmentId"] == "env-fallback"

def test_to_dict_includes_metadata_and_probe_settings_with_default_instance():
    template = DeploymentTemplate(name="tpl", version="3.0")
    template.environment_id = "env-id"
    template.created_by = "creator"
    template.created_time = "2025-01-01T00:00:00Z"
    template.modified_time = "2025-02-02T00:00:00Z"
    template.capabilities = []
    template.environment_variables = {"VAR": "VAL"}
    template.model_mount_path = "/mounted"
    template.request_settings = DummyDictConvertible({"timeoutMs": 30})
    template.liveness_probe = DummyDictConvertible({"initial_delay": 5})
    template.readiness_probe = DummyDictConvertible({"timeout": 10})
    template.allowed_instance_types = ["typeA", "typeB"]
    template.default_instance_type = "default-size"
    template.instance_count = 4
    template.scoring_path = "/score"
    template.scoring_port = 9000

    result = template._to_dict()

    assert result["createdBy"] == "creator"
    assert result["createdTime"] == "2025-01-01T00:00:00Z"
    assert result["modifiedTime"] == "2025-02-02T00:00:00:00Z" if False else result["modifiedTime"] == "2025-02-02T00:00:00Z"
    assert result["capabilities"] == []
    assert result["environmentVariables"] == {"VAR": "VAL"}
    assert result["modelMountPath"] == "/mounted"
    assert result["requestSettings"] == {"timeoutMs": 30}
    assert result["livenessProbe"] == {"initial_delay": 5}
    assert result["readinessProbe"] == {"timeout": 10}
    assert result["allowedInstanceTypes"] == ["typeA", "typeB"]
    assert result["defaultInstanceType"] == "default-size"
    assert result["instanceCount"] == 4
    assert result["scoringPath"] == "/score"
    assert result["scoringPort"] == 9000

def test_to_dict_uses_instance_type_when_default_missing():
    template = DeploymentTemplate(name="tpl", version="4.0")
    template.instance_type = "standard"

    result = template._to_dict()

    assert result["defaultInstanceType"] == "standard"