# pylint: disable=line-too-long
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live orchestration for the external Foundry SDK health test plans."""

import json
import os
import time
from base64 import urlsafe_b64decode
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pytest
from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential

_BASE_URL = "https://ca-foundry-sdk-health-backend.jollycoast-bec92a3a.westus.azurecontainerapps.io"
_TOKEN_SCOPE = "https://management.azure.com/.default"
_REGION = "westus2"
_BRANCH = "main"
_POLL_INTERVAL_SECONDS = 10 * 60
_REPORT_URL = "https://aka.ms/fhd"


def _token_identity(token: str) -> dict[str, Any]:
    payload = token.split(".")[1]
    claims = json.loads(urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    return {name: claims.get(name) for name in ("tid", "appid", "azp", "oid", "aud")}


def _request_json(credential: TokenCredential, method: str, url: str) -> dict[str, Any]:
    token = credential.get_token(_TOKEN_SCOPE).token
    request = Request(
        url,
        method=method,
        headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
    )
    try:
        with urlopen(
            request, timeout=60
        ) as response:  # nosec B310 - URL is a fixed HTTPS service endpoint
            return json.load(response)
    except HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        if exc.code in (401, 403):
            raise RuntimeError(
                "Foundry SDK health API authentication failed. Ensure the pipeline identity is allowed to call "
                f"the API with scope {_TOKEN_SCOPE}. HTTP {exc.code}: {response_body}"
            ) from exc
        raise RuntimeError(
            f"Foundry SDK health API returned HTTP {exc.code}: {response_body}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            f"Foundry SDK health API request failed: {exc.reason}"
        ) from exc


def _run_health_test_plans(
    credential: TokenCredential,
    *,
    request_json: Callable[[TokenCredential, str, str], dict[str, Any]] = _request_json,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    run_url = (
        f"{_BASE_URL}/tests/plans/run/region/{_REGION}?{urlencode({'branch': _BRANCH})}"
    )
    run_result = request_json(credential, "POST", run_url)
    print(
        f"Queued {run_result.get('updated', 0)} Foundry SDK health test plans "
        f"for region {_REGION} and branch {_BRANCH}."
    )

    status_url = f"{_BASE_URL}/tests/plans/run/active?{urlencode({'region': _REGION})}"
    while True:
        status = request_json(credential, "GET", status_url)
        has_running_tests = status.get("has_running_tests")
        if not isinstance(has_running_tests, bool):
            raise RuntimeError(
                "Foundry SDK health API response did not contain boolean 'has_running_tests'."
            )
        if not has_running_tests:
            print(
                f"Foundry SDK health tests finished. Check the test report at {_REPORT_URL}"
            )
            return

        print(
            f"Foundry SDK health tests are still running; checking again in 10 minutes. Report: {_REPORT_URL}"
        )
        sleep(_POLL_INTERVAL_SECONDS)


@pytest.mark.live_test_only
@pytest.mark.foundry_sdk_health_live
@pytest.mark.skipif(
    os.environ.get("RUN_FOUNDRY_SDK_HEALTH_TEST", "").lower() != "true",
    reason="Only the dedicated live pipeline may queue Foundry SDK health test plans.",
)
def test_foundry_sdk_health_main_westus2() -> None:
    """Queue and await the main-branch Foundry SDK health plans in westus2."""
    with DefaultAzureCredential() as credential:
        token = credential.get_token(_TOKEN_SCOPE).token
        print(
            f"Foundry SDK health caller identity: {json.dumps(_token_identity(token), sort_keys=True)}"
        )
        _run_health_test_plans(credential)


def test_run_health_test_plans_polls_until_complete(capsys) -> None:
    """Polling waits ten minutes between active responses and reports completion."""
    responses = iter(
        [
            {"updated": 2, "has_running_tests": True},
            {"region": _REGION, "matched": 2, "has_running_tests": True},
            {"region": _REGION, "matched": 2, "has_running_tests": False},
        ]
    )
    requests = []
    sleeps = []

    def fake_request(credential, method, url):
        requests.append((credential, method, url))
        return next(responses)

    credential = object()
    _run_health_test_plans(credential, request_json=fake_request, sleep=sleeps.append)  # type: ignore[arg-type]

    assert [request[1] for request in requests] == ["POST", "GET", "GET"]
    assert requests[0][2].endswith("/tests/plans/run/region/westus2?branch=main")
    assert requests[1][2].endswith("/tests/plans/run/active?region=westus2")
    assert sleeps == [_POLL_INTERVAL_SECONDS]
    assert f"Check the test report at {_REPORT_URL}" in capsys.readouterr().out


def test_token_identity_returns_only_allowlist_claims() -> None:
    """Token diagnostics expose identity claims without exposing the JWT."""
    payload = "eyJ0aWQiOiAidGVuYW50IiwgImFwcGlkIjogImFwcCIsICJvaWQiOiAib2JqZWN0IiwgImF1ZCI6ICJhdWQifQ"
    token = f"header.{payload}.signature"

    assert _token_identity(token) == {
        "tid": "tenant",
        "appid": "app",
        "azp": None,
        "oid": "object",
        "aud": "aud",
    }
