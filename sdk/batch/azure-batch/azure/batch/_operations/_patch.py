# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
import time
import json
from typing import Any, Callable, Deque, List, MutableMapping, Optional, Iterable, Iterator, overload
import collections
import logging
import threading

from azure.core import MatchConditions
from azure.core.exceptions import (
    HttpResponseError, 
    ResourceNotFoundError,
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotModifiedError,
    ResourceModifiedError,
    map_error,
)
from azure.core.polling import LROPoller
from azure.core.rest import HttpResponse, HttpRequest
from azure.core.pipeline import PipelineResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from .. import models as _models
from .._utils.model_base import SdkJSONEncoder, _deserialize, _failsafe_deserialize
from ._operations import (
    BatchClientOperationsMixin as BatchClientOperationsMixinGenerated,
    build_batch_delete_job_request,
    build_batch_remove_nodes_request,
)

# Type definitions
from typing import Dict, TypeVar
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

MAX_TASKS_PER_REQUEST = 100
_LOGGER = logging.getLogger(__name__)

__all__: List[str] = [
    "BatchClientOperationsMixin",
    "JobDeletePollingMethod"
]  # Add all objects you want publicly available to users at this package level

class JobDeletePollingMethod:
    """Polling method for job delete operation.

    This class is used to poll the status of a job deletion operation.
    It checks the status of the job until it is deleted or an error occurs.
    """

    def __init__(self, job_id: str, polling_interval: int = 5):
        # remove client to keep in initialize
        self._job_id = job_id
        self._polling_interval = polling_interval

    def initialize(
        self, 
        client: Any, 
        initial_response: PipelineResponse, 
        deserialization_callback: Optional[Callable]
    ) -> None:
        """Set the initial status of this LRO, verify that we can poll, and
        initialize anything necessary for polling.

        :param client: An instance of a client. In this example, the generated client.
        :param initial_response: In this example, the PipelineResponse returned from the initial call.
        :param deserialization_callback: A callable to transform the final result before returning to the end user.
        """

        # double checking the 202 (server accepted)

        self._client = client
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._status = "InProgress"
        self._finished = False

    def status(self) -> str:
        """Should return the current status as a string. The initial status is set by
        the polling strategy with set_initial_status() and then subsequently set by
        each call to get_status().

        This is what is returned to the user when status() is called on the LROPoller.

        :rtype: str
        """
        return self._status

    def finished(self) -> bool:
        """Is this polling finished?
        Controls whether the polling loop should continue to poll.

        :returns: Return True if the operation has reached a terminal state
            or False if polling should continue.
        :rtype: bool
        """
        return self._finished

    def resource(self) -> Optional[Any]:
        """Return the built resource.
        This is what is returned when to the user when result() is called on the LROPoller.

        This might include a deserialization callback (passed in initialize())
        to transform or customize the final result, if necessary.
        """
        if self._deserialization_callback and self._finished:
            return self._deserialization_callback()
        return None

    def run(self) -> None:
        """The polling loop.

        The polling should call the status monitor, evaluate and set the current status,
        insert delay between polls, and continue polling until a terminal state is reached.
        """
        while not self.finished():
            self.update_status()
            if not self.finished():
                # add a delay if not done
                time.sleep(self._polling_interval)

    def update_status(self):
        """Update the current status of the LRO by calling the status monitor
        and then using the polling strategy's get_status() to set the status."""
        try:
            job = self._client.get_job(self._job_id)

            # check job state is DELETING state (if not in deleting state then it's succeeded)
            if job.state != _models.BatchJobState.DELETING:
                self._status = "Succeeded"
                self._finished = True
            
        # testing an invalid job_id will throw a JobNotFound error before actually building the poller
        # probably don't need this?

        except ResourceNotFoundError: 
            # Job no longer exists, deletion is complete
            self._status = "Succeeded"
            self._finished = True
        except Exception:
            # Some other error occurred, continue polling
            self._status = "InProgress"
            self._finished = False

