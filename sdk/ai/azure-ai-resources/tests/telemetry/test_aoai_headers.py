import pytest

from azure.ai.resources._telemetry.aoai_injector import (
    get_aoai_telemetry_headers,
    inject_openai_headers,
    IS_LEGACY_OPENAI,
)


@pytest.mark.unittest
def test_inject_openai_headers_sync():
    @inject_openai_headers
    def f(**kwargs):
        return kwargs

    if IS_LEGACY_OPENAI:
        headers = "headers"
        kwargs_1 = {"headers": {"a": 1, "b": 2}}
    else:
        headers = "extra_headers"
        kwargs_1 = {"extra_headers": {"a": 1, "b": 2}}

    injected_headers = get_aoai_telemetry_headers()
    assert f(a=1, b=2) == {"a": 1, "b": 2, headers: injected_headers}

    merged_headers = {**injected_headers, "a": 1, "b": 2}
    assert f(**kwargs_1) == {headers: merged_headers}
