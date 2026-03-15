# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Test that every public method on AIProjectClient.beta sub-clients sends the
'Foundry-Features' HTTP request header.

This test does NOT make real network calls. It uses a custom transport that
captures the outgoing HttpRequest and raises a sentinel exception, so no
actual HTTP traffic occurs.

Sub-clients and their methods are discovered dynamically at collection time via
introspection, so the test automatically covers new methods added to .beta and
stops covering methods that are removed — no manual updates needed.

Discovery strategy:
  - Non-callable public attributes of `client.beta` are sub-clients
    (e.g. evaluation_taxonomies, memory_stores, …).
  - Public bound methods on each sub-client are the API methods to test.
  - Fake arguments are inferred from each method's signature: required
    parameters (those with no default, or whose default is the _Unset sentinel)
    receive a type-appropriate placeholder value.

Run with:  pytest tests/beta_operations/test_foundry_features_header.py -s
The -s flag (or --capture=no) is required to see the printed report.
"""

import inspect
from typing import Any, Iterator, List, Tuple, Union, get_origin

import pytest
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpTransport
from azure.ai.projects import AIProjectClient
from azure.ai.projects.operations._operations import _Unset  # internal sentinel


FAKE_ENDPOINT = "https://fake-account.services.ai.azure.com/api/projects/fake-project"
FOUNDRY_FEATURES_HEADER = "Foundry-Features"

# Expected Foundry-Features header value for each .beta sub-client.
# If a new sub-client is added to .beta and is missing from this mapping, the test will
# fail at collection time with a message asking you to add it here.
EXPECTED_FOUNDRY_FEATURES: dict[str, str] = {
    "evaluation_taxonomies": "Evaluations=V1Preview",
    "evaluators": "Evaluations=V1Preview",
    "insights": "Insights=V1Preview",
    "memory_stores": "MemoryStores=V1Preview",
    "red_teams": "RedTeams=V1Preview",
    "schedules": "Schedules=V1Preview",
    "toolsets": "Toolsets=V1Preview",
}

# Collects (label, header_value) pairs during the test run; printed as a report at the end.
_report: List[Tuple[str, str]] = []
_report_max_label_len: int = 0


# ---------------------------------------------------------------------------
# Helpers: fake credential + capturing transport
# ---------------------------------------------------------------------------


class _RequestCaptured(Exception):
    """Sentinel raised by CapturingTransport so tests never block on I/O."""

    def __init__(self, request: Any) -> None:
        self.request = request
        super().__init__("request captured")


class CapturingTransport(HttpTransport):
    """Transport that captures the outgoing request and raises _RequestCaptured."""

    def send(self, request: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        raise _RequestCaptured(request)

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __enter__(self) -> "CapturingTransport":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class FakeCredential:
    """Returns a fake, non-expiring token so the auth policy doesn't fail."""

    def get_token(self, *args: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", 9_999_999_999)


# ---------------------------------------------------------------------------
# Fake-argument builder
# ---------------------------------------------------------------------------


def _fake_for_param(param: inspect.Parameter) -> Any:
    """Return a plausible fake value for a single required parameter.

    Resolution order:
      - Union types (e.g. Union[Model, JSON, IO[bytes]])  -> {} (JSON body)
      - list / List[...]                                  -> []
      - str                                               -> "fake-value"
      - int                                               -> 0
      - bool                                              -> False
      - anything else (model classes, etc.)               -> {}
    """
    ann = param.annotation
    if ann is inspect.Parameter.empty:
        return "fake-value"

    origin = get_origin(ann)
    if origin is Union:
        return {}
    if origin is list:
        return []
    if ann is str:
        return "fake-value"
    if ann is int:
        return 0
    if ann is bool:
        return False
    return {}


def _make_fake_call(method: Any) -> Any:
    """Return a zero-argument callable that invokes *method* with fake args.

    Only required parameters (no default, or default is _Unset) are populated.
    Optional ones are omitted so as not to trigger extra validation paths.
    """
    sig = inspect.signature(method)
    args: list[Any] = []
    kwargs: dict[str, Any] = {}

    for pname, param in sig.parameters.items():
        if pname in ("self", "cls"):
            continue
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue

        is_required = param.default is inspect.Parameter.empty or param.default is _Unset
        if not is_required:
            continue

        fake = _fake_for_param(param)
        if param.kind in (param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY):
            args.append(fake)
        else:  # KEYWORD_ONLY
            kwargs[pname] = fake

    return lambda: method(*args, **kwargs)


# ---------------------------------------------------------------------------
# Core capture / assertion logic
# ---------------------------------------------------------------------------


def _capture(call: Any) -> Any:
    """Call *call()* and return the captured HttpRequest.

    Most methods raise _RequestCaptured immediately (transport is hit
    synchronously).  Lazy methods that return an ItemPaged only call the
    transport when the first item is fetched, so we trigger that with next().
    """
    try:
        result = call()
    except _RequestCaptured as exc:
        return exc.request

    # call() returned without raising -> lazy iterable (ItemPaged)
    try:
        next(iter(result))
    except _RequestCaptured as exc:
        return exc.request
    except StopIteration:
        raise AssertionError("Iterator exhausted without the transport being called") from None

    raise AssertionError("Transport was never called")


def _assert_header(label: str, call: Any, expected_value: str) -> str:
    """Invoke *call*, assert the Foundry-Features header equals *expected_value*,
    record the result for the end-of-session report, and return the header value.
    Fails the test if the header is absent, empty, or has an unexpected value.
    """
    request = _capture(call)

    header_value: str | None = request.headers.get(FOUNDRY_FEATURES_HEADER)
    assert header_value, (
        f"{label}: REST call was made but '{FOUNDRY_FEATURES_HEADER}' header is "
        f"missing or empty.\nActual headers: {dict(request.headers)}"
    )
    assert header_value == expected_value, (
        f"{label}: expected '{FOUNDRY_FEATURES_HEADER}: {expected_value}' "
        f"but got '{header_value}'"
    )
    global _report_max_label_len
    _report_max_label_len = max(_report_max_label_len, len(label))
    _report.append((label, header_value))
    return header_value


# ---------------------------------------------------------------------------
# Dynamic test-case discovery (runs at collection time, not at test time)
# ---------------------------------------------------------------------------


def _discover_test_cases() -> list[pytest.param]:
    """Introspect client.beta and yield one pytest.param per public method.

    Steps:
      1. Instantiate a temporary client (no network calls are made here).
      2. Non-callable public attributes of client.beta are sub-clients.
      3. Public bound methods on each sub-client are the API methods to test.
    """
    temp = AIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=FakeCredential(),  # type: ignore[arg-type]
        transport=CapturingTransport(),
    )

    cases: list[pytest.param] = []
    for sc_name in sorted(dir(temp.beta)):
        if sc_name.startswith("_"):
            continue
        sc = getattr(temp.beta, sc_name)
        # Sub-clients are non-callable objects (instances of operations classes).
        # Skip anything callable (e.g. methods directly on BetaOperations itself).
        if callable(sc):
            continue

        assert sc_name in EXPECTED_FOUNDRY_FEATURES, (
            f"New .beta sub-client '{sc_name}' discovered but not found in EXPECTED_FOUNDRY_FEATURES. "
            f"Please add an entry for '.beta.{sc_name}' to the EXPECTED_FOUNDRY_FEATURES mapping in this test file."
        )

        for m_name in sorted(dir(sc)):
            if m_name.startswith("_"):
                continue
            method = getattr(sc, m_name)
            if not inspect.ismethod(method):
                continue

            label = f".beta.{sc_name}.{m_name}()"
            expected = EXPECTED_FOUNDRY_FEATURES[sc_name]
            cases.append(pytest.param(label, sc_name, m_name, expected, id=label))

    return cases


_TEST_CASES = _discover_test_cases()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client() -> Iterator[AIProjectClient]:
    with AIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=FakeCredential(),  # type: ignore[arg-type]
        transport=CapturingTransport(),
    ) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def _print_report() -> Iterator[None]:
    """Print the full Foundry-Features header report after all tests finish."""
    yield
    if _report:
        print("\n\nFoundry-Features header report:")
        for label, header_value in sorted(_report):
            print(f"{label:<{_report_max_label_len}}  |  \"{header_value}\"")


# ---------------------------------------------------------------------------
# Single parametrized test — one case per discovered public method
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label,subclient_name,method_name,expected_header_value", _TEST_CASES)
def test_foundry_feature_header(
    client: AIProjectClient,
    label: str,
    subclient_name: str,
    method_name: str,
    expected_header_value: str,
) -> None:
    """Assert that *method_name* on .beta.<subclient_name> sends the expected Foundry-Features value."""
    sc = getattr(client.beta, subclient_name)
    method = getattr(sc, method_name)
    _assert_header(label, _make_fake_call(method), expected_header_value)