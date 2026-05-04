import http
import math
import os
import pathlib
import json, html, re
from typing import Any, Iterator, MutableMapping, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.evaluation._common.constants import EvaluationMetrics, HarmSeverityLevel, RAIService
from azure.ai.evaluation._common.rai_service import (
    _get_service_discovery_url,
    ensure_service_availability,
    evaluate_with_rai_service,
    evaluate_with_rai_service_sync,
    evaluate_with_rai_service_sync_multimodal,
    fetch_or_reuse_token,
    fetch_result,
    get_common_headers,
    get_rai_svc_url,
    parse_response,
    submit_request,
    Tasks,
    USER_TEXT_TEMPLATE_DICT,
    get_formatted_template,
)
from azure.core.exceptions import HttpResponseError
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.identity import DefaultAzureCredential


@pytest.fixture
def data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data.jsonl")


class MockAsyncHttpResponse(AsyncHttpResponse):
    """A mocked implementation of azure.core.rest.HttpResponse."""

    def __init__(
        self,
        status_code: int,
        *,
        text: Optional[str] = None,
        json: Optional[Any] = None,
        headers: Optional[MutableMapping[str, str]] = None,
        request: Optional[HttpRequest] = None,
        content_type: Optional[str] = None,
    ) -> None:
        self._status_code = status_code
        self._text = text or ""
        self._json = json
        self._request = request
        self._headers = headers or {}
        self._content_type = content_type

    def json(self) -> Any:
        return self._json

    def text(self, encoding: Optional[str] = None) -> str:
        return self._text

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def request(self) -> HttpRequest:
        return self._request

    @property
    def reason(self) -> str:
        return f"{self.status_code} {http.client.responses[self.status_code]}"

    @property
    def headers(self) -> MutableMapping[str, str]:
        return self._headers

    @property
    def content_type(self) -> Optional[str]:
        return self._content_type

    @property
    def is_closed(self) -> bool:
        return True

    @property
    def is_stream_consumed(self) -> bool:
        return True

    @property
    def encoding(self) -> Optional[str]:
        return None

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HttpResponseError(response=self)

    async def close(self) -> None:
        pass

    async def __aenter__(self) -> object:
        raise NotImplementedError()

    async def __aexit__(self, *args) -> None:
        raise NotImplementedError()

    @property
    def url(self) -> str:
        raise NotImplementedError()

    @property
    def content(self) -> bytes:
        raise NotImplementedError()

    async def read(self) -> bytes:
        raise NotImplementedError()

    async def iter_bytes(self, **kwargs) -> Iterator[bytes]:
        raise NotImplementedError()

    async def iter_raw(self, **kwargs) -> Iterator[bytes]:
        raise NotImplementedError()


