# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from openai import APIStatusError, AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion

from azure.ai.evaluation._legacy.prompty import AsyncPrompty
from azure.ai.evaluation._legacy.prompty._exceptions import WrappedOpenAIError
from azure.ai.evaluation._legacy.prompty._utils import openai_error_retryable


def _downstream_body(**overrides: Any) -> Dict[str, Any]:
    """Build a synthetic, structured downstream error."""
    return {
        "type": "CustomerManagedDownstreamError",
        "customerManagedDownstreamIssue": True,
        "innerStatusCode": 429,
        **overrides,
    }


def _status_error(status: int, body: object, retry_after: Optional[str] = None) -> APIStatusError:
    """Use the OpenAI client's error decoding with a synthetic HTTP response."""
    headers = {"x-request-id": "synthetic-request"}
    if retry_after is not None:
        headers["Retry-After"] = retry_after
    response = httpx.Response(
        status, request=httpx.Request("POST", "https://example.invalid/chat/completions"), headers=headers
    )
    with OpenAI(api_key="not-a-real-key") as client:
        return client._make_status_error("Synthetic service error", body=body, response=response)


@pytest.mark.unittest
class TestPromptyRetries:
    """Exercise retry classification and the real bounded prompty retry loop."""

    @pytest.mark.parametrize(
        "status,body,expected",
        [
            pytest.param(429, {"type": "rate_limit_exceeded"}, True, id="direct-429"),
            pytest.param(424, _downstream_body(), True, id="wrapped-429"),
            pytest.param(424, {"error": _downstream_body()}, True, id="openai-error-envelope"),
            pytest.param(424, {}, False, id="unrelated-424"),
            pytest.param(424, None, False, id="missing-body"),
            pytest.param(424, [_downstream_body()], False, id="list-body"),
            pytest.param(424, str(_downstream_body()), False, id="string-body"),
            pytest.param(424, {"type": "CustomerManagedDownstreamError"}, False, id="missing-fields"),
            pytest.param(424, _downstream_body(innerStatusCode=None), False, id="missing-inner-status"),
            pytest.param(424, _downstream_body(innerStatusCode="429"), False, id="string-inner-status"),
            pytest.param(424, _downstream_body(innerStatusCode=503), False, id="other-inner-status"),
            pytest.param(424, _downstream_body(customerManagedDownstreamIssue=None), False, id="missing-marker"),
            pytest.param(424, _downstream_body(customerManagedDownstreamIssue=False), False, id="false-marker"),
            pytest.param(424, _downstream_body(customerManagedDownstreamIssue="true"), False, id="string-marker"),
            pytest.param(424, _downstream_body(customerManagedDownstreamIssue=1), False, id="integer-marker"),
            pytest.param(424, _downstream_body(type="OtherError"), False, id="wrong-type"),
            pytest.param(424, _downstream_body(type=None), False, id="missing-type"),
            pytest.param(424, _downstream_body(innerError="not-json"), True, id="unstructured-inner-error"),
            pytest.param(424, _downstream_body(innerError={"type": 1}), True, id="non-string-inner-type"),
            pytest.param(404, _downstream_body(), False, id="outer-404"),
            pytest.param(500, {}, True, id="server-error"),
        ],
    )
    def test_status_classification(self, status: int, body: object, expected: bool) -> None:
        """Only explicitly identified downstream throttling extends the retryable statuses."""
        error = _status_error(status, body)
        original_body = deepcopy(error.body)
        retries = [0]
        assert openai_error_retryable(error, 0, retries, 3) == (expected, 3)
        assert retries == [0]
        assert error.body == original_body
        assert error.status_code == error.response.status_code == status
        assert error.request is error.response.request
        assert error.request_id == "synthetic-request"

    @pytest.mark.parametrize("quota", ["insufficient_quota", "Insufficient_Quota", "INSUFFICIENT_QUOTA"])
    @pytest.mark.parametrize("field", ["type", "code"])
    @pytest.mark.parametrize("wrapper", [None, "error", "innerError", "innererror"])
    def test_hard_quota_is_not_retried(self, quota: str, field: str, wrapper: Optional[str]) -> None:
        """Quota subtypes remain terminal even inside a trusted downstream envelope."""
        body = {field: quota} if wrapper is None else _downstream_body(**{wrapper: {field: quota}})
        error = _status_error(429 if wrapper is None else 424, {"error": body}, retry_after="7")
        assert error.body == body
        assert openai_error_retryable(error, 0, [0], 3) == (False, 3)

    def test_nested_upstream_quota_is_not_retried(self) -> None:
        """An upstream OpenAI error object can carry the terminal quota subtype."""
        error = _status_error(424, _downstream_body(innerError={"error": {"type": "insufficient_quota"}}))
        assert openai_error_retryable(error, 0, [0], 3) == (False, 3)

    @pytest.mark.parametrize("status,body", [(429, {}), (424, _downstream_body())])
    def test_retry_after_and_backoff(self, status: int, body: object) -> None:
        """Wrapped throttling uses the existing response-header and capped backoff policy."""
        assert openai_error_retryable(_status_error(status, body, "1.25"), 0, [0], 3) == (True, 1.25)
        assert openai_error_retryable(_status_error(status, body), 1, [0], 3) == (True, 4)
        assert openai_error_retryable(_status_error(status, body), 8, [0], 3) == (True, 60)

    def test_entity_retry_budget_is_unchanged(self) -> None:
        """HTTP 422 retains its separate smaller retry budget."""
        error = _status_error(422, {})
        retries = [0]
        assert [openai_error_retryable(error, i, retries, 3)[0] for i in range(4)] == [True, True, True, False]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status,body,expected_attempts",
        [
            pytest.param(429, {}, 2, id="direct-429"),
            pytest.param(424, _downstream_body(), 2, id="wrapped-429"),
            pytest.param(424, {}, 1, id="unrelated-424"),
            pytest.param(424, _downstream_body(innerStatusCode=500), 1, id="other-inner-status"),
            pytest.param(404, _downstream_body(), 1, id="outer-404"),
            pytest.param(429, {"type": "INSUFFICIENT_QUOTA"}, 1, id="direct-hard-quota"),
            pytest.param(424, _downstream_body(innerError={"type": "INSUFFICIENT_QUOTA"}), 1, id="wrapped-hard-quota"),
        ],
    )
    async def test_retry_loop_attempts(
        self, monkeypatch: pytest.MonkeyPatch, status: int, body: object, expected_attempts: int
    ) -> None:
        """The real loop retries once before success or preserves the original terminal error."""
        error = _status_error(status, {"error": body}, retry_after="1.25")
        response = ChatCompletion(
            id="synthetic-completion", choices=[], created=0, model="synthetic-model", object="chat.completion"
        )
        client = Mock(spec=AsyncOpenAI)
        client.with_options.return_value = client
        client.chat.completions.create = AsyncMock(side_effect=[error, response])
        sleep = AsyncMock()
        monkeypatch.setattr("azure.ai.evaluation._legacy.prompty._prompty.asyncio.sleep", sleep)
        prompty = AsyncPrompty(Path(__file__).parent.parent / "e2etests" / "data" / "basic.prompty")
        if expected_attempts == 2:
            assert await prompty._send_with_retries(client, {"model": "synthetic-model"}, timeout=12) is response
            sleep.assert_awaited_once_with(1.25)
        else:
            with pytest.raises(WrappedOpenAIError) as caught:
                await prompty._send_with_retries(client, {"model": "synthetic-model"}, timeout=12)
            assert caught.value.__cause__ is error
            sleep.assert_not_awaited()
        assert client.chat.completions.create.await_count == expected_attempts
        client.with_options.assert_called_once_with(timeout=12)
        assert error.status_code == error.response.status_code == status
        assert error.body == body

    @pytest.mark.asyncio
    @pytest.mark.parametrize("max_retries", [None, 0, 2])
    async def test_retry_loop_is_bounded(self, monkeypatch: pytest.MonkeyPatch, max_retries: Optional[int]) -> None:
        """Repeated downstream throttling exhausts the existing retry budget without replacing the error."""
        body = _downstream_body()
        error = _status_error(424, {"error": body})
        client = Mock(spec=AsyncOpenAI)
        client.with_options.return_value = client
        client.chat.completions.create = AsyncMock(side_effect=error)
        sleep = AsyncMock()
        monkeypatch.setattr("azure.ai.evaluation._legacy.prompty._prompty.asyncio.sleep", sleep)
        prompty = AsyncPrompty(Path(__file__).parent.parent / "e2etests" / "data" / "basic.prompty")
        kwargs = {} if max_retries is None else {"max_retries": max_retries}
        budget = 10 if max_retries is None else max_retries
        with pytest.raises(WrappedOpenAIError) as caught:
            await prompty._send_with_retries(client, {}, timeout=None, **kwargs)
        assert client.chat.completions.create.await_count == budget + 1
        assert [call.args[0] for call in sleep.await_args_list] == [min(60, 2 + 2**i) for i in range(budget)]
        assert caught.value.__cause__ is error
        assert error.body == body
        assert error.status_code == error.response.status_code == 424
        assert error.request_id == "synthetic-request"
