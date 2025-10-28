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
from typing import Any, Callable, Dict, IO, Mapping, Optional, TypeVar, Union, cast, overload, Generic, TYPE_CHECKING
from collections.abc import MutableMapping  # pylint:disable=import-error
from urllib.parse import urlparse

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.polling.base_polling import LROBasePolling
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.core.credentials import AzureKeyCredential
from azure.core.paging import ItemPaged

from ._client import TextAnalysisClient as AnalysisTextClientGenerated
from . import models as _models
from .models import AnalyzeTextOperationState, TextActions  # convenience re-exports if present
from ._utils.serialization import Serializer

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

JSON = MutableMapping[str, Any]
_Unset: Any = object()
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def _parse_operation_id(op_loc: Optional[str]) -> Optional[str]:
    """Extract the operation ID from an Operation-Location URL.

    :param op_loc: The ``Operation-Location`` header value or URL to parse.
        If ``None`` or malformed, no ID can be extracted.
    :type op_loc: Optional[str]
    :return: The trailing path segment as the operation ID, or ``None`` if not found.
    :rtype: Optional[str]
    """
    if not op_loc:
        return None
    path = urlparse(op_loc).path.rstrip("/")
    if "/" not in path:
        return None
    return path.rsplit("/", 1)[-1]


PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)