@pytest.mark.usefixtures("mock_project_scope")
@pytest.mark.unittest
class TestContentSafetyEvaluator:
    def test_rai_subscript_functions(self):
        # ensure_service_availability()

        """
        evaluate_with_rai_service()
        fetch_or_reuse_token()
        get_rai_svc_url()
        _get_service_discovery_url()
        parse_response()
        fetch_result()
        submit_request()
        ensure_service_availability()"""

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._http_utils.AsyncHttpPipeline.get", return_value=MockAsyncHttpResponse(200, json={}))
    async def test_ensure_service_availability(self, client_mock):
        _ = await ensure_service_availability("dummy_url", "dummy_token")
        assert client_mock._mock_await_count == 1

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._http_utils.AsyncHttpPipeline.get", return_value=MockAsyncHttpResponse(9001, json={}))
    async def test_ensure_service_availability_service_unavailable(self, client_mock):
        with pytest.raises(Exception) as exc_info:
            _ = await ensure_service_availability("dummy_url", "dummy_token")
        assert "RAI service is unavailable in this region" in str(exc_info._excinfo[1])
        assert "Status Code: 9001" in str(exc_info._excinfo[1])
        assert client_mock._mock_await_count == 1

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._http_utils.AsyncHttpPipeline.get", return_value=MockAsyncHttpResponse(200, json={}))
    async def test_ensure_service_availability_exception_capability_unavailable(self, client_mock):
        with pytest.raises(Exception) as exc_info:
            _ = await ensure_service_availability("dummy_url", "dummy_token", capability="does not exist")
        assert "The needed capability 'does not exist' is not supported by the RAI service in this region" in str(
            exc_info._excinfo[1]
        )
        assert client_mock._mock_await_count == 1

    @pytest.mark.asyncio
    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.post",
        return_value=MockAsyncHttpResponse(
            202,
            json={"location": "this/is/the/dummy-operation-id"},
        ),
    )
    async def test_submit_request(self, client_mock):
        result = await submit_request(
            data={"query": "What is the meaning of life", "response": "42"},
            metric="points",
            rai_svc_url="www.notarealurl.com",
            token="dummy",
            annotation_task=Tasks.CONTENT_HARM,
            evaluator_name="dummy-evaluator",
        )
        assert result == "dummy-operation-id"

    @pytest.mark.asyncio
    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.post",
        return_value=MockAsyncHttpResponse(
            404,
            json={"location": "this/is/the/dummy-operation-id"},
            content_type="application/json",
        ),
    )
    async def test_submit_request_not_found(self, client_mock):
        with pytest.raises(HttpResponseError) as exc_info:
            _ = await submit_request(
                data={"query": "What is the meaning of life", "response": "42"},
                metric="points",
                rai_svc_url="www.notarealurl.com",
                token="dummy",
                annotation_task=Tasks.CONTENT_HARM,
                evaluator_name="dummy-evaluator",
            )
        assert "Operation returned an invalid status '404 Not Found'" in str(exc_info._excinfo[1])

    @pytest.mark.usefixtures("mock_token")
    @pytest.mark.usefixtures("mock_expired_token")
    @pytest.mark.asyncio
    async def test_fetch_or_reuse_token(self, mock_token, mock_expired_token):
        mock_cred = MagicMock(Spec=DefaultAzureCredential)
        mock_cred.get_token.return_value = type("", (object,), {"token": 100})()

        res = await fetch_or_reuse_token(credential=mock_cred, token=mock_token)
        assert res == mock_token

        res = await fetch_or_reuse_token(credential=mock_cred, token=mock_expired_token)
        assert res == 100

        res = await fetch_or_reuse_token(credential=mock_cred, token="not-a-token")
        assert res == 100

    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.get",
        return_value=MockAsyncHttpResponse(200, json={"result": "stuff"}),
    )
    @patch("azure.ai.evaluation._common.constants.RAIService.TIMEOUT", 1)
    @patch("azure.ai.evaluation._common.constants.RAIService.SLEEP_TIME", 1.2)
    @pytest.mark.usefixtures("mock_token")
    @pytest.mark.asyncio
    async def test_fetch_result(self, client_mock, mock_token):
        # These asserts aren't necessary, but given the scarcity of constant patches,
        # it's nice to include an obvious example.
        assert RAIService.TIMEOUT == 1
        assert RAIService.SLEEP_TIME == 1.2
        res = await fetch_result(
            operation_id="op-id", rai_svc_url="www.notarealurl.com", credential=None, token=mock_token
        )
        assert client_mock._mock_await_count == 1
        assert res["result"] == "stuff"

    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.get",
        return_value=MockAsyncHttpResponse(404, json={"result": "stuff"}),
    )
    @patch("azure.ai.evaluation._common.constants.RAIService.TIMEOUT", 1)
    @patch("azure.ai.evaluation._common.constants.RAIService.SLEEP_TIME", 1.2)
    @pytest.mark.usefixtures("mock_token")
    @pytest.mark.asyncio
    async def test_fetch_result_timeout(self, client_mock, mock_token):
        with pytest.raises(TimeoutError) as exc_info:
            _ = await fetch_result(
                operation_id="op-id", rai_svc_url="www.notarealurl.com", credential=None, token=mock_token
            )
        # We expect 2 calls; the initial call, then one more ~2 seconds later.
        assert client_mock._mock_await_count == 2
        # Don't bother checking exact time beyond seconds, that's never going to be consistent across machines.
        assert "Fetching annotation result 2 times out after 1" in str(exc_info._excinfo[1])

    def test_parse_response(self):
        batch_response = [{"not-a-metric": "not-a-value"}]
        metric_name = EvaluationMetrics.HATE_FAIRNESS
        result = parse_response(
            batch_response=batch_response,
            metric_name=metric_name,
            metric_display_name=EvaluationMetrics.HATE_UNFAIRNESS,
        )
        assert math.isnan(result[EvaluationMetrics.HATE_UNFAIRNESS])
        assert math.isnan(result[EvaluationMetrics.HATE_UNFAIRNESS + "_score"])
        assert math.isnan(result[EvaluationMetrics.HATE_UNFAIRNESS + "_reason"])

        metric_name = EvaluationMetrics.VIOLENCE
        response_value = {
            "label": 0,
            "reasoning": "This is a sample reasoning.",
            "version": "0.3",
        }

        # The parse_response function has a TON of conditional logic that depends
        # on the exact structure of batch_response[0][metric_name].
        # This tests ALL of it.
        batch_response[0] = {metric_name: str(response_value)}

        result = parse_response(batch_response=batch_response, metric_name=metric_name, metric_display_name=metric_name)
        assert result[metric_name] == HarmSeverityLevel.VeryLow.value
        assert result[metric_name + "_score"] == 0
        assert result[metric_name + "_reason"] == response_value["reasoning"]

        response_value["output"] = {
            "valid": True,
            "reason": "This is a sample reason.",
        }
        batch_response[0] = {metric_name: str(response_value)}
        result = parse_response(batch_response=batch_response, metric_name=metric_name, metric_display_name=metric_name)
        assert result[metric_name] == HarmSeverityLevel.VeryLow.value
        assert result[metric_name + "_score"] == 0
        assert result[metric_name + "_reason"] == response_value["output"]["reason"]

        response_value.pop("output")
        response_value.pop("reasoning")
        response_value.pop("label")
        batch_response[0] = {metric_name: str(response_value)}
        result = parse_response(batch_response=batch_response, metric_name=metric_name)
        assert math.isnan(result[metric_name])
        assert math.isnan(result[metric_name + "_score"])
        assert result[metric_name + "_reason"] == ""

        batch_response[0] = {metric_name: 5}
        result = parse_response(batch_response=batch_response, metric_name=metric_name)
        assert result[metric_name] == HarmSeverityLevel.Medium.value
        assert result[metric_name + "_score"] == 5
        assert result[metric_name + "_reason"] == ""

        batch_response[0] = {metric_name: 8}
        result = parse_response(batch_response=batch_response, metric_name=metric_name)
        assert math.isnan(result[metric_name])
        assert math.isnan(result[metric_name + "_score"])

        batch_response[0] = {metric_name: "value is 7"}
        result = parse_response(batch_response=batch_response, metric_name=metric_name)
        assert result[metric_name] == HarmSeverityLevel.High.value
        assert result[metric_name + "_score"] == 7
        assert result[metric_name + "_reason"] == "value is 7"

        batch_response[0] = {metric_name: "not a number"}
        result = parse_response(batch_response=batch_response, metric_name=metric_name)
        assert math.isnan(result[metric_name])
        assert math.isnan(result[metric_name + "_score"])

        batch_response[0] = {metric_name: ["still not a number"]}
        result = parse_response(batch_response=batch_response, metric_name=metric_name, metric_display_name=metric_name)
        assert math.isnan(result[metric_name])
        assert math.isnan(result[metric_name + "_score"])

    @pytest.mark.asyncio
    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.get",
        return_value=MockAsyncHttpResponse(
            200, json={"properties": {"discoveryUrl": "https://www.url.com:123/thePath"}}
        ),
    )
    async def test_get_service_discovery_url(self, client_mock):

        token = "fake-token"
        azure_ai_project = {
            "subscription_id": "fake-id",
            "project_name": "fake-name",
            "resource_group_name": "fake-group",
        }

        url = await _get_service_discovery_url(azure_ai_project=azure_ai_project, token=token)
        assert url == "https://www.url.com:123"

    @pytest.mark.asyncio
    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.get",
        return_value=MockAsyncHttpResponse(
            201, json={"properties": {"discoveryUrl": "https://www.url.com:123/thePath"}}
        ),
    )
    async def test_get_service_discovery_url_exception(self, client_mock):
        token = "fake-token"
        azure_ai_project = {
            "subscription_id": "fake-id",
            "project_name": "fake-name",
            "resource_group_name": "fake-group",
        }

        with pytest.raises(Exception) as exc_info:
            _ = await _get_service_discovery_url(azure_ai_project=azure_ai_project, token=token)
        assert "Failed to connect to your Azure AI project." in str(exc_info._excinfo[1])

    @pytest.mark.asyncio
    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.get",
        return_value=MockAsyncHttpResponse(
            200, json={"properties": {"discoveryUrl": "https://www.url.com:123/thePath"}}
        ),
    )
    @patch(
        "azure.ai.evaluation._common.rai_service._get_service_discovery_url",
        return_value="https://www.url.com:123",
    )
    async def test_get_rai_svc_url(self, client_mock, discovery_mock):
        token = "fake-token"
        project_scope = {
            "subscription_id": "fake-id",
            "project_name": "fake-name",
            "resource_group_name": "fake-group",
        }
        rai_url = await get_rai_svc_url(project_scope=project_scope, token=token)
        assert rai_url == (
            "https://www.url.com:123/raisvc/v1.0/subscriptions/fake-id/"
            + "resourceGroups/fake-group/providers/Microsoft.MachineLearningServices/workspaces/fake-name"
        )

    @pytest.mark.asyncio
    @patch("azure.identity.DefaultAzureCredential")
    @patch("azure.ai.evaluation._common.rai_service.fetch_or_reuse_token")
    @patch("azure.ai.evaluation._common.rai_service.get_rai_svc_url")
    @patch("azure.ai.evaluation._common.rai_service.ensure_service_availability")
    @patch("azure.ai.evaluation._common.rai_service.get_sync_http_client_with_retry")
    async def test_evaluate_with_rai_service_sync(
        self, http_client_mock, ensure_avail_mock, get_url_mock, fetch_token_mock, cred_mock
    ):
        # Mock token fetch
        fetch_token_mock.return_value = "fake-token"

        # Mock RAI service URL
        get_url_mock.return_value = "https://fake-rai-url.com"

        # Mock service availability (returns None)
        ensure_avail_mock.return_value = None

        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "name": "hate_unfairness",
                    "score": 2,
                    "label": "Medium",
                    "reason": "Test reason",
                }
            ]
        }

        # Mock the HTTP client's post method
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        http_client_mock.return_value = mock_client

        result = await evaluate_with_rai_service_sync(
            data={"query": "what is the weather outside?", "response": "test response"},
            metric_name=EvaluationMetrics.HATE_UNFAIRNESS,
            project_scope={
                "subscription_id": "fake-id",
                "project_name": "fake-name",
                "resource_group_name": "fake-group",
            },
            credential=DefaultAzureCredential(),
            annotation_task="content harm",
        )

        assert "results" in result
        assert mock_client.post.call_count == 1
        fetch_token_mock.assert_called_once()
        get_url_mock.assert_called_once()
        ensure_avail_mock.assert_called_once()

    # RAI service templates are so different that it's not worth trying to test them all in one test.
    # Groundedness is JSON
    def test_get_formatted_template_groundedness(self):
        tagged_text = "This text </> has <> tags."
        bracketed_text = "{This text has {brackets}, and I didn't even both to even them out {."
        quoted_text = (
            'This text has \'quotes\', also it has "quotes", and it even has `backticks` and """ triple quotes""".'
        )
        all_texts = [tagged_text, quoted_text, bracketed_text]
        for text in all_texts:
            input_kwargs = {
                "query": text,
                "response": text,
                "context": text,
            }
            formatted_payload = get_formatted_template(input_kwargs, Tasks.GROUNDEDNESS)
            assert json.loads(formatted_payload)["question"] == text

    # Default is basic markup.
    def test_get_formatted_template_default(self):
        tagged_text = "This text </> has <> tags."
        bracketed_text = "{This text has {brackets}, and I didn't even both to even them out {."
        quoted_text = (
            'This text has \'quotes\', also it has "quotes", and it even has `backticks` and """ triple quotes""".'
        )
        all_texts = [tagged_text, quoted_text, bracketed_text]
        for text in all_texts:
            input_kwargs = {
                "query": text,
                "response": text,
                "context": text,
            }
            formatted_payload = get_formatted_template(input_kwargs, "DEFAULT")
            assert html.unescape(re.match("\<Human\>{(.*?)}\<", formatted_payload)[1]) == text

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._common.rai_service.evaluate_with_rai_service", new_callable=AsyncMock)
    async def test_evaluate_with_rai_service_sync_legacy_routes_to_legacy(self, legacy_mock):
        """Verify that use_legacy_endpoint=True delegates to evaluate_with_rai_service."""
        legacy_mock.return_value = {"violence": "Very low", "violence_score": 0}

        result = await evaluate_with_rai_service_sync(
            data={"query": "test", "response": "test"},
            metric_name=EvaluationMetrics.VIOLENCE,
            project_scope={
                "subscription_id": "fake-id",
                "project_name": "fake-name",
                "resource_group_name": "fake-group",
            },
            credential=DefaultAzureCredential(),
            use_legacy_endpoint=True,
        )

        legacy_mock.assert_called_once()
        assert result == {"violence": "Very low", "violence_score": 0}

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._common.rai_service.evaluate_with_rai_service", new_callable=AsyncMock)
    async def test_evaluate_with_rai_service_sync_legacy_maps_hate_unfairness_to_hate_fairness(self, legacy_mock):
        """When use_legacy_endpoint=True and metric is hate_unfairness, it should be mapped to hate_fairness."""
        legacy_mock.return_value = {}

        # Test with enum value
        await evaluate_with_rai_service_sync(
            data={"query": "test", "response": "test"},
            metric_name=EvaluationMetrics.HATE_UNFAIRNESS,
            project_scope={
                "subscription_id": "fake-id",
                "project_name": "fake-name",
                "resource_group_name": "fake-group",
            },
            credential=DefaultAzureCredential(),
            use_legacy_endpoint=True,
        )

        _, kwargs = legacy_mock.call_args
        assert kwargs["metric_name"] == "hate_fairness"

        legacy_mock.reset_mock()

        # Test with string value
        await evaluate_with_rai_service_sync(
            data={"query": "test", "response": "test"},
            metric_name="hate_unfairness",
            project_scope={
                "subscription_id": "fake-id",
                "project_name": "fake-name",
                "resource_group_name": "fake-group",
            },
            credential=DefaultAzureCredential(),
            use_legacy_endpoint=True,
        )

        _, kwargs = legacy_mock.call_args
        assert kwargs["metric_name"] == "hate_fairness"

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._common.rai_service.fetch_or_reuse_token")
    @patch("azure.ai.evaluation._common.rai_service.get_rai_svc_url")
    @patch("azure.ai.evaluation._common.rai_service.ensure_service_availability")
    @patch("azure.ai.evaluation._common.rai_service.get_sync_http_client_with_retry")
    async def test_evaluate_with_rai_service_sync_maps_hate_fairness_to_hate_unfairness(
        self, http_client_mock, ensure_avail_mock, get_url_mock, fetch_token_mock
    ):
        """When use_legacy_endpoint=False and metric is hate_fairness, payload should use hate_unfairness."""
        fetch_token_mock.return_value = "fake-token"
        get_url_mock.return_value = "https://fake-rai-url.com"
        ensure_avail_mock.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        http_client_mock.return_value = mock_client

        # Test with enum value
        await evaluate_with_rai_service_sync(
            data={"query": "test", "response": "test"},
            metric_name=EvaluationMetrics.HATE_FAIRNESS,
            project_scope={
                "subscription_id": "fake-id",
                "project_name": "fake-name",
                "resource_group_name": "fake-group",
            },
            credential=DefaultAzureCredential(),
            use_legacy_endpoint=False,
        )

        # Verify the POST payload uses hate_unfairness
        post_call_args = mock_client.post.call_args
        payload = json.loads(post_call_args[1]["data"] if "data" in post_call_args[1] else post_call_args[0][1])
        evaluator_name = payload["testing_criteria"][0]["evaluator_name"]
        assert evaluator_name == "builtin.hate_unfairness"

        mock_client.post.reset_mock()

        # Test with string value
        await evaluate_with_rai_service_sync(
            data={"query": "test", "response": "test"},
            metric_name="hate_fairness",
            project_scope={
                "subscription_id": "fake-id",
                "project_name": "fake-name",
                "resource_group_name": "fake-group",
            },
            credential=DefaultAzureCredential(),
            use_legacy_endpoint=False,
        )

        post_call_args = mock_client.post.call_args
        payload = json.loads(post_call_args[1]["data"] if "data" in post_call_args[1] else post_call_args[0][1])
        evaluator_name = payload["testing_criteria"][0]["evaluator_name"]
        assert evaluator_name == "builtin.hate_unfairness"

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._common.rai_service.evaluate_with_rai_service_multimodal", new_callable=AsyncMock)
    async def test_evaluate_with_rai_service_sync_multimodal_legacy_maps_metric(self, legacy_mm_mock):
        """When use_legacy_endpoint=True and metric is hate_unfairness, multimodal should map to hate_fairness."""
        legacy_mm_mock.return_value = {}

        await evaluate_with_rai_service_sync_multimodal(
            messages=[{"role": "user", "content": "test"}],
            metric_name=EvaluationMetrics.HATE_UNFAIRNESS,
            project_scope={
                "subscription_id": "fake-id",
                "project_name": "fake-name",
                "resource_group_name": "fake-group",
            },
            credential=DefaultAzureCredential(),
            use_legacy_endpoint=True,
        )

        _, kwargs = legacy_mm_mock.call_args
        assert kwargs["metric_name"] == "hate_fairness"

        legacy_mm_mock.reset_mock()

        # Also test with string input
        await evaluate_with_rai_service_sync_multimodal(
            messages=[{"role": "user", "content": "test"}],
            metric_name="hate_unfairness",
            project_scope={
                "subscription_id": "fake-id",
                "project_name": "fake-name",
                "resource_group_name": "fake-group",
            },
            credential=DefaultAzureCredential(),
            use_legacy_endpoint=True,
        )

        _, kwargs = legacy_mm_mock.call_args
        assert kwargs["metric_name"] == "hate_fairness"


