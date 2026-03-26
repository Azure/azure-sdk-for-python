import json
from types import SimpleNamespace

import pytest

from azure.ai.ml._restclient.v2022_05_01.models import ManagedServiceIdentity
from azure.ai.ml.constants._common import WorkspaceDiscoveryUrlKey
from azure.ai.ml._utils import utils
from azure.ai.ml._utils.utils import (
    ListViewType,
    MlException,
    MFE_PATH_PREFIX,
    _get_base_urls_from_discovery_service,
    _get_mfe_base_url_from_batch_endpoint,
    _get_mfe_base_url_from_discovery_service,
    _get_mfe_base_url_from_registry_discovery_service,
    _get_workspace_base_url,
    append_double_curly,
    camel_to_snake,
    convert_identity_dict,
    download_text_from_url,
    float_to_str,
    from_iso_duration_format_min_sec,
    hash_dict,
    map_single_brackets_and_warn,
    module_logger,
    modified_operation_client,
    snake_to_camel,
    snake_to_kebab,
    snake_to_pascal,
    strip_double_curly,
)


class _StubResponse:
    def __init__(self, status_code, text_value):
        self.status_code = status_code
        self._text_value = text_value

    def text(self):
        return self._text_value


class _StubPipeline:
    def __init__(self, response):
        self._response = response
        self.last_kwargs = {}

    def get(self, uri, **kwargs):
        self.last_kwargs = kwargs
        return self._response


class _FakePipeline:
    def __init__(self):
        self.policies = None

    def with_policies(self, **kwargs):
        self.policies = kwargs
        return self


class _FakeClient:
    def __init__(self):
        self._base_url = "https://original"


class _FakeOperation:
    def __init__(self):
        self._client = _FakeClient()


def test_snake_to_pascal_handles_none_simple_and_multiple():
    assert snake_to_pascal(None) is None
    assert snake_to_pascal("foo_bar") == "FooBar"
    assert snake_to_pascal("foo_bar,baz_qux") == "FooBar,BazQux"


def test_snake_to_kebab_handles_values_and_none():
    assert snake_to_kebab("a_b_c") == "a-b-c"
    assert snake_to_kebab(None) is None


def test_camel_to_snake_converts_and_handles_none():
    assert camel_to_snake("HTTPRequest") == "http_request"
    assert camel_to_snake(None) is None


def test_snake_to_camel_handles_values_and_none():
    assert snake_to_camel("foo_bar") == "fooBar"
    assert snake_to_camel(None) is None


def test_float_to_str_preserves_precision():
    assert float_to_str(1.23e-5) == "0.0000123"


def test_download_text_from_url_returns_empty_for_404():
    pipeline = _StubPipeline(_StubResponse(404, "not found"))
    assert download_text_from_url("https://example.com", pipeline) == ""


def test_download_text_from_url_respects_timeout_tuple():
    pipeline = _StubPipeline(_StubResponse(200, "payload"))
    result = download_text_from_url("https://example.com", pipeline, timeout=(1.5, 3.5))
    assert result == "payload"
    assert pipeline.last_kwargs == {"read_timeout": 3.5, "connection_timeout": 1.5}


def test_discovery_service_urls_and_mfe_paths(monkeypatch):
    base_urls = {WorkspaceDiscoveryUrlKey.API: "https://api.azure.com"}
    discovery_url = "https://discovery"
    workspace_operations = SimpleNamespace(
        get=lambda name: SimpleNamespace(discovery_url=discovery_url)
    )
    pipeline = _FakePipeline()

    def fake_download(source_uri, pipeline_arg, **kwargs):
        assert source_uri == discovery_url
        assert pipeline_arg is pipeline
        return json.dumps(base_urls)

    monkeypatch.setattr(utils, "download_text_from_url", fake_download)

    result = _get_base_urls_from_discovery_service(workspace_operations, "workspace", pipeline)
    assert result == base_urls

    monkeypatch.setattr(
        utils, "_get_base_urls_from_discovery_service", lambda *_args, **_kwargs: base_urls
    )
    assert (
        _get_mfe_base_url_from_discovery_service(None, "workspace", pipeline)
        == f"{base_urls[WorkspaceDiscoveryUrlKey.API]}{MFE_PATH_PREFIX}"
    )
    assert (
        _get_mfe_base_url_from_registry_discovery_service(None, "workspace", pipeline)
        == base_urls[WorkspaceDiscoveryUrlKey.API]
    )
    assert _get_workspace_base_url(None, "workspace", pipeline) == base_urls[WorkspaceDiscoveryUrlKey.API]


