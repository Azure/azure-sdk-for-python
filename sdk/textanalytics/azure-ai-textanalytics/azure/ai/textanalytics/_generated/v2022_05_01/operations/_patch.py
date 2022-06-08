# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any, Optional, Union, TypeVar, Callable, Dict, cast
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.rest import HttpRequest
from ._text_analytics_client_operations import TextAnalyticsClientOperationsMixin as GeneratedTextAnalyticsClientOperationsMixin
from ...._lro import AnalyzeActionsLROPoller, AnalyzeActionsLROPollingMethod
from .. import models as _models
T = TypeVar('T')
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]


class TextAnalyticsClientOperationsMixin(GeneratedTextAnalyticsClientOperationsMixin):

    @distributed_trace
    def begin_analyze_text_submit_job(
            self,
            body: _models.AnalyzeTextJobsInput,
            **kwargs: Any
    ) -> AnalyzeActionsLROPoller[_models.AnalyzeTextJobState]:
        """Submit text analysis job.

        Submit a collection of text documents for analysis. Specify one or more unique tasks to be
        executed as a long-running operation.

        :param body: Collection of documents to analyze and one or more tasks to execute.
        :type body: ~azure.ai.textanalytics.v2022_05_01.models.AnalyzeTextJobsInput
        :keyword callable cls: A custom type or function that will be passed the direct response
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be AnalyzeActionsLROPollingMethod. Pass
         in False for this operation to not poll, or pass in your own initialized polling object for a
         personal polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of AnalyzeActionsLROPoller that returns either AnalyzeTextJobState or the
         result of cls(response)
        :rtype:
         ~...._lro.AnalyzeActionsLROPoller[~azure.ai.textanalytics.v2022_05_01.models.AnalyzeTextJobState]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        poller_cls = kwargs.pop("poller_cls", AnalyzeActionsLROPoller)  # Handwritten
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

        api_version = kwargs.pop('api_version', _params.pop('api-version', "2022-05-01"))  # type: str
        content_type = kwargs.pop('content_type',
                                  _headers.pop('Content-Type', "application/json"))  # type: Optional[str]
        cls = kwargs.pop('cls', None)  # type: ClsType[_models.AnalyzeTextJobState]
        polling = kwargs.pop('polling', True)  # type: Union[bool, PollingMethod]
        lro_delay = kwargs.pop(
            'polling_interval',
            self._config.polling_interval
        )
        cont_token = kwargs.pop('continuation_token', None)  # type: Optional[str]
        if cont_token is None:
            raw_result = self._analyze_text_submit_job_initial(  # type: ignore
                body=body,
                api_version=api_version,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs
            )
        kwargs.pop('error_map', None)

        def get_long_running_output(pipeline_response):
            deserialized = self._deserialize('AnalyzeTextJobState', pipeline_response)
            if cls:
                return cls(pipeline_response, deserialized, {})
            return deserialized

        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
        }

        if polling is True:
            polling_method = cast(PollingMethod, AnalyzeActionsLROPollingMethod(
                lro_delay,

                path_format_arguments=path_format_arguments,
                **kwargs
            ))  # type: PollingMethod
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return poller_cls.from_continuation_token(  # Handwritten
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output
            )
        return poller_cls(self._client, raw_result, get_long_running_output, polling_method)  # Handwritten

    begin_analyze_text_submit_job.metadata = {'url': "/analyze-text/jobs"}  # type: ignore


__all__: List[str] = ["TextAnalyticsClientOperationsMixin"]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