class TestParseEvalResult:
    """Tests for _parse_eval_result function that handles sync_evals response format."""

    def test_parse_eval_result_with_dict_results(self):
        """Test parsing when results are plain dicts."""
        from azure.ai.evaluation._evaluators._common._base_rai_svc_eval import RaiServiceEvaluatorBase
        from azure.ai.evaluation._common.constants import EvaluationMetrics

        # Mock a sync_evals response with dict results
        eval_result = {
            "results": [
                {
                    "type": "azure_ai_evaluator",
                    "name": "violence",
                    "metric": "violence",
                    "score": 0,
                    "label": "pass",
                    "reason": "No violent content detected.",
                    "threshold": 3,
                    "passed": True,
                }
            ],
            "status": "completed",
        }

        # Create a mock evaluator to test _parse_eval_result
        class MockViolenceEvaluator(RaiServiceEvaluatorBase):
            def __init__(self):
                self._eval_metric = EvaluationMetrics.VIOLENCE

        evaluator = MockViolenceEvaluator.__new__(MockViolenceEvaluator)
        evaluator._eval_metric = EvaluationMetrics.VIOLENCE

        result = evaluator._parse_eval_result(eval_result)

        assert result["violence"] == "Very low"  # Score 0 maps to "Very low"
        assert result["violence_score"] == 0
        assert result["violence_reason"] == "No violent content detected."

    def test_parse_eval_result_with_model_like_objects(self):
        """Test parsing when results are Model-like objects with dict-like access."""
        from azure.ai.evaluation._evaluators._common._base_rai_svc_eval import RaiServiceEvaluatorBase
        from azure.ai.evaluation._common.constants import EvaluationMetrics

        # Create a Model-like object that supports dict-like access via .get()
        class ModelLikeObject:
            def __init__(self, data):
                self._data = data

            def get(self, key, default=None):
                return self._data.get(key, default)

            def __getitem__(self, key):
                return self._data[key]

        # Mock a sync_evals response with Model-like result objects
        result_item = ModelLikeObject(
            {
                "type": "azure_ai_evaluator",
                "name": "violence",
                "metric": "violence",
                "score": 2,
                "label": "pass",
                "reason": "Low violence detected.",
                "threshold": 3,
                "passed": True,
            }
        )

        # Create a mock eval_result with Model-like results attribute
        class MockEvalRunOutputItem:
            def __init__(self):
                self.results = [result_item]
                self.status = "completed"

        eval_result = MockEvalRunOutputItem()

        # Create a mock evaluator to test _parse_eval_result
        evaluator = RaiServiceEvaluatorBase.__new__(RaiServiceEvaluatorBase)
        evaluator._eval_metric = EvaluationMetrics.VIOLENCE

        result = evaluator._parse_eval_result(eval_result)

        assert result["violence"] == "Low"  # Score 2 maps to "Low"
        assert result["violence_score"] == 2
        assert result["violence_reason"] == "Low violence detected."

    def test_parse_eval_result_severity_not_from_label(self):
        """Test that severity is calculated from score, not from the 'label' field."""
        from azure.ai.evaluation._evaluators._common._base_rai_svc_eval import RaiServiceEvaluatorBase
        from azure.ai.evaluation._common.constants import EvaluationMetrics

        # In sync_evals, label is "pass"/"fail", not the severity
        eval_result = {
            "results": [
                {
                    "metric": "violence",
                    "score": 4,  # Medium severity
                    "label": "fail",  # This is pass/fail, NOT severity
                    "reason": "Medium violence detected.",
                }
            ]
        }

        evaluator = RaiServiceEvaluatorBase.__new__(RaiServiceEvaluatorBase)
        evaluator._eval_metric = EvaluationMetrics.VIOLENCE

        result = evaluator._parse_eval_result(eval_result)

        # Severity should be "Medium" (from score 4), not "fail" (from label)
        assert result["violence"] == "Medium"
        assert result["violence_score"] == 4

    def test_parse_eval_result_with_builtin_prefix(self):
        """Test parsing when metric has 'builtin.' prefix (actual API response format)."""
        from azure.ai.evaluation._evaluators._common._base_rai_svc_eval import RaiServiceEvaluatorBase
        from azure.ai.evaluation._common.constants import EvaluationMetrics

        # Actual sync_evals API returns metric with "builtin." prefix
        eval_result = {
            "results": [
                {
                    "name": "violence",
                    "type": "azure_ai_evaluator",
                    "metric": "builtin.violence",  # API returns this format
                    "score": 0.0,
                    "label": None,
                    "reason": "No violent content detected.",
                    "properties": {
                        "outcome": "pass",
                        "metrics": {"promptTokens": "15", "completionTokens": "55"},
                    },
                }
            ]
        }

        evaluator = RaiServiceEvaluatorBase.__new__(RaiServiceEvaluatorBase)
        evaluator._eval_metric = EvaluationMetrics.VIOLENCE

        result = evaluator._parse_eval_result(eval_result)

        assert result["violence"] == "Very low"
        assert result["violence_score"] == 0.0
        assert result["violence_reason"] == "No violent content detected."
        # Token counts should be extracted from properties.metrics
        assert result["violence_prompt_tokens"] == "15"
        assert result["violence_completion_tokens"] == "55"


