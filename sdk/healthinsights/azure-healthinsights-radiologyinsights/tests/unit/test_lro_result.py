# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.polling.base_polling import LROBasePolling
from azure.core.rest import AsyncHttpResponse, HttpResponse
from azure.core.utils import case_insensitive_dict
from azure.healthinsights.radiologyinsights import RadiologyInsightsClient, models
from azure.healthinsights.radiologyinsights.aio import RadiologyInsightsClient as AsyncClient


ENDPOINT = "https://radiology.invalid"
RESOURCE_URL = ENDPOINT + "/health-insights/radiology-insights/jobs/offline-job?api-version=2024-10-01"
POLL_URL = ENDPOINT + "/operations/offline-job?api-version=2024-10-01"
RESOURCE = {"jobData": {"patients": [{"id": "patient-1", "patientDocuments": []}]}}
RESULT = {"modelVersion": "final-model", "patientResults": [{"patientId": "patient-1", "inferences": []}]}
COMPLETED_TRACE = [("PUT", RESOURCE_URL), ("GET", POLL_URL), ("GET", POLL_URL), ("GET", RESOURCE_URL)]


class ResponseData:
    """Pickleable response data also supports continuation tokens on older azure-core."""

    def __init__(self, request, headers, payload):
        self._request = request
        self._headers = headers
        self._content = json.dumps(payload).encode()
        self._closed = False
        self._consumed = False
        self._encoding = "utf-8"

    @property
    def request(self):
        return self._request

    @property
    def url(self):
        return self.request.url

    @property
    def status_code(self):
        return 200

    @property
    def reason(self):
        return "OK"

    @property
    def headers(self):
        return self._headers

    @property
    def content_type(self):
        return self.headers["Content-Type"]

    @property
    def content(self):
        return self._content

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value

    @property
    def is_closed(self):
        return self._closed

    @property
    def is_stream_consumed(self):
        return self._consumed

    def text(self, encoding=None):
        return self.content.decode(encoding or self.encoding)

    def json(self):
        return json.loads(self.content)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HttpResponseError(response=self)


class FakeHttpResponse(ResponseData, HttpResponse):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def read(self):
        self._consumed = True
        return self.content

    def close(self):
        self._closed = True

    def iter_bytes(self, **kwargs):
        yield self.read()

    def iter_raw(self, **kwargs):
        yield self.read()


class FakeAsyncHttpResponse(ResponseData, AsyncHttpResponse):
    async def __aexit__(self, *args):
        await self.close()

    async def read(self):
        self._consumed = True
        return self.content

    async def close(self):
        self._closed = True

    async def iter_bytes(self, **kwargs):
        yield await self.read()

    async def iter_raw(self, **kwargs):
        yield await self.read()


class Scenario:
    def __init__(self, *, asynchronous=False, failure=False, initial_result="missing"):
        self.asynchronous = asynchronous
        self.failure = failure
        self.initial_result = initial_result
        self.requests = []
        self.polls = 0

    def send(self, request, **kwargs):
        self.requests.append((request.method, request.url))
        headers = case_insensitive_dict({"Content-Type": "application/json", "Retry-After": "0"})
        payload = {"id": "offline-job", "status": "running"}
        if request.method == "PUT":
            assert self.requests == [("PUT", RESOURCE_URL)], "Continuation must not issue another PUT"
            assert json.loads(request.content) == RESOURCE
            headers.update({"Operation-Location": POLL_URL, "x-ms-request-id": "initial-request"})
            if self.initial_result != "missing":
                payload["result"] = None if self.initial_result == "null" else RESULT
        elif request.method == "GET" and request.url == POLL_URL:
            self.polls += 1
            if self.polls == 2:
                payload["status"] = "failed" if self.failure else "succeeded"
                if self.failure:
                    payload["error"] = {"code": "OfflineFailure", "message": "offline failure"}
                else:
                    payload["result"] = {**RESULT, "modelVersion": "poll-model"}
        elif request.method == "GET" and request.url == RESOURCE_URL:
            headers["x-ms-request-id"] = "final-request"
            payload.update({"status": "succeeded", "result": RESULT})
        else:
            raise AssertionError(f"Unexpected offline HTTP request: {request.method} {request.url}")
        response_type = FakeAsyncHttpResponse if self.asynchronous else FakeHttpResponse
        return response_type(request, headers, payload)

    def client(self):
        transport = MagicMock(spec=AsyncHttpTransport if self.asynchronous else HttpTransport)
        if self.asynchronous:
            transport.send = AsyncMock(side_effect=self.send)
        else:
            transport.send.side_effect = self.send
        client_type = AsyncClient if self.asynchronous else RadiologyInsightsClient
        return client_type(
            ENDPOINT,
            AzureKeyCredential("offline-test-key"),
            transport=transport,
            polling_interval=0,
        )


def assert_result(value):
    assert isinstance(value, models.RadiologyInsightsInferenceResult)
    assert value.as_dict() == RESULT
    assert isinstance(value.patient_results[0], models.RadiologyInsightsPatientResult)
    assert value.patient_results[0].patient_id == "patient-1"


def callback(observations):
    def cls(response, value, headers):
        assert_result(value)
        observations.append((response.http_response.request.url, headers["x-ms-request-id"]))
        return ("callback-result", value)

    return cls


