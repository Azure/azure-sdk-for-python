# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Polling customizations for Voice Agent campaigns.

The pinned campaign-routes.tsp at 3e2177ff982e0e0af47a19f1bed59187f9084929
declares a final GET guarded by the initiating Operation-Id. The emitted
methods use default Azure Core routing instead. The generation-commit
configuration pins typespec-python 0.63.10 and http-client-python 0.39.0,
but the resolved emission log is unavailable; the emitter-side cause remains
unverified. Follow up upstream with these inputs and remove this routing
workaround when regenerated methods pass the campaign LRO regression tests.
"""

from collections.abc import Mapping
from typing import Any, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from azure.core.pipeline import PipelineResponse
from azure.core.polling.base_polling import (
    BadResponse,
    LocationPolling,
    OperationResourcePolling,
    StatusCheckPolling,
)
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.utils import case_insensitive_dict

from .polling import AIProjectsLROBasePolling, AsyncAIProjectsLROBasePolling


class _CampaignOperationResourcePolling(OperationResourcePolling[HttpRequest, HttpResponse]):
    def __init__(self, *, lro_options: Optional[dict[str, Any]] = None) -> None:
        super().__init__(lro_options=lro_options)
        self._operation_id: Optional[str] = None

    def set_initial_status(self, pipeline_response: PipelineResponse[HttpRequest, HttpResponse]) -> str:
        self._operation_id = case_insensitive_dict(pipeline_response.http_response.headers).get("Operation-Id")
        return super().set_initial_status(pipeline_response)

    def get_final_get_url(self, pipeline_response: PipelineResponse[HttpRequest, HttpResponse]) -> Optional[str]:
        if self._request.method == "DELETE":
            return None
        if self._request.method not in {"PUT", "POST"}:
            return super().get_final_get_url(pipeline_response)
        if not self._operation_id:
            raise BadResponse("Campaign operation response is missing Operation-Id; cannot guard the final GET.")

        url = urlsplit(self._request.url)
        path = url.path
        if self._request.method == "POST":
            if not path.endswith(":cancel"):
                raise BadResponse("Campaign cancellation request URL must end with ':cancel'.")
            path = path.removesuffix(":cancel")
        query = [(key, value) for key, value in parse_qsl(url.query, keep_blank_values=True) if key != "operation_id"]
        query.append(("operation_id", self._operation_id))
        return urlunsplit(url._replace(path=path, query=urlencode(query)))


class _CampaignLROBasePolling(AIProjectsLROBasePolling):
    def _filter_headers_for_continuation_token(self, headers: Mapping[str, str]) -> dict[str, str]:
        filtered = super()._filter_headers_for_continuation_token(headers)
        operation_id = case_insensitive_dict(headers).get("Operation-Id")
        if operation_id is not None:
            filtered["Operation-Id"] = operation_id
        return filtered


class _AsyncCampaignLROBasePolling(AsyncAIProjectsLROBasePolling):
    def _filter_headers_for_continuation_token(self, headers: Mapping[str, str]) -> dict[str, str]:
        filtered = super()._filter_headers_for_continuation_token(headers)
        operation_id = case_insensitive_dict(headers).get("Operation-Id")
        if operation_id is not None:
            filtered["Operation-Id"] = operation_id
        return filtered


def _configure_campaign_polling(
    kwargs: dict[str, Any],
    polling_interval: float,
    path_format_arguments: dict[str, str],
    *,
    is_async: bool = False,
) -> None:
    if kwargs.get("polling", True) is not True:
        return

    polling_kwargs = {
        key: value
        for key, value in kwargs.items()
        if key
        not in {"cls", "content_type", "continuation_token", "error_map", "params", "polling", "polling_interval"}
    }
    if not polling_kwargs.get("lro_algorithms"):
        polling_kwargs["lro_algorithms"] = [
            _CampaignOperationResourcePolling(lro_options=polling_kwargs.get("lro_options")),
            LocationPolling(),
            StatusCheckPolling(),
        ]
    polling_type = _AsyncCampaignLROBasePolling if is_async else _CampaignLROBasePolling
    kwargs["polling"] = polling_type(
        kwargs.get("polling_interval", polling_interval),
        path_format_arguments=path_format_arguments,
        **polling_kwargs,
    )
