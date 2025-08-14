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
from typing import Any, Callable, Dict, IO, Iterator, Optional, TypeVar, Union, cast, overload
from ._client import ConversationAnalysisClient as AnalysisClientGenerated
from collections.abc import MutableMapping
from .models import AnalyzeConversationOperationInput, AnalyzeConversationOperationState, ConversationActions
from ._operations import AnalyzeConversationLROPoller
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
from ._validation import api_version_validation

JSON = MutableMapping[str, Any]
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


class ConversationAnalysisClient(AnalysisClientGenerated):

    @overload
    def begin_analyze_conversation_job(
        self, body: AnalyzeConversationOperationInput, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationLROPoller:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: ~azure.ai.language.conversations.models.AnalyzeConversationOperationInput
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: A custom poller that yields ItemPaged[ConversationActions] and exposes metadata via `.details`.
        :rtype: ~azure.core.polling.LROPoller[~azure.core.paging.ItemPaged[ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_analyze_conversation_job(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationLROPoller:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: A custom poller that yields ItemPaged[ConversationActions] and exposes metadata via `.details`.
        :rtype: ~azure.core.polling.LROPoller[~azure.core.paging.ItemPaged[ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_analyze_conversation_job(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeConversationLROPoller:
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: A custom poller that yields ItemPaged[ConversationActions] and exposes metadata via `.details`.
        :rtype: ~azure.core.polling.LROPoller[~azure.core.paging.ItemPaged[ConversationActions]]
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
    ) -> AnalyzeConversationLROPoller:  # <-- CHANGED: return type
        """Analyzes the input conversation utterance.

        :param body: The input for the analyze conversations operation. Required.
        :type body: ~azure.ai.language.conversations.models.AnalyzeConversationOperationInput or JSON or IO[bytes]
        :return: A custom poller that yields ItemPaged[ConversationActions] and exposes metadata via `.details`.
        :rtype: ~azure.core.polling.LROPoller[~azure.core.paging.ItemPaged[ConversationActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)  # <-- CHANGED: typed PollingMethod
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        cls = kwargs.pop("cls", None)  # optional custom deserializer
        kwargs.pop("error_map", None)

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str"),
        }

        # ----- CHANGED: paging helpers to turn final state into ItemPaged[ConversationActions]
        def _fetch_state_by_next_link(next_link: str) -> AnalyzeConversationOperationState:
            req = HttpRequest("GET", next_link)
            resp = self._client.send_request(req)  # type: ignore[attr-defined]
            if resp.status_code != 200:
                raise HttpResponseError(response=resp)
            data = json.loads(resp.text())
            return AnalyzeConversationOperationState(data)

        def _build_pager_from_state(state: AnalyzeConversationOperationState) -> ItemPaged[ConversationActions]:
            def extract_data(s: AnalyzeConversationOperationState):
                next_link = s.next_link  # attribute, not ["nextLink"]
                actions: ConversationActions = s.actions  # attribute, not ["actions"]
                return next_link, [actions]

            def get_next(token: Optional[str]) -> Optional[AnalyzeConversationOperationState]:
                if token is None:
                    return state
                if not token:
                    return None
                return _fetch_state_by_next_link(token)

            return ItemPaged(get_next, extract_data)

        # ----- end paging helpers

        # we fill this after creating the poller, then the deserializer closure uses it
        poller_holder: dict[str, AnalyzeConversationLROPoller] = {}

        # ----- CHANGED: deserializer now returns ItemPaged[ConversationActions] and updates poller._last_state
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

        # ----- end deserializer

        # polling method selection (unchanged behavior)
        if polling is True:
            polling_method: PollingMethod = LROBasePolling(
                lro_delay, path_format_arguments=path_format_arguments, **kwargs
            )
        elif polling is False:
            from azure.core.polling import NoPolling

            polling_method = NoPolling()
        else:
            polling_method = cast(PollingMethod, polling)

        # ----- CHANGED: continuation path returns your custom poller subclass
        if cont_token:
            return AnalyzeConversationLROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                # NOTE: the polling method reconstructs (client, initial_response, deserializer)
                # using the token; any `cls` provided here is ignored on resume.
            )

        # Submit the job (unchanged)
        raw_result = self._analyze_conversation_job_initial(
            body=body, content_type=content_type, cls=lambda x, y, z: x, headers=_headers, params=_params, **kwargs
        )

        # ----- CHANGED: return custom poller subclass and backfill the holder for the closure above
        lro: AnalyzeConversationLROPoller = AnalyzeConversationLROPoller(
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


__all__ = ["ConversationAnalysisClient"]