def test_generated_public_clients_and_released_models():
    from azure.healthinsights.radiologyinsights._client import RadiologyInsightsClient as GeneratedClient
    from azure.healthinsights.radiologyinsights.aio._client import RadiologyInsightsClient as GeneratedAsyncClient

    assert RadiologyInsightsClient is GeneratedClient
    assert AsyncClient is GeneratedAsyncClient
    for model in (
        models.GuidanceInference,
        models.QualityMeasureInference,
        models.ScoringAndAssessmentInference,
        models.ContactPointSystem,
        models.ContactPointUse,
        models.ResearchStudyStatusCodeType,
    ):
        assert model is not None


@pytest.mark.parametrize("custom_polling", [False, True])
def test_sync_completed_result_and_callback(custom_polling):
    scenario = Scenario()
    observations = []
    with scenario.client() as client:
        poller = client.begin_infer_radiology_insights(
            "offline-job",
            RESOURCE,
            cls=callback(observations),
            polling=LROBasePolling(0) if custom_polling else True,
        )
        marker, result = poller.result()
    assert marker == "callback-result"
    assert_result(result)
    assert observations == [(RESOURCE_URL, "final-request")]
    assert scenario.requests == COMPLETED_TRACE


@pytest.mark.asyncio
@pytest.mark.parametrize("custom_polling", [False, True])
async def test_async_completed_result_and_callback(custom_polling):
    scenario = Scenario(asynchronous=True)
    observations = []
    async with scenario.client() as client:
        poller = await client.begin_infer_radiology_insights(
            "offline-job",
            RESOURCE,
            cls=callback(observations),
            polling=AsyncLROBasePolling(0) if custom_polling else True,
        )
        marker, result = await poller.result()
    assert marker == "callback-result"
    assert_result(result)
    assert observations == [(RESOURCE_URL, "final-request")]
    assert scenario.requests == COMPLETED_TRACE


@pytest.mark.parametrize("initial_result", ["present", "missing", "null"])
def test_sync_no_poll_result_boundary(initial_result):
    scenario = Scenario(initial_result=initial_result)
    with scenario.client() as client:
        result = client.begin_infer_radiology_insights("offline-job", RESOURCE, polling=False).result()
    if initial_result == "present":
        assert_result(result)
    elif initial_result == "missing":
        # Current Python backend uses .get("result", {}); the released wrapper returned None.
        assert isinstance(result, models.RadiologyInsightsInferenceResult)
        assert result.as_dict() == {}
    else:
        assert result is None
    assert scenario.requests == [("PUT", RESOURCE_URL)]


@pytest.mark.asyncio
@pytest.mark.parametrize("initial_result", ["present", "missing", "null"])
async def test_async_no_poll_result_boundary(initial_result):
    scenario = Scenario(asynchronous=True, initial_result=initial_result)
    async with scenario.client() as client:
        poller = await client.begin_infer_radiology_insights("offline-job", RESOURCE, polling=False)
        result = await poller.result()
    if initial_result == "present":
        assert_result(result)
    elif initial_result == "missing":
        assert isinstance(result, models.RadiologyInsightsInferenceResult)
        assert result.as_dict() == {}
    else:
        assert result is None
    assert scenario.requests == [("PUT", RESOURCE_URL)]


def test_sync_failure_propagates():
    scenario = Scenario(failure=True)
    with scenario.client() as client:
        poller = client.begin_infer_radiology_insights("offline-job", RESOURCE)
        with pytest.raises(HttpResponseError, match="offline failure"):
            poller.result()
    assert scenario.requests == COMPLETED_TRACE[:3]


@pytest.mark.asyncio
async def test_async_failure_propagates():
    scenario = Scenario(asynchronous=True, failure=True)
    async with scenario.client() as client:
        poller = await client.begin_infer_radiology_insights("offline-job", RESOURCE)
        with pytest.raises(HttpResponseError, match="offline failure"):
            await poller.result()
    assert scenario.requests == COMPLETED_TRACE[:3]


class TokenOnlyPolling(LROBasePolling):
    def run(self):
        """Capture a continuation token before the first polling GET."""


class AsyncTokenOnlyPolling(AsyncLROBasePolling):
    async def run(self):
        """Capture a continuation token before the first polling GET."""


def test_sync_continuation_does_not_repeat_put():
    scenario = Scenario()
    with scenario.client() as client:
        initial = client.begin_infer_radiology_insights("offline-job", RESOURCE, polling=TokenOnlyPolling(0))
        initial.wait()
        token = initial.continuation_token()
    with scenario.client() as client:
        resumed = client.begin_infer_radiology_insights("offline-job", RESOURCE, continuation_token=token)
        assert_result(resumed.result())
    assert scenario.requests == COMPLETED_TRACE


@pytest.mark.asyncio
async def test_async_continuation_does_not_repeat_put():
    scenario = Scenario(asynchronous=True)
    async with scenario.client() as client:
        initial = await client.begin_infer_radiology_insights("offline-job", RESOURCE, polling=AsyncTokenOnlyPolling(0))
        token = initial.continuation_token()
    async with scenario.client() as client:
        resumed = await client.begin_infer_radiology_insights("offline-job", RESOURCE, continuation_token=token)
        assert_result(await resumed.result())
    assert scenario.requests == COMPLETED_TRACE