def test_batch_endpoint_mfe_url_and_modified_client():
    endpoint = SimpleNamespace(scoring_uri="https://example.azure.com/subscriptions/123/resource")
    assert _get_mfe_base_url_from_batch_endpoint(endpoint) == "https://example.azure.com"

    class _Client:
        def __init__(self, base_url):
            self._base_url = base_url

    class _Operation:
        def __init__(self, base_url):
            self._client = _Client(base_url)

    operation = _Operation("https://original.azure.com")
    with modified_operation_client(operation, "https://override.azure.com"):
        assert operation._client._base_url == "https://override.azure.com"
    assert operation._client._base_url == "https://original.azure.com"

    with modified_operation_client(operation, None):
        assert operation._client._base_url == "https://original.azure.com"
    assert operation._client._base_url == "https://original.azure.com"


def test_hash_dict_omits_keys_and_is_deterministic():
    sample = {"b": 2, "a": 1, "c": {"nested": 3}}
    full_hash = hash_dict(sample)
    assert full_hash == hash_dict({"a": 1, "b": 2, "c": {"nested": 3}})
    omitted_hash = hash_dict(sample, keys_to_omit=["b"])
    assert omitted_hash == hash_dict({"a": 1, "c": {"nested": 3}})
    assert full_hash != omitted_hash


def test_convert_identity_dict_variants_and_curly_helpers():
    default_identity = convert_identity_dict(None)
    assert default_identity.type == "SystemAssigned"

    none_identity = ManagedServiceIdentity(type="none")
    normalized = convert_identity_dict(none_identity)
    assert normalized.type == "SystemAssigned"

    list_identity = ManagedServiceIdentity(
        type="user_assigned",
        user_assigned_identities=[{"resource_id": "/subscriptions/id"}],
    )
    converted = convert_identity_dict(list_identity)
    assert converted.user_assigned_identities == {"/subscriptions/id": {}}
    assert converted.type == snake_to_camel("user_assigned")

    dict_identity = ManagedServiceIdentity(
        type="user_assigned",
        user_assigned_identities={"/subscriptions/another": {}},
    )
    assert convert_identity_dict(dict_identity) is dict_identity

    assert strip_double_curly("${{value}}") == "value"
    assert append_double_curly("value") == "${{value}}"


def test_discovery_service_url_helpers(monkeypatch):
    base_url = "https://example.com"
    monkeypatch.setattr(
        utils,
        "_get_base_urls_from_discovery_service",
        lambda *_args, **_kwargs: {WorkspaceDiscoveryUrlKey.API: base_url},
    )
    endpoint = type("BatchEndpoint", (), {"scoring_uri": f"{base_url}/subscriptions/abc"})()

    assert _get_mfe_base_url_from_discovery_service(None, "ws", None) == f"{base_url}{MFE_PATH_PREFIX}"
    assert _get_mfe_base_url_from_registry_discovery_service(None, "ws", None) == base_url
    assert _get_workspace_base_url(None, "ws", None) == base_url
    assert _get_mfe_base_url_from_batch_endpoint(endpoint) == base_url


def test_modified_operation_client_restores_url():
    operation = _FakeOperation()
    with modified_operation_client(operation, "https://custom"):
        assert operation._client._base_url == "https://custom"
    assert operation._client._base_url == "https://original"


def test_modified_operation_client_ignores_empty_url():
    operation = _FakeOperation()
    with modified_operation_client(operation, ""):
        assert operation._client._base_url == "https://original"
    assert operation._client._base_url == "https://original"


def test_from_iso_duration_format_min_sec():
    assert from_iso_duration_format_min_sec("PT3M4.567S") == "3m 4s"


def test_hash_dict_omit_keys_and_ordering():
    payload = {"b": 2, "a": 1}
    default_hash = hash_dict(payload)
    reordered_hash = hash_dict({"a": 1, "b": 2})
    assert default_hash == reordered_hash
    omitted_hash = hash_dict(payload, keys_to_omit=["b"])
    assert omitted_hash != default_hash