class AnalyzeTextLROPoller(LROPoller[PollingReturnType_co], Generic[PollingReturnType_co]):
    """Custom poller that returns PollingReturnType_co and exposes operation metadata."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._last_state: Optional[AnalyzeTextOperationState] = None  # set by deserializer

    # internal: called by the deserializer to update details()
    def _record_state_for_details(self, state: AnalyzeTextOperationState) -> None:
        self._last_state = state

    @property
    def details(self) -> Mapping[str, Any]:
        """Metadata associated with the long-running operation.

        :return: A mapping with keys like ``operation_id`` and, when available,
            ``status``, ``job_id``, ``display_name``, ``created_at``,
            ``last_updated_at``, ``expires_on``, ``statistics``,
            ``errors``, and ``next_link``.
        :rtype: Mapping[str, Any]
        """
        try:
            headers = getattr(self.polling_method(), "_initial_response").http_response.headers  # type: ignore[attr-defined]
            op_loc = headers.get("Operation-Location") or headers.get("operation-location")
        except (AttributeError, TypeError):
            op_loc = None

        info: Dict[str, Any] = {"operation_id": _parse_operation_id(op_loc)}
        if self._last_state is not None:
            s = self._last_state
            info.update(
                {
                    "status": s.status,
                    "job_id": s.job_id,
                    "display_name": s.display_name,
                    "created_at": s.created_at,
                    "last_updated_at": s.last_updated_at,
                    "expires_on": s.expires_on,
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
    ) -> "AnalyzeTextLROPoller[PollingReturnType_co]":
        client, initial_response, deserialization_callback = polling_method.from_continuation_token(
            continuation_token, **kwargs
        )
        return cls(client, initial_response, deserialization_callback, polling_method)


class TextAnalysisClient(AnalysisTextClientGenerated):
    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "TokenCredential"],
        *,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Create a TextAnalysisClient.
        :param endpoint: Supported Cognitive Services endpoint.
        :type endpoint: str
        :param credential: Key or token credential.
        :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
        :keyword api_version: The API version to use for this operation. Default value is
        "2025-05-15-preview". Note that overriding this default value may result in unsupported
        behavior.
        :paramtype api_version: str`
        """
        if api_version is not None:
            kwargs["api_version"] = api_version
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)

    @overload
    def begin_analyze_text_job(
        self,
        *,
        text_input: _models.MultiLanguageTextInput,
        actions: list[_models.AnalyzeTextOperationAction],
        content_type: str = "application/json",
        display_name: Optional[str] = None,
        default_language: Optional[str] = None,
        cancel_after: Optional[float] = None,
        **kwargs: Any,
    ) -> AnalyzeTextLROPoller[ItemPaged["TextActions"]]:
        """Submit a collection of text documents for analysis. Specify one or more unique tasks to be
        executed as a long-running operation.

        :keyword text_input: Contains the input to be analyzed. Required.
        :paramtype text_input: ~azure.ai.textanalytics.models.MultiLanguageTextInput
        :keyword actions: List of tasks to be performed as part of the LRO. Required.
        :paramtype actions: list[~azure.ai.textanalytics.models.AnalyzeTextOperationAction]
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :keyword display_name: Name for the task. Default value is None.
        :paramtype display_name: str
        :keyword default_language: Default language to use for records requesting automatic language
         detection. Default value is None.
        :paramtype default_language: str
        :keyword cancel_after: Optional duration in seconds after which the job will be canceled if not
         completed. Default value is None.
        :paramtype cancel_after: float
        :return: A poller whose ``result()`` yields ``ItemPaged[TextActions]`` and exposes metadata via ``.details``.
        :rtype: ~azure.ai.textanalytics.AnalyzeTextLROPoller[
                ~azure.core.paging.ItemPaged[~azure.ai.textanalytics.models.TextActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_analyze_text_job(
        self, body: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeTextLROPoller[ItemPaged["TextActions"]]:
        """Submit a collection of text documents for analysis. Specify one or more unique tasks to be
        executed as a long-running operation.

        :param body: Required.
        :type body: JSON
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: A poller whose ``result()`` yields ``ItemPaged[TextActions]`` and exposes metadata via ``.details``.
        :rtype: ~azure.ai.textanalytics.AnalyzeTextLROPoller[
                ~azure.core.paging.ItemPaged[~azure.ai.textanalytics.models.TextActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_analyze_text_job(
        self, body: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> AnalyzeTextLROPoller[ItemPaged["TextActions"]]:
        """Submit a collection of text documents for analysis. Specify one or more unique tasks to be
        executed as a long-running operation.

        :param body: Required.
        :type body: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: A poller whose ``result()`` yields ``ItemPaged[TextActions]`` and exposes metadata via ``.details``.
        :rtype: ~azure.ai.textanalytics.AnalyzeTextLROPoller[
                ~azure.core.paging.ItemPaged[~azure.ai.textanalytics.models.TextActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_analyze_text_job(  # type: ignore[override]
        self,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        text_input: _models.MultiLanguageTextInput = _Unset,
        actions: list[_models.AnalyzeTextOperationAction] = _Unset,
        display_name: Optional[str] = None,
        default_language: Optional[str] = None,
        cancel_after: Optional[float] = None,
        **kwargs: Any,
    ) -> AnalyzeTextLROPoller[ItemPaged["TextActions"]]:
        """Submit a collection of text documents for analysis. Specify one or more unique tasks to be
        executed as a long-running operation.

        :param body: Is either a JSON type or a IO[bytes] type. Required.
        :type body: JSON or IO[bytes]
        :keyword text_input: Contains the input to be analyzed. Required.
        :paramtype text_input: ~azure.ai.textanalytics.models.MultiLanguageTextInput
        :keyword actions: List of tasks to be performed as part of the LRO. Required.
        :paramtype actions: list[~azure.ai.textanalytics.models.AnalyzeTextOperationAction]
        :keyword display_name: Name for the task. Default value is None.
        :paramtype display_name: str
        :keyword default_language: Default language to use for records requesting automatic language
         detection. Default value is None.
        :paramtype default_language: str
        :keyword cancel_after: Optional duration in seconds after which the job will be canceled if not
         completed. Default value is None.
        :paramtype cancel_after: float
        :return: A poller whose ``result()`` yields ``ItemPaged[TextActions]`` and exposes metadata via ``.details``.
        :rtype: ~azure.ai.textanalytics.AnalyzeTextLROPoller[
                ~azure.core.paging.ItemPaged[~azure.ai.textanalytics.models.TextActions]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        polling: Union[bool, PollingMethod[ItemPaged["TextActions"]]] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        cls: ClsType[ItemPaged["TextActions"]] = kwargs.pop("cls", None)
        kwargs.pop("error_map", None)

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        def _fetch_state_by_next_link(next_link: str) -> AnalyzeTextOperationState:
            req = HttpRequest("GET", next_link)
            resp = self._client.send_request(req)  # type: ignore[attr-defined]
            if resp.status_code != 200:
                raise HttpResponseError(response=resp)
            data = json.loads(resp.text())
            return AnalyzeTextOperationState(data)

        def _build_pager_from_state(state: AnalyzeTextOperationState) -> ItemPaged["TextActions"]:
            def extract_data(s: AnalyzeTextOperationState):
                next_link = s.next_link
                actions_payload: TextActions = s.actions
                return next_link, [actions_payload]

            def get_next(token: Optional[str]) -> Optional[AnalyzeTextOperationState]:
                if token is None:  # First call → return the initial state
                    return state
                if not token:  # No nextLink → stop iteration
                    return None
                return _fetch_state_by_next_link(token)  # Fetch next page

            return ItemPaged(get_next, extract_data)

        poller_holder: Dict[str, AnalyzeTextLROPoller[ItemPaged["TextActions"]]] = {}

        def get_long_running_output(pipeline_response: PipelineResponse[HttpRequest, HttpResponse]):
            final_response = pipeline_response.http_response
            if final_response.status_code == 200:
                data = json.loads(final_response.text())
                op_state = AnalyzeTextOperationState(data)
                poller_ref = poller_holder["poller"]
                poller_ref._record_state_for_details(op_state)  # pylint: disable=protected-access
                paged = _build_pager_from_state(op_state)
                return cls(pipeline_response, paged, {}) if cls else paged
            raise HttpResponseError(response=final_response)

        if polling is True:
            polling_method: PollingMethod[ItemPaged["TextActions"]] = cast(
                PollingMethod[ItemPaged["TextActions"]],
                LROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(PollingMethod[ItemPaged["TextActions"]], NoPolling())
        else:
            polling_method = cast(PollingMethod[ItemPaged["TextActions"]], polling)

        if cont_token:
            return AnalyzeTextLROPoller[ItemPaged["TextActions"]].from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
            )

        initial_kwargs = dict(  # pylint:disable=use-dict-literal
            text_input=text_input,
            actions=actions,
            display_name=display_name,
            default_language=default_language,
            cancel_after=cancel_after,
            content_type=content_type,
            cls=lambda x, y, z: x,  # passthrough raw pipeline response
            headers=_headers,
            params=_params,
            **kwargs,
        )
        if body is not _Unset and body is not None:
            initial_kwargs["body"] = body

        raw_result = self._analyze_text_job_initial(**initial_kwargs)
        raw_result.http_response.read()  # type: ignore[attr-defined]

        lro: AnalyzeTextLROPoller[ItemPaged["TextActions"]] = AnalyzeTextLROPoller(
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


__all__ = ["TextAnalysisClient", "AnalyzeTextLROPoller"]