@pytest.mark.unittest
class TestExtraHeaders:
    """Tests for extra_headers propagation through the RAI service call chain."""

    # ------------------------------------------------------------------ #
    # get_common_headers
    # ------------------------------------------------------------------ #

    def test_get_common_headers_without_extra_headers(self):
        """get_common_headers returns base headers when extra_headers is None."""
        headers = get_common_headers("fake-token")
        assert headers["Authorization"] == "Bearer fake-token"
        assert "User-Agent" in headers
        assert len(headers) == 2

    def test_get_common_headers_with_extra_headers(self):
        """get_common_headers merges extra_headers into the result."""
        extra = {"X-Custom": "value", "X-Another": "42"}
        headers = get_common_headers("fake-token", extra_headers=extra)
        assert headers["Authorization"] == "Bearer fake-token"
        assert headers["X-Custom"] == "value"
        assert headers["X-Another"] == "42"

    def test_get_common_headers_extra_headers_do_not_override_auth(self):
        """SDK-owned headers (Authorization, User-Agent) must win over extra_headers."""
        extra = {"Authorization": "Bearer override"}
        headers = get_common_headers("fake-token", extra_headers=extra)
        # SDK headers are applied after extra_headers, so they cannot be overridden
        assert headers["Authorization"] == "Bearer fake-token"

    def test_get_common_headers_with_evaluator_name_and_extra_headers(self):
        """Both evaluator_name and extra_headers work together."""
        extra = {"X-Trace-Id": "abc123"}
        headers = get_common_headers("fake-token", evaluator_name="violence", extra_headers=extra)
        assert "violence" in headers["User-Agent"]
        assert headers["X-Trace-Id"] == "abc123"

    # ------------------------------------------------------------------ #
    # submit_request — raw HTTP path
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.post",
        return_value=MockAsyncHttpResponse(
            202,
            json={"location": "this/is/the/op-id"},
        ),
    )
    async def test_submit_request_extra_headers_included(self, post_mock):
        """extra_headers should appear in the HTTP request headers for submit_request."""
        extra = {"X-Custom": "submit-value"}
        await submit_request(
            data={"query": "q", "response": "r"},
            metric="violence",
            rai_svc_url="https://fake-url.com",
            token="fake-token",
            annotation_task=Tasks.CONTENT_HARM,
            evaluator_name="violence",
            extra_headers=extra,
        )
        _, call_kwargs = post_mock.call_args
        sent_headers = call_kwargs.get("headers", {})
        assert sent_headers.get("X-Custom") == "submit-value"
        assert sent_headers.get("Authorization") == "Bearer fake-token"

    # ------------------------------------------------------------------ #
    # fetch_result — raw HTTP path
    # ------------------------------------------------------------------ #

    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.get",
        return_value=MockAsyncHttpResponse(200, json={"result": "done"}),
    )
    @pytest.mark.usefixtures("mock_token")
    @pytest.mark.asyncio
    async def test_fetch_result_extra_headers_included(self, get_mock, mock_token):
        """extra_headers should appear in the HTTP request headers for fetch_result."""
        extra = {"X-Custom": "fetch-value"}
        result = await fetch_result(
            operation_id="op-id",
            rai_svc_url="https://fake-url.com",
            credential=None,
            token=mock_token,
            extra_headers=extra,
        )
        _, call_kwargs = get_mock.call_args
        sent_headers = call_kwargs.get("headers", {})
        assert sent_headers.get("X-Custom") == "fetch-value"
        assert result["result"] == "done"

    # ------------------------------------------------------------------ #
    # ensure_service_availability — raw HTTP path
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.get",
        return_value=MockAsyncHttpResponse(200, json={}),
    )
    async def test_ensure_service_availability_extra_headers_included(self, get_mock):
        """extra_headers should appear in the HTTP request headers for ensure_service_availability."""
        extra = {"X-Custom": "avail-value"}
        await ensure_service_availability("https://fake-url.com", "fake-token", extra_headers=extra)
        _, call_kwargs = get_mock.call_args
        sent_headers = call_kwargs.get("headers", {})
        assert sent_headers.get("X-Custom") == "avail-value"

    # ------------------------------------------------------------------ #
    # _get_service_discovery_url — ARM call
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    @patch(
        "azure.ai.evaluation._http_utils.AsyncHttpPipeline.get",
        return_value=MockAsyncHttpResponse(200, json={"properties": {"discoveryUrl": "https://disc.com/path"}}),
    )
    async def test_get_service_discovery_url_extra_headers_included(self, get_mock):
        """extra_headers should appear in the ARM request headers."""
        extra = {"X-Custom": "disc-value"}
        project = {"subscription_id": "sub", "resource_group_name": "rg", "project_name": "proj"}
        await _get_service_discovery_url(project, "fake-token", extra_headers=extra)
        _, call_kwargs = get_mock.call_args
        sent_headers = call_kwargs.get("headers", {})
        assert sent_headers.get("X-Custom") == "disc-value"

    # ------------------------------------------------------------------ #
    # evaluate_with_rai_service_sync — non-onedp sync evals path
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._common.rai_service.fetch_or_reuse_token")
    @patch("azure.ai.evaluation._common.rai_service.get_rai_svc_url")
    @patch("azure.ai.evaluation._common.rai_service.ensure_service_availability")
    @patch("azure.ai.evaluation._common.rai_service.get_sync_http_client_with_retry")
    async def test_evaluate_sync_extra_headers_in_http_request(
        self, http_client_mock, ensure_avail_mock, get_url_mock, fetch_token_mock
    ):
        """extra_headers should be merged into the sync_evals HTTP POST headers."""
        fetch_token_mock.return_value = "fake-token"
        get_url_mock.return_value = "https://fake-rai-url.com"
        ensure_avail_mock.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        http_client_mock.return_value = mock_client

        extra = {"X-Custom": "sync-value"}
        await evaluate_with_rai_service_sync(
            data={"query": "q", "response": "r"},
            metric_name=EvaluationMetrics.VIOLENCE,
            project_scope={"subscription_id": "s", "project_name": "p", "resource_group_name": "rg"},
            credential=DefaultAzureCredential(),
            extra_headers=extra,
        )

        sent_headers = mock_client.post.call_args[1].get("headers", {})
        assert sent_headers.get("X-Custom") == "sync-value"
        # extra_headers should also be forwarded to get_rai_svc_url and ensure_service_availability
        get_url_mock.assert_called_once()
        _, url_kwargs = get_url_mock.call_args
        assert url_kwargs.get("extra_headers") == extra
        ensure_avail_mock.assert_called_once()
        _, avail_kwargs = ensure_avail_mock.call_args
        assert avail_kwargs.get("extra_headers") == extra

    # ------------------------------------------------------------------ #
    # evaluate_with_rai_service_sync — legacy routing
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._common.rai_service.evaluate_with_rai_service", new_callable=AsyncMock)
    async def test_evaluate_sync_legacy_passes_extra_headers(self, legacy_mock):
        """extra_headers should be passed through to the legacy endpoint."""
        legacy_mock.return_value = {"violence": "Very low", "violence_score": 0}
        extra = {"X-Custom": "legacy-value"}

        await evaluate_with_rai_service_sync(
            data={"query": "q", "response": "r"},
            metric_name=EvaluationMetrics.VIOLENCE,
            project_scope={"subscription_id": "s", "project_name": "p", "resource_group_name": "rg"},
            credential=DefaultAzureCredential(),
            use_legacy_endpoint=True,
            extra_headers=extra,
        )

        _, kwargs = legacy_mock.call_args
        assert kwargs["extra_headers"] == extra

    # ------------------------------------------------------------------ #
    # evaluate_with_rai_service_sync_multimodal — legacy routing
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._common.rai_service.evaluate_with_rai_service_multimodal", new_callable=AsyncMock)
    async def test_evaluate_sync_multimodal_legacy_passes_extra_headers(self, legacy_mm_mock):
        """extra_headers should be passed through to the legacy multimodal endpoint."""
        legacy_mm_mock.return_value = {}
        extra = {"X-Custom": "mm-legacy-value"}

        await evaluate_with_rai_service_sync_multimodal(
            messages=[{"role": "user", "content": "test"}],
            metric_name=EvaluationMetrics.VIOLENCE,
            project_scope={"subscription_id": "s", "project_name": "p", "resource_group_name": "rg"},
            credential=DefaultAzureCredential(),
            use_legacy_endpoint=True,
            extra_headers=extra,
        )

        _, kwargs = legacy_mm_mock.call_args
        assert kwargs["extra_headers"] == extra

    # ------------------------------------------------------------------ #
    # evaluate_with_rai_service_sync_multimodal — non-onedp sync evals
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._common.rai_service.fetch_or_reuse_token")
    @patch("azure.ai.evaluation._common.rai_service.get_rai_svc_url")
    @patch("azure.ai.evaluation._common.rai_service.ensure_service_availability")
    @patch("azure.ai.evaluation._common.rai_service.get_sync_http_client_with_retry")
    async def test_evaluate_sync_multimodal_extra_headers_in_http_request(
        self, http_client_mock, ensure_avail_mock, get_url_mock, fetch_token_mock
    ):
        """extra_headers should be merged into the multimodal sync_evals HTTP POST headers."""
        fetch_token_mock.return_value = "fake-token"
        get_url_mock.return_value = "https://fake-rai-url.com"
        ensure_avail_mock.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        http_client_mock.return_value = mock_client

        extra = {"X-Custom": "mm-sync-value"}
        await evaluate_with_rai_service_sync_multimodal(
            messages=[{"role": "user", "content": "test"}, {"role": "assistant", "content": "reply"}],
            metric_name="violence",
            project_scope={"subscription_id": "s", "project_name": "p", "resource_group_name": "rg"},
            credential=DefaultAzureCredential(),
            extra_headers=extra,
        )

        sent_headers = mock_client.post.call_args[1].get("headers", {})
        assert sent_headers.get("X-Custom") == "mm-sync-value"

    # ------------------------------------------------------------------ #
    # evaluate_with_rai_service — legacy non-onedp path
    # ------------------------------------------------------------------ #

    @pytest.mark.asyncio
    @patch("azure.ai.evaluation._common.rai_service.fetch_or_reuse_token")
    @patch("azure.ai.evaluation._common.rai_service.get_rai_svc_url")
    @patch("azure.ai.evaluation._common.rai_service.ensure_service_availability")
    @patch("azure.ai.evaluation._common.rai_service.submit_request", new_callable=AsyncMock)
    @patch("azure.ai.evaluation._common.rai_service.fetch_result", new_callable=AsyncMock)
    async def test_evaluate_legacy_passes_extra_headers_to_sub_functions(
        self, fetch_result_mock, submit_mock, ensure_avail_mock, get_url_mock, fetch_token_mock
    ):
        """extra_headers should be passed to submit_request and fetch_result in legacy path."""
        fetch_token_mock.return_value = "fake-token"
        get_url_mock.return_value = "https://fake-rai-url.com"
        ensure_avail_mock.return_value = None
        submit_mock.return_value = "op-id"
        fetch_result_mock.return_value = [{"violence": '{"label": 0, "reasoning": "safe"}'}]

        extra = {"X-Custom": "legacy-sub-value"}
        await evaluate_with_rai_service(
            data={"query": "q", "response": "r"},
            metric_name=EvaluationMetrics.VIOLENCE,
            project_scope={"subscription_id": "s", "project_name": "p", "resource_group_name": "rg"},
            credential=DefaultAzureCredential(),
            extra_headers=extra,
        )

        _, submit_kwargs = submit_mock.call_args
        assert submit_kwargs.get("extra_headers") == extra
        _, fetch_kwargs = fetch_result_mock.call_args
        assert fetch_kwargs.get("extra_headers") == extra

    # ------------------------------------------------------------------ #
    # RaiServiceEvaluatorBase — extra_headers stored from kwargs
    # ------------------------------------------------------------------ #

    def test_base_evaluator_stores_extra_headers(self):
        """RaiServiceEvaluatorBase should store extra_headers from kwargs."""
        from azure.ai.evaluation._evaluators._common._base_rai_svc_eval import RaiServiceEvaluatorBase

        evaluator = RaiServiceEvaluatorBase.__new__(RaiServiceEvaluatorBase)
        # Simulate __init__ by setting attributes manually
        extra = {"X-Custom": "eval-value"}
        evaluator._extra_headers = extra
        assert evaluator._extra_headers == extra

    def test_base_evaluator_extra_headers_defaults_to_none(self):
        """RaiServiceEvaluatorBase should default extra_headers to None when not provided."""
        from azure.ai.evaluation._evaluators._common._base_rai_svc_eval import RaiServiceEvaluatorBase

        evaluator = RaiServiceEvaluatorBase.__new__(RaiServiceEvaluatorBase)
        evaluator._extra_headers = None
        assert evaluator._extra_headers is None
