# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
from typing import Any, Callable, Dict, IO, Mapping, Optional, TypeVar, Union, cast, overload
from ._client import ConversationAnalysisClient as AnalysisClientGenerated
from collections.abc import MutableMapping
from .models import AnalyzeConversationOperationInput, AnalyzeConversationOperationState, ConversationActions
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
)
from azure.core.pipeline import PipelineResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.polling.base_polling import LROBasePolling
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.core.paging import ItemPaged

from ._configuration import ConversationAnalysisClientConfiguration
from ._utils.model_base import SdkJSONEncoder, _deserialize, _failsafe_deserialize
from ._utils.serialization import Serializer
from ._utils.utils import ClientMixinABC
from urllib.parse import urlparse
from ._validation import api_version_validation

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

def _parse_operation_id(op_loc: Optional[str]) -> Optional[str]:
    """Extract the final path segment as operation id (service-agnostic)."""
    if not op_loc:
        return None
    path = urlparse(op_loc).path.rstrip("/")
    if "/" not in path:
        return None
    return path.rsplit("/", 1)[-1]

PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

class AnalyzeConversationLROPoller(LROPoller[PollingReturnType_co]):
    """Custom poller that returns PollingReturnType_co and exposes operation metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # populated by the deserialization callback in your begin_* method
        self._last_state: Optional["AnalyzeConversationOperationState"] = None

    @property
    def details(self) -> Mapping[str, Any]:
        """Metadata associated with the long-running operation."""
        try:
            # header name may vary in case; be tolerant
            headers = getattr(self.polling_method(), "_initial_response").http_response.headers  # type: ignore[attr-defined]
            op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        except Exception:
            op_loc = None

        op_id = _parse_operation_id(op_loc)
        info: Dict[str, Any] = {"operation_id": op_id}

        # Merge fields from the final state (if available)
        if self._last_state is not None:
            s = self._last_state
            info.update(
                {
                    "status": s.status,
                    "job_id": s.job_id,
                    "display_name": s.display_name,
                    "created_date_time": s.created_date_time,
                    "last_updated_date_time": s.last_updated_date_time,
                    "expiration_date_time": s.expiration_date_time,
                    "statistics": s.statistics,
                    "errors": s.errors,
                    "next_link": s.next_link,
                }
            )
        return info

    @classmethod
    def from_continuation_token(
        cls,
        polling_method: PollingMethod[PollingReturnType_co],
        continuation_token: str,
        **kwargs: Any,
    ) -> "AnalyzeConversationLROPoller[PollingReturnType_co]":
        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        return cls(client, initial_response, deserialization_callback, polling_method)
    
class ConversationAnalysisClient(AnalysisClientGenerated):

    @overload
    def begin_analyze_conversation_job(
        self, body: AnalyzeConversationOperationInput, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationLROPoller[ItemPaged["ConversationActions"]]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: ~azure.ai.language.conversations.models.AnalyzeConversationOperationInput
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: A poller whose ``result()`` yields ``ItemPaged[ConversationActions]`` and exposes metadata via ``.details``.
        :rtype: ~azure.ai.language.conversations.AnalyzeConversationLROPoller[
                ~azure.core.paging.ItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_analyze_conversation_job(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationLROPoller[ItemPaged["ConversationActions"]]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: A poller whose ``result()`` yields ``ItemPaged[ConversationActions]`` and exposes metadata via ``.details``.
        :rtype: ~azure.ai.language.conversations.AnalyzeConversationLROPoller[
                ~azure.core.paging.ItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_analyze_conversation_job(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationLROPoller[ItemPaged["ConversationActions"]]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: A poller whose ``result()`` yields ``ItemPaged[ConversationActions]`` and exposes metadata via ``.details``.
        :rtype: ~azure.ai.language.conversations.AnalyzeConversationLROPoller[
                ~azure.core.paging.ItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    @api_version_validation(
        method_added_on="2023-04-01",
        params_added_on={"2023-04-01": ["api_version", "content_type", "accept"]},
        api_versions_list=["2023-04-01", "2024-05-01", "2024-11-01", "2024-11-15-preview", "2025-05-15-preview"],
    )
    def begin_analyze_conversation_job(  # type: ignore[override]
        self, body: Union[AnalyzeConversationOperationInput, JSON, IO[bytes]], **kwargs: Any
    ) -> AnalyzeConversationLROPoller[ItemPaged["ConversationActions"]]:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: ~azure.ai.language.conversations.models.AnalyzeConversationOperationInput or JSON or IO[bytes]
        :return: A poller whose ``result()`` yields ``ItemPaged[ConversationActions]`` and exposes metadata via ``.details``.
        :rtype: ~azure.ai.language.conversations.AnalyzeConversationLROPoller[
                ~azure.core.paging.ItemPaged[~azure.ai.language.conversations.models.ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        polling: Union[bool, PollingMethod[ItemPaged["ConversationActions"]]] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        cls = kwargs.pop("cls", None)  # optional custom deserializer
        kwargs.pop("error_map", None)

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str"),
        }

        def _fetch_state_by_next_link(next_link: str) -> AnalyzeConversationOperationState:
            req = HttpRequest("GET", next_link)
            resp = self._client.send_request(req)  # type: ignore[attr-defined]
            if resp.status_code != 200:
                raise HttpResponseError(response=resp)
            data = json.loads(resp.text())
            return AnalyzeConversationOperationState(data)

        def _build_pager_from_state(state: AnalyzeConversationOperationState) -> ItemPaged["ConversationActions"]:
            def extract_data(s: AnalyzeConversationOperationState):
                next_link = s.next_link
                actions: ConversationActions = s.actions
                return next_link, [actions]

            def get_next(token: Optional[str]) -> Optional[AnalyzeConversationOperationState]:
                if token is None:
                    return state
                if not token:
                    return None
                return _fetch_state_by_next_link(token)

            return ItemPaged(get_next, extract_data)

        # ----- end paging helpers

        # filled after creating the poller; used inside the deserializer
        poller_holder: Dict[str, AnalyzeConversationLROPoller[ItemPaged["ConversationActions"]]] = {}

        def get_long_running_output(pipeline_response):
            final_response = pipeline_response.http_response
            if final_response.status_code == 200:
                data = json.loads(final_response.text())
                op_state = AnalyzeConversationOperationState(data)

                # stash state on the custom poller for `.details`
                poller_ref = poller_holder["poller"]
                poller_ref._last_state = op_state  # type: ignore[attr-defined]

                paged = _build_pager_from_state(op_state)
                return cls(pipeline_response, paged, {}) if cls else paged
            raise HttpResponseError(response=final_response)

        # ----- polling method selection
        if polling is True:
            polling_method: PollingMethod[ItemPaged["ConversationActions"]] = cast(
                PollingMethod[ItemPaged["ConversationActions"]],
                LROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(PollingMethod[ItemPaged["ConversationActions"]], NoPolling())
        else:
            polling_method = cast(PollingMethod[ItemPaged["ConversationActions"]], polling)

        if cont_token:
            return AnalyzeConversationLROPoller[ItemPaged["ConversationActions"]].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
            )

        # Submit the job
        raw_result = self._analyze_conversation_job_initial(
            body=body, content_type=content_type, cls=lambda x, y, z: x, headers=_headers, params=_params, **kwargs
        )

        lro: AnalyzeConversationLROPoller[ItemPaged["ConversationActions"]] = AnalyzeConversationLROPoller(
            self._client, raw_result, get_long_running_output, polling_method
        )
        poller_holder["poller"] = lro
        return lro


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = ["ConversationAnalysisClient", "AnalyzeConversationLROPoller"]
