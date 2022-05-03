# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

# This file is used for handwritten extensions to the generated code. Example:
# https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/customize_code/how-to-patch-sdk-code.md
import importlib
from .operations import TextAnalyticsClientOperationsMixin as GeneratedTextAnalyticsClientOperationsMixin
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from ....aio._lro_async import AsyncAnalyzeActionsLROPoller, AsyncAnalyzeActionsLROPollingMethod
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import AsyncHttpResponse
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async

from .. import models as _models
from .._vendor import _convert_request
from ..operations._text_analytics_client_operations import build_analyze_text_cancel_job_request_initial, build_analyze_text_job_status_request, build_analyze_text_request, build_analyze_text_submit_job_request_initial
T = TypeVar('T')
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]


def patch_sdk():
    class TextAnalyticsClientOperationsMixin(GeneratedTextAnalyticsClientOperationsMixin):

        @distributed_trace_async
        async def analyze_text(
                self,
                body: "_models.AnalyzeTextTask",
                show_stats: Optional[bool] = None,
                **kwargs: Any
        ) -> "_models.AnalyzeTextTaskResult":
            """Request text analysis over a collection of documents.

            Submit a collection of text documents for analysis.  Specify a single unique task to be
            executed immediately.

            :param body: Collection of documents to analyze and a single task to execute.
            :type body: ~azure.ai.textanalytics.v2022_04_01_preview.models.AnalyzeTextTask
            :param show_stats: (Optional) if set to true, response will contain request and document level
             statistics.
            :type show_stats: bool
            :keyword callable cls: A custom type or function that will be passed the direct response
            :return: AnalyzeTextTaskResult, or the result of cls(response)
            :rtype: ~azure.ai.textanalytics.v2022_04_01_preview.models.AnalyzeTextTaskResult
            :raises: ~azure.core.exceptions.HttpResponseError
            """
            cls = kwargs.pop('cls', None)  # type: ClsType["_models.AnalyzeTextTaskResult"]
            error_map = {
                401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
            }
            error_map.update(kwargs.pop('error_map', {}))

            api_version = kwargs.pop('api_version', "2022-04-01-preview")  # type: str
            content_type = kwargs.pop('content_type', "application/json")  # type: Optional[str]

            _json = self._serialize.body(body, 'AnalyzeTextTask')

            request = build_analyze_text_request(
                api_version=api_version,
                content_type=content_type,
                json=_json,
                show_stats=show_stats,
                template_url=self.analyze_text.metadata['url'],
            )
            request = _convert_request(request)
            path_format_arguments = {
                "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
            }
            request.url = self._client.format_url(request.url, **path_format_arguments)

            pipeline_response = await self._client._pipeline.run(  # pylint: disable=protected-access
                request,
                stream=False,
                **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(_models.ErrorResponse, pipeline_response)
                raise HttpResponseError(response=response, model=error)

            deserialized = self._deserialize('AnalyzeTextTaskResult', pipeline_response)

            if cls:
                return cls(pipeline_response, deserialized, {})

            return deserialized

        analyze_text.metadata = {'url': "/:analyze-text"}  # type: ignore

        async def _analyze_text_submit_job_initial(
                self,
                body: "_models.AnalyzeTextJobsInput",
                **kwargs: Any
        ) -> Optional["_models.AnalyzeTextJobState"]:
            cls = kwargs.pop('cls', None)  # type: ClsType[Optional["_models.AnalyzeTextJobState"]]
            error_map = {
                401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
            }
            error_map.update(kwargs.pop('error_map', {}))

            api_version = kwargs.pop('api_version', "2022-04-01-preview")  # type: str
            content_type = kwargs.pop('content_type', "application/json")  # type: Optional[str]

            _json = self._serialize.body(body, 'AnalyzeTextJobsInput')

            request = build_analyze_text_submit_job_request_initial(
                api_version=api_version,
                content_type=content_type,
                json=_json,
                template_url=self._analyze_text_submit_job_initial.metadata['url'],
            )
            request = _convert_request(request)
            path_format_arguments = {
                "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
            }
            request.url = self._client.format_url(request.url, **path_format_arguments)

            pipeline_response = await self._client._pipeline.run(  # pylint: disable=protected-access
                request,
                stream=False,
                **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200, 202]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            deserialized = None
            response_headers = {}
            if response.status_code == 200:
                deserialized = self._deserialize('AnalyzeTextJobState', pipeline_response)

            if response.status_code == 202:
                response_headers['Operation-Location'] = self._deserialize('str',
                                                                           response.headers.get('Operation-Location'))

            if cls:
                return cls(pipeline_response, deserialized, response_headers)

            return deserialized

        _analyze_text_submit_job_initial.metadata = {'url': "/analyze-text/jobs"}  # type: ignore

        @distributed_trace_async
        async def begin_analyze_text_submit_job(
                self,
                body: "_models.AnalyzeTextJobsInput",
                **kwargs: Any
        ) -> AsyncAnalyzeActionsLROPoller["_models.AnalyzeTextJobState"]:
            """Submit text analysis job.

            Submit a collection of text documents for analysis. Specify one or more unique tasks to be
            executed as a long-running operation.

            :param body: Collection of documents to analyze and one or more tasks to execute.
            :type body: ~azure.ai.textanalytics.v2022_04_01_preview.models.AnalyzeTextJobsInput
            :keyword callable cls: A custom type or function that will be passed the direct response
            :keyword str continuation_token: A continuation token to restart a poller from a saved state.
            :keyword polling: By default, your polling method will be AsyncAnalyzeActionsLROPollingMethod.
             Pass in False for this operation to not poll, or pass in your own initialized polling object
             for a personal polling strategy.
            :paramtype polling: bool or ~azure.core.polling.AsyncPollingMethod
            :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
             Retry-After header is present.
            :return: An instance of AsyncAnalyzeActionsLROPoller that returns either AnalyzeTextJobState or
             the result of cls(response)
            :rtype:
             ~.....aio._lro_async.AsyncAnalyzeActionsLROPoller[~azure.ai.textanalytics.v2022_04_01_preview.models.AnalyzeTextJobState]
            :raises: ~azure.core.exceptions.HttpResponseError
            """
            poller_cls = kwargs.pop("poller_cls", AsyncAnalyzeActionsLROPoller)  # Handwritten
            api_version = kwargs.pop('api_version', "2022-04-01-preview")  # type: str
            content_type = kwargs.pop('content_type', "application/json")  # type: Optional[str]
            polling = kwargs.pop('polling', True)  # type: Union[bool, AsyncPollingMethod]
            cls = kwargs.pop('cls', None)  # type: ClsType["_models.AnalyzeTextJobState"]
            lro_delay = kwargs.pop(
                'polling_interval',
                self._config.polling_interval
            )
            cont_token = kwargs.pop('continuation_token', None)  # type: Optional[str]
            if cont_token is None:
                raw_result = await self._analyze_text_submit_job_initial(
                    body=body,
                    api_version=api_version,
                    content_type=content_type,
                    cls=lambda x, y, z: x,
                    **kwargs
                )
            kwargs.pop('error_map', None)

            def get_long_running_output(pipeline_response):
                response = pipeline_response.http_response
                deserialized = self._deserialize('AnalyzeTextJobState', pipeline_response)
                if cls:
                    return cls(pipeline_response, deserialized, {})
                return deserialized

            path_format_arguments = {
                "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
            }

            if polling is True:
                polling_method = AsyncAnalyzeActionsLROPollingMethod(lro_delay,
                                                                     path_format_arguments=path_format_arguments,
                                                                     **kwargs)
            elif polling is False:
                polling_method = AsyncNoPolling()
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

        @distributed_trace_async
        async def analyze_text_job_status(
                self,
                job_id: str,
                show_stats: Optional[bool] = None,
                top: Optional[int] = None,
                skip: Optional[int] = None,
                **kwargs: Any
        ) -> "_models.AnalyzeTextJobState":
            """Get analysis status and results.

            Get the status of an analysis job.  A job may consist of one or more tasks.  Once all tasks are
            succeeded, the job will transition to the succeeded state and results will be available for
            each task.

            :param job_id: Job ID.
            :type job_id: str
            :param show_stats: (Optional) if set to true, response will contain request and document level
             statistics.
            :type show_stats: bool
            :param top: The maximum number of resources to return from the collection.
            :type top: int
            :param skip: An offset into the collection of the first resource to be returned.
            :type skip: int
            :keyword callable cls: A custom type or function that will be passed the direct response
            :return: AnalyzeTextJobState, or the result of cls(response)
            :rtype: ~azure.ai.textanalytics.v2022_04_01_preview.models.AnalyzeTextJobState
            :raises: ~azure.core.exceptions.HttpResponseError
            """
            cls = kwargs.pop('cls', None)  # type: ClsType["_models.AnalyzeTextJobState"]
            error_map = {
                401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
            }
            error_map.update(kwargs.pop('error_map', {}))

            api_version = kwargs.pop('api_version', "2022-04-01-preview")  # type: str

            request = build_analyze_text_job_status_request(
                job_id=job_id,
                api_version=api_version,
                show_stats=show_stats,
                top=top,
                skip=skip,
                template_url=self.analyze_text_job_status.metadata['url'],
            )
            request = _convert_request(request)
            path_format_arguments = {
                "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
            }
            request.url = self._client.format_url(request.url, **path_format_arguments)

            pipeline_response = await self._client._pipeline.run(  # pylint: disable=protected-access
                request,
                stream=False,
                **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(_models.ErrorResponse, pipeline_response)
                raise HttpResponseError(response=response, model=error)

            deserialized = self._deserialize('AnalyzeTextJobState', pipeline_response)

            if cls:
                return cls(pipeline_response, deserialized, {})

            return deserialized

        analyze_text_job_status.metadata = {'url': "/analyze-text/jobs/{jobId}"}  # type: ignore

        async def _analyze_text_cancel_job_initial(  # pylint: disable=inconsistent-return-statements
                self,
                job_id: str,
                **kwargs: Any
        ) -> None:
            cls = kwargs.pop('cls', None)  # type: ClsType[None]
            error_map = {
                401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
            }
            error_map.update(kwargs.pop('error_map', {}))
            api_version = kwargs.pop('api_version', "2022-04-01-preview")  # type: str
            request = build_analyze_text_cancel_job_request_initial(
                job_id=job_id,
                api_version=api_version,
                template_url=self._analyze_text_cancel_job_initial.metadata['url'],
            )
            request = _convert_request(request)
            path_format_arguments = {
                "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
            }
            request.url = self._client.format_url(request.url, **path_format_arguments)

            pipeline_response = await self._client._pipeline.run(  # pylint: disable=protected-access
                request,
                stream=False,
                **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [202]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            response_headers = {}
            response_headers['Operation-Location'] = self._deserialize('str',
                                                                       response.headers.get('Operation-Location'))

            if cls:
                return cls(pipeline_response, None, response_headers)

        _analyze_text_cancel_job_initial.metadata = {'url': "/analyze-text/jobs/{jobId}:cancel"}  # type: ignore

        @distributed_trace_async
        async def begin_analyze_text_cancel_job(  # pylint: disable=inconsistent-return-statements
                self,
                job_id: str,
                **kwargs: Any
        ) -> AsyncLROPoller[None]:
            """Cancel a long-running Text Analysis job.

            Cancel a long-running Text Analysis job.

            :param job_id: Job ID.
            :type job_id: str
            :keyword callable cls: A custom type or function that will be passed the direct response
            :keyword str continuation_token: A continuation token to restart a poller from a saved state.
            :keyword polling: By default, your polling method will be AsyncLROBasePolling. Pass in False
             for this operation to not poll, or pass in your own initialized polling object for a personal
             polling strategy.
            :paramtype polling: bool or ~azure.core.polling.AsyncPollingMethod
            :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
             Retry-After header is present.
            :return: An instance of AsyncLROPoller that returns either None or the result of cls(response)
            :rtype: ~azure.core.polling.AsyncLROPoller[None]
            :raises: ~azure.core.exceptions.HttpResponseError
            """
            api_version = kwargs.pop('api_version', "2022-04-01-preview")  # type: str
            polling = kwargs.pop('polling', True)  # type: Union[bool, AsyncPollingMethod]
            cls = kwargs.pop('cls', None)  # type: ClsType[None]
            lro_delay = kwargs.pop(
                'polling_interval',
                self._config.polling_interval
            )
            cont_token = kwargs.pop('continuation_token', None)  # type: Optional[str]
            if cont_token is None:
                raw_result = await self._analyze_text_cancel_job_initial(
                    job_id=job_id,
                    api_version=api_version,
                    cls=lambda x, y, z: x,
                    **kwargs
                )
            kwargs.pop('error_map', None)

            def get_long_running_output(pipeline_response):
                if cls:
                    return cls(pipeline_response, None, {})

            path_format_arguments = {
                "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
            }

            if polling is True:
                polling_method = AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs)
            elif polling is False:
                polling_method = AsyncNoPolling()
            else:
                polling_method = polling
            if cont_token:
                return AsyncLROPoller.from_continuation_token(
                    polling_method=polling_method,
                    continuation_token=cont_token,
                    client=self._client,
                    deserialization_callback=get_long_running_output
                )
            return AsyncLROPoller(self._client, raw_result, get_long_running_output, polling_method)

        begin_analyze_text_cancel_job.metadata = {'url': "/analyze-text/jobs/{jobId}:cancel"}  # type: ignore

    curr_package = importlib.import_module("azure.ai.textanalytics._generated.v2022_04_01_preview.aio.operations")
    curr_package.TextAnalyticsClientOperationsMixin = TextAnalyticsClientOperationsMixin