def test_convert_identity_dict_variants():
    assert convert_identity_dict(None).type == "SystemAssigned"

    system_assigned = convert_identity_dict(ManagedServiceIdentity(type="system_assigned"))
    assert system_assigned.type == "SystemAssigned"

    list_identity = ManagedServiceIdentity(
        type="user_assigned",
        user_assigned_identities=[{"resource_id": "/subscriptions/123"}],
    )
    list_converted = convert_identity_dict(list_identity)
    assert "/subscriptions/123" in list_converted.user_assigned_identities
    assert list_converted.type == snake_to_camel("user_assigned")

    dict_identity = ManagedServiceIdentity(
        type="user_assigned",
        user_assigned_identities={"/subscriptions/123": {"foo": "bar"}},
    )
    dict_converted = convert_identity_dict(dict_identity)
    assert dict_converted.user_assigned_identities == dict_identity.user_assigned_identities


def test_strip_and_append_double_curly():
    assert strip_double_curly("${{payload}}") == "payload"
    assert append_double_curly("payload") == "${{payload}}"


def test_map_single_brackets_and_warn(monkeypatch):
    warnings = []
    monkeypatch.setattr(module_logger, "warning", lambda msg: warnings.append(msg))
    command = "{inputs.value} {outputs.artifacts} {search_space.choice}"
    result = map_single_brackets_and_warn(command)

    assert "${{inputs.value}}" in result
    assert "${{outputs.artifacts}}" in result
    assert "${{search_space.choice}}" in result
    assert warnings == ["Use of {} for parameters is deprecated, instead use ${{}}."]


class DummyLogger:
    def __init__(self):
        self.infos = []
        self.warnings = []

    def info(self, message):
        self.infos.append(message)

    def warning(self, message):
        self.warnings.append(message)


def test_transform_dict_keys_recurses():
    data = {"outer_key": {"inner_key": 42}}
    transformed = utils.transform_dict_keys(data, lambda key: key.replace("_", "-"))
    assert "outer-key" in transformed
    assert transformed["outer-key"]["inner-key"] == 42
    assert "inner_key" in data["outer_key"]


def test_merge_dict_merges_nested_dicts():
    origin = {"nested": {"value": 1}}
    delta = {"nested": {"value": 2}, "extra": {"leaf": "x"}}
    merged = utils.merge_dict(origin, delta)
    assert merged["nested"]["value"] == 2
    assert merged["extra"]["leaf"] == "x"
    assert origin["nested"]["value"] == 2


def test_merge_dict_overwrites_non_dict_values():
    origin = {"nested": {"value": 1}}
    delta = {"nested": 10}
    merged = utils.merge_dict(origin, delta)
    assert merged["nested"] == 10
    assert isinstance(origin["nested"], dict)


def test_retry_retries_until_success(monkeypatch):
    monkeypatch.setattr(utils.time, "sleep", lambda _: None)
    logger = DummyLogger()
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise ValueError("boom")
        return "ok"

    decorated = utils.retry(ValueError, "fail", logger, max_attempts=2, delay_multiplier=0)(flaky)
    assert decorated() == "ok"
    assert logger.infos
    assert any("Operation failed. Retrying" in info for info in logger.infos)


def test_retry_warns_and_rethrows_when_exhausted(monkeypatch):
    monkeypatch.setattr(utils.time, "sleep", lambda _: None)
    logger = DummyLogger()

    def always_fail():
        raise RuntimeError("boom")

    decorated = utils.retry(RuntimeError, "cannot recover", logger, max_attempts=1, delay_multiplier=0)(always_fail)
    with pytest.raises(RuntimeError):
        decorated()
    assert logger.warnings == ["cannot recover"]


def test_get_list_view_type_conflict_raises():
    with pytest.raises(MlException) as excinfo:
        utils.get_list_view_type(True, True)
    assert "Cannot provide both archived-only and include-archived." in str(excinfo.value)


def test_get_list_view_type_returns_expected_values():
    assert utils.get_list_view_type(True, False) == ListViewType.ALL
    assert utils.get_list_view_type(False, True) == ListViewType.ARCHIVED_ONLY
    assert utils.get_list_view_type(False, False) == ListViewType.ACTIVE_ONLY