class BatchClientOperationsMixin(BatchClientOperationsMixinGenerated):
    """Customize generated code"""

    @distributed_trace
    def delete_job_LRO(
        self,
        job_id: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        force: Optional[bool] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> LROPoller[None]:
        """Deletes a Job with Long Running Operation support.

        Deleting a Job also deletes all Tasks that are part of that Job, and all Job
        statistics. This also overrides the retention period for Task data; that is, if
        the Job contains Tasks which are still retained on Compute Nodes, the Batch
        services deletes those Tasks' working directories and all their contents.  When
        a Delete Job request is received, the Batch service sets the Job to the
        deleting state. All update operations on a Job that is in deleting state will
        fail with status code 409 (Conflict), with additional information indicating
        that the Job is being deleted.

        :param job_id: The ID of the Job to delete. Required.
        :type job_id: str
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword force: If true, the server will delete the Job even if the corresponding nodes have
         not fully processed the deletion. The default value is false. Default value is None.
        :paramtype force: bool
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 30.
        :paramtype polling_interval: int
        :return: An LROPoller that can be used to wait for the job deletion to complete
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        # call the operations delete_job instead of copy pasting

        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        if match_condition == MatchConditions.IfNotModified:
            error_map[412] = ResourceModifiedError
        elif match_condition == MatchConditions.IfPresent:
            error_map[412] = ResourceNotFoundError
        elif match_condition == MatchConditions.IfMissing:
            error_map[412] = ResourceExistsError
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[None] = kwargs.pop("cls", None)

        _request = build_batch_delete_job_request(
            job_id=job_id,
            timeout=timeout,
            ocpdate=ocpdate,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            force=force,
            etag=etag,
            match_condition=match_condition,
            api_version=self._config.api_version,
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        _request.url = self._client.format_url(_request.url, **path_format_arguments)

        _stream = False
        pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = _failsafe_deserialize(_models.BatchError, response.json())
            raise HttpResponseError(response=response, model=error)

        response_headers = {}
        response_headers["client-request-id"] = self._deserialize("str", response.headers.get("client-request-id"))
        response_headers["request-id"] = self._deserialize("str", response.headers.get("request-id"))

        if cls:
            cls(pipeline_response, None, response_headers)

        polling_method = JobDeletePollingMethod(job_id, polling_interval)
        return LROPoller(self, pipeline_response, lambda: None, polling_method, **kwargs)

    # @distributed_trace
    # def remove_nodes_LRO(
    #     self,
    #     pool_id: str,
    #     content: _models.BatchNodeRemoveOptions,
    #     *,
    #     timeout: Optional[int] = None,
    #     ocpdate: Optional[datetime.datetime] = None,
    #     if_modified_since: Optional[datetime.datetime] = None,
    #     if_unmodified_since: Optional[datetime.datetime] = None,
    #     etag: Optional[str] = None,
    #     match_condition: Optional[MatchConditions] = None,
    #     **kwargs: Any
    # ) -> LROPoller:
    #     error_map: MutableMapping = {
    #         401: ClientAuthenticationError,
    #         404: ResourceNotFoundError,
    #         409: ResourceExistsError,
    #         304: ResourceNotModifiedError,
    #     }
    #     if match_condition == MatchConditions.IfNotModified:
    #         error_map[412] = ResourceModifiedError
    #     elif match_condition == MatchConditions.IfPresent:
    #         error_map[412] = ResourceNotFoundError
    #     elif match_condition == MatchConditions.IfMissing:
    #         error_map[412] = ResourceExistsError
    #     error_map.update(kwargs.pop("error_map", {}) or {})

    #     _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    #     _params = kwargs.pop("params", {}) or {}

    #     content_type: str = kwargs.pop(
    #         "content_type", _headers.pop("content-type", "application/json; odata=minimalmetadata")
    #     )
    #     cls: ClsType[None] = kwargs.pop("cls", None)

    #     _content = json.dumps(content, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

    #     _request = build_batch_remove_nodes_request(
    #         pool_id=pool_id,
    #         timeout=timeout,
    #         ocpdate=ocpdate,
    #         if_modified_since=if_modified_since,
    #         if_unmodified_since=if_unmodified_since,
    #         etag=etag,
    #         match_condition=match_condition,
    #         content_type=content_type,
    #         api_version=self._config.api_version,
    #         content=_content,
    #         headers=_headers,
    #         params=_params,
    #     )
    #     path_format_arguments = {
    #         "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
    #     }
    #     _request.url = self._client.format_url(_request.url, **path_format_arguments)

    #     _stream = False
    #     pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
    #         _request, stream=_stream, **kwargs
    #     )

    #     response = pipeline_response.http_response

    #     if response.status_code not in [202]:
    #         map_error(status_code=response.status_code, response=response, error_map=error_map)
    #         error = _failsafe_deserialize(_models.BatchError, response.json())
    #         raise HttpResponseError(response=response, model=error)

    #     response_headers = {}
    #     response_headers["DataServiceId"] = self._deserialize("str", response.headers.get("DataServiceId"))
    #     response_headers["ETag"] = self._deserialize("str", response.headers.get("ETag"))
    #     response_headers["Last-Modified"] = self._deserialize("rfc-1123", response.headers.get("Last-Modified"))
    #     response_headers["client-request-id"] = self._deserialize("str", response.headers.get("client-request-id"))
    #     response_headers["request-id"] = self._deserialize("str", response.headers.get("request-id"))

    #     if cls:
    #         return cls(pipeline_response, None, response_headers)  # type: ignore
        
    #     # follow pool state (once stat is steady then finished)
    #     return LROPoller(self._client, response, deserialization_callback=None, **kwargs)  # type: ignore

    # create_task_collection renamed
    @distributed_trace
    def create_tasks(
        self,
        job_id: str,
        task_collection: List[_models.BatchTaskCreateOptions],
        concurrencies: int = 0,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> _models.BatchCreateTaskCollectionResult:
        """Adds a collection of Tasks to the specified Job.

        Note that each Task must have a unique ID. The Batch service may not return the
        results for each Task in the same order the Tasks were submitted in this
        request. If the server times out or the connection is closed during the
        request, the request may have been partially or fully processed, or not at all.
        In such cases, the user should re-issue the request. Note that it is up to the
        user to correctly handle failures when re-issuing a request. For example, you
        should use the same Task IDs during a retry so that if the prior operation
        succeeded, the retry will not create extra Tasks unexpectedly. If the response
        contains any Tasks which failed to add, a client can retry the request. In a
        retry, it is most efficient to resubmit only Tasks that failed to add, and to
        omit Tasks that were successfully added on the first attempt. The maximum
        lifetime of a Task from addition to completion is 180 days. If a Task has not
        completed within 180 days of being added it will be terminated by the Batch
        service and left in whatever state it was in at that time.

        :param job_id: The ID of the Job to which the Task collection is to be added. Required.
        :type job_id: str
        :param task_collection: The Tasks to be added. Required.
        :type task_collection: ~azure.batch.models.BatchTaskAddCollectionResult
        :param concurrencies: number of threads to use in parallel when adding tasks. If specified
        and greater than 0, will start additional threads to submit requests and wait for them to finish.
        Otherwise will submit create_task_collection requests sequentially on main thread
        :type concurrencies: int
        :keyword timeout: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword content_type: Type of content. Default value is "application/json;
         odata=minimalmetadata".
        :paramtype content_type: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: BatchTaskAddCollectionResult. The BatchTaskAddCollectionResult is compatible with MutableMapping
        :rtype: ~azure.batch.models.BatchTaskAddCollectionResult
        :raises ~azure.batch.custom.CreateTasksError
        """

        kwargs.update({"timeout": timeout, "ocpdate": ocpdate})

        # deque operations(append/pop) are thread-safe
        results_queue: Deque[_models.BatchTaskCreateResult] = collections.deque()
        task_workflow_manager = _TaskWorkflowManager(self, job_id=job_id, task_collection=task_collection, **kwargs)

        # multi-threaded behavior
        if concurrencies:
            if concurrencies < 0:
                raise ValueError("Concurrencies must be positive or 0")

            active_threads = []
            for i in range(concurrencies):
                active_threads.append(
                    threading.Thread(
                        target=task_workflow_manager.task_collection_thread_handler,
                        args=(results_queue,),
                    )
                )
                active_threads[-1].start()
            for thread in active_threads:
                thread.join()
        # single-threaded behavior
        else:
            task_workflow_manager.task_collection_thread_handler(results_queue)

        # Only define error if all threads have finished and there were failures
        if task_workflow_manager.failure_tasks or task_workflow_manager.errors:
            raise _models.CreateTasksError(
                task_workflow_manager.tasks_to_add,
                task_workflow_manager.failure_tasks,
                task_workflow_manager.errors,
            )
        else:
            submitted_tasks = _handle_output(results_queue)
            return _models.BatchCreateTaskCollectionResult(values_property=submitted_tasks)

    @distributed_trace
    def get_node_file(
        self,
        pool_id: str,
        node_id: str,
        file_path: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        ocp_range: Optional[str] = None,
        **kwargs: Any
    ) -> Iterator[bytes]:
        """Returns the content of the specified Compute Node file.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node from which you want to delete the file. Required.
        :type node_id: str
        :param file_path: The path to the file or directory that you want to delete. Required.
        :type file_path: str
        :keyword timeout: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword ocp_range: The byte range to be retrieved. The default is to retrieve the entire file.
         The
         format is bytes=startRange-endRange. Default value is None.
        :paramtype ocp_range: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: bytes
        :rtype: bytes
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        args = [pool_id, node_id, file_path]
        kwargs.update(
            {
                "timeout": timeout,
                "ocpdate": ocpdate,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
                "ocp_range": ocp_range,
            }
        )
        kwargs["stream"] = True
        return super().get_node_file(*args, **kwargs)

    @distributed_trace
    def get_node_file_properties(
        self,
        pool_id: str,
        node_id: str,
        file_path: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> _models.BatchFileProperties:
        """Gets the properties of the specified Compute Node file.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node from which you want to delete the file. Required.
        :type node_id: str
        :param file_path: The path to the file or directory that you want to delete. Required.
        :type file_path: str
        :keyword timeout: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: BatchFileProperties
        :rtype: ~azure.batch.models.BatchFileProperties
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        cls = lambda pipeline_response, json_response, headers: _models.BatchFileProperties(
            url=headers["ocp-batch-file-url"],
            is_directory=headers["ocp-batch-file-isdirectory"],
            last_modified=headers["Last-Modified"],
            content_length=headers["Content-Length"],
            creation_time=headers["ocp-creation-time"],
            # content_type=headers["Content-Type"], # need to add to typespec
            file_mode=headers["ocp-batch-file-mode"],
        )

        get_response: _models.BatchFileProperties = super()._get_node_file_properties_internal(  # type: ignore
            pool_id,
            node_id,
            file_path,
            timeout=timeout,
            ocpdate=ocpdate,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            cls=cls,
            **kwargs
        )

        return get_response

    @distributed_trace
    def get_task_file_properties(
        self,
        job_id: str,
        task_id: str,
        file_path: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> _models.BatchFileProperties:
        """Gets the properties of the specified Task file.

        :param job_id: The ID of the Job that contains the Task. Required.
        :type job_id: str
        :param task_id: The ID of the Task whose file you want to retrieve. Required.
        :type task_id: str
        :param file_path: The path to the Task file that you want to get the content of. Required.
        :type file_path: str
        :keyword timeout: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: BatchFileProperties
        :rtype: ~azure.batch.models.BatchFileProperties
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        cls = lambda pipeline_response, json_response, headers: _models.BatchFileProperties(
            url=headers["ocp-batch-file-url"],
            is_directory=headers["ocp-batch-file-isdirectory"],
            last_modified=headers["Last-Modified"],
            content_length=headers["Content-Length"],
            creation_time=headers["ocp-creation-time"],
            # content_type=headers["Content-Type"], # need to add to typespec
            file_mode=headers["ocp-batch-file-mode"],
        )

        get_response: _models.BatchFileProperties = super()._get_task_file_properties_internal(  # type: ignore
            job_id,
            task_id,
            file_path,
            timeout=timeout,
            ocpdate=ocpdate,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            cls=cls,
            **kwargs
        )

        return get_response

    @distributed_trace
    def get_task_file(
        self,
        job_id: str,
        task_id: str,
        file_path: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        ocp_range: Optional[str] = None,
        **kwargs: Any
    ) -> Iterator[bytes]:
        """Returns the content of the specified Task file.

        :param job_id: The ID of the Job that contains the Task. Required.
        :type job_id: str
        :param task_id: The ID of the Task whose file you want to retrieve. Required.
        :type task_id: str
        :param file_path: The path to the Task file that you want to get the content of. Required.
        :type file_path: str
        :keyword timeout: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword ocp_range: The byte range to be retrieved. The default is to retrieve the entire file.
         The
         format is bytes=startRange-endRange. Default value is None.
        :paramtype ocp_range: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: bytes
        :rtype: bytes
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        args = [job_id, task_id, file_path]
        kwargs.update(
            {
                "timeout": timeout,
                "ocpdate": ocpdate,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
                "ocp_range": ocp_range,
            }
        )
        kwargs["stream"] = True
        return super().get_task_file(*args, **kwargs)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class _TaskWorkflowManager:
    """Worker class for one create_task_collection request

    :param ~TaskOperations task_operations: Parent object which instantiated this
    :param str job_id: The ID of the job to which the task collection is to be
        added.
    :param tasks_to_add: The collection of tasks to add.
    :type tasks_to_add: list of :class:`TaskAddParameter
        <azure.batch.models.TaskAddParameter>`
    :param task_create_task_collection_options: Additional parameters for the
        operation
    :type task_create_task_collection_options: :class:`BatchTaskAddCollectionResult
        <azure.batch.models.BatchTaskAddCollectionResult>`
    """

    def __init__(
        self,
        batch_client: BatchClientOperationsMixin,
        job_id: str,
        task_collection: Iterable[_models.BatchTaskCreateOptions],
        **kwargs
    ):
        # Append operations thread safe - Only read once all threads have completed
        # List of tasks which failed to add due to a returned client error
        self.failure_tasks: Deque[_models.BatchTaskCreateResult] = collections.deque()
        # List of unknown exceptions which occurred during requests.
        self.errors: Deque[Any] = collections.deque()

        # synchronized through lock variables
        self._max_tasks_per_request = MAX_TASKS_PER_REQUEST
        self.tasks_to_add = collections.deque(task_collection)
        self._error_lock = threading.Lock()
        self._max_tasks_lock = threading.Lock()
        self._pending_queue_lock = threading.Lock()

        # Variables to be used for task create_task_collection requests
        self._batch_client = batch_client
        self._job_id = job_id

        self._kwargs = kwargs

    def _bulk_add_tasks(
        self, 
        results_queue: collections.deque, 
        chunk_tasks_to_add: List[_models.BatchTaskCreateOptions],
    ):
        """Adds a chunk of tasks to the job

        Retry chunk if body exceeds the maximum request size and retry tasks
        if failed due to server errors.

        :param results_queue: Queue to place the return value of the request
        :type results_queue: collections.deque
        :param chunk_tasks_to_add: Chunk of at most 100 tasks with retry details
        :type chunk_tasks_to_add: list[~BatchTaskAddResult]
        """

        try:
            create_task_collection_response: _models.BatchCreateTaskCollectionResult = (
                self._batch_client.create_task_collection(
                    job_id=self._job_id,
                    task_collection=_models.BatchTaskGroup(values_property=chunk_tasks_to_add),
                    **self._kwargs
                )
            )
        except HttpResponseError as e:
            # In case of a chunk exceeding the MaxMessageSize split chunk in half
            # and resubmit smaller chunk requests
            # TODO: Replace string with constant variable once available in SDK
            if e.error and e.error.code == "RequestBodyTooLarge":  # pylint: disable=no-member
                # In this case the task is misbehaved and will not be able to be added due to:
                #   1) The task exceeding the max message size
                #   2) A single cell of the task exceeds the per-cell limit, or
                #   3) Sum of all cells exceeds max row limit
                if len(chunk_tasks_to_add) == 1:
                    failed_task = chunk_tasks_to_add.pop()
                    self.errors.appendleft(e)
                    _LOGGER.error(
                        "Failed to add task with ID %s due to the body" " exceeding the maximum request size",
                        failed_task.id,
                    )
                else:
                    # Assumption: Tasks are relatively close in size therefore if one batch exceeds size limit
                    # we should decrease the initial task collection size to avoid repeating the error
                    # Midpoint is lower bounded by 1 due to above base case
                    midpoint = int(len(chunk_tasks_to_add) / 2)
                    # Restrict one thread at a time to do this compare and set,
                    # therefore forcing max_tasks_per_request to be strictly decreasing
                    with self._max_tasks_lock:
                        if midpoint < self._max_tasks_per_request:
                            _LOGGER.info(
                                "Amount of tasks per request reduced from %s to %s due to the"
                                " request body being too large",
                                str(self._max_tasks_per_request),
                                str(midpoint),
                            )
                            self._max_tasks_per_request = midpoint

                    # Not the most efficient solution for all cases, but the goal of this is to handle this
                    # exception and have it work in all cases where tasks are well behaved
                    # Behavior retries as a smaller chunk and
                    # appends extra tasks to queue to be picked up by another thread .
                    self.tasks_to_add.extendleft(chunk_tasks_to_add[midpoint:])
                    self._bulk_add_tasks(results_queue, chunk_tasks_to_add[:midpoint])
            # Retry server side errors
            elif 500 <= e.response.status_code <= 599:
                self.tasks_to_add.extendleft(chunk_tasks_to_add)
            else:
                # Re-add to pending queue as unknown status / don't have result
                self.tasks_to_add.extendleft(chunk_tasks_to_add)
                # Unknown State - don't know if tasks failed to add or were successful
                self.errors.appendleft(e)
        except Exception as e:  # pylint: disable=broad-except
            # Re-add to pending queue as unknown status / don't have result
            self.tasks_to_add.extendleft(chunk_tasks_to_add)
            # Unknown State - don't know if tasks failed to add or were successful
            self.errors.appendleft(e)
        else:
            if create_task_collection_response.values_property:
                for task_result in create_task_collection_response.values_property:  # pylint: disable=no-member
                    if task_result.status == _models.BatchTaskAddStatus.SERVER_ERROR:
                        # Server error will be retried
                        with self._pending_queue_lock:
                            for task in chunk_tasks_to_add:
                                if task.id == task_result.task_id:
                                    self.tasks_to_add.appendleft(task)
                    elif task_result.status == _models.BatchTaskAddStatus.CLIENT_ERROR and not (
                        task_result.error and task_result.error.code == "TaskExists"
                    ):
                        # Client error will be recorded unless Task already exists
                        self.failure_tasks.appendleft(task_result)
                    else:
                        results_queue.appendleft(task_result)

    def task_collection_thread_handler(self, results_queue):
        """Main method for worker to run

        Pops a chunk of tasks off the collection of pending tasks to be added and submits them to be added.

        :param collections.deque results_queue: Queue for worker to output results to
        """
        # Add tasks until either we run out or we run into an unexpected error
        while self.tasks_to_add and not self.errors:
            max_tasks = self._max_tasks_per_request  # local copy
            chunk_tasks_to_add = []
            with self._pending_queue_lock:
                while len(chunk_tasks_to_add) < max_tasks and self.tasks_to_add:
                    chunk_tasks_to_add.append(self.tasks_to_add.pop())

            if chunk_tasks_to_add:
                self._bulk_add_tasks(results_queue, chunk_tasks_to_add)


def _handle_output(results_queue):
    """Scan output for exceptions

    If there is an output from an add task collection call add it to the results.

    :param results_queue: Queue containing results of attempted create_task_collection's
    :type results_queue: collections.deque
    :return: list of TaskAddResults
    :rtype: list[~TaskAddResult]
    """
    results = []
    while results_queue:
        queue_item = results_queue.pop()
        results.append(queue_item)
    return results
