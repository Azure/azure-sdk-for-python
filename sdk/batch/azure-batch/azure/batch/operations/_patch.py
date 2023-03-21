# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Any
import collections
import importlib
import logging
import threading
import types
import sys

__all__: List[str] = []  # Add all objects you want publicly available to users at this package level

from ..models import (
    TaskAddCollectionResult,
    TaskAddStatus,
    BatchTaskCollection,
)
from ..models._patch import CreateTasksErrorException
from ..operations import TaskOperations
from azure.core.exceptions import HttpResponseError
from azure.core.rest import HttpResponse

MAX_TASKS_PER_REQUEST = 100
_LOGGER = logging.getLogger(__name__)


class _TaskWorkflowManager(object):
    """Worker class for one add_collection request

    :param ~TaskOperations task_operations: Parent object which instantiated this
    :param str job_id: The ID of the job to which the task collection is to be
        added.
    :param tasks_to_add: The collection of tasks to add.
    :type tasks_to_add: list of :class:`TaskAddParameter
        <azure.batch.models.TaskAddParameter>`
    :param task_add_collection_options: Additional parameters for the
        operation
    :type task_add_collection_options: :class:`TaskAddCollectionOptions
        <azure.batch.models.TaskAddCollectionOptions>`
    """

    def __init__(
        self,
        client,
        original_add_collection,
        job_id: str,
        task_collection: BatchTaskCollection,
        time_out: Optional[int] = None,
        client_request_id: Optional[str] = None,
        return_client_request_id: Optional[bool] = None,
        ocp_date: Optional[str] = None,
        content_type: str = "application/json; odata=minimalmetadata",
        **kwargs
    ):
        # Append operations thread safe - Only read once all threads have completed
        # List of tasks which failed to add due to a returned client error
        self.failure_tasks = collections.deque()
        # List of unknown exceptions which occurred during requests.
        self.errors = collections.deque()

        # synchronized through lock variables
        self._max_tasks_per_request = MAX_TASKS_PER_REQUEST
        self.tasks_to_add = collections.deque(task_collection)
        self._error_lock = threading.Lock()
        self._max_tasks_lock = threading.Lock()
        self._pending_queue_lock = threading.Lock()

        # Variables to be used for task add_collection requests
        self._client = client
        self._original_add_collection = original_add_collection
        self._job_id = job_id
        self._time_out = time_out
        self._client_request_id = client_request_id
        self._return_client_request_id = return_client_request_id
        self._ocp_date = ocp_date
        self._content_type = content_type

        self._kwargs = dict(**kwargs)

    def _bulk_add_tasks(self, results_queue, chunk_tasks_to_add):
        """Adds a chunk of tasks to the job

        Retry chunk if body exceeds the maximum request size and retry tasks
        if failed due to server errors.

        :param results_queue: Queue to place the return value of the request
        :type results_queue: collections.deque
        :param chunk_tasks_to_add: Chunk of at most 100 tasks with retry details
        :type chunk_tasks_to_add: list[~TrackedCloudTask]
        """

        try:
            add_collection_response = self._original_add_collection(
                self._client,
                job_id=self._job_id,
                task_collection=BatchTaskCollection(value=chunk_tasks_to_add),
                time_out = self._time_out,
                client_request_id = self._client_request_id,
                return_client_request_id = self._return_client_request_id,
                ocp_date = self._ocp_date,
                content_type = self._content_type,
            )
        except HttpResponseError as e:
            # In case of a chunk exceeding the MaxMessageSize split chunk in half
            # and resubmit smaller chunk requests
            # TODO: Replace string with constant variable once available in SDK
            if e.error.code == "RequestBodyTooLarge":  # pylint: disable=no-member
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
                            self._max_tasks_per_request = midpoint
                            _LOGGER.info(
                                "Amount of tasks per request reduced from %s to %s due to the"
                                " request body being too large",
                                str(self._max_tasks_per_request),
                                str(midpoint),
                            )

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
            try:
                add_collection_response = add_collection_response.output
            except AttributeError:
                pass

            for task_result in add_collection_response.value:  # pylint: disable=no-member
                if task_result.status == TaskAddStatus.server_error:
                    # Server error will be retried
                    with self._pending_queue_lock:
                        for task in chunk_tasks_to_add:
                            if task.id == task_result.task_id:
                                self.tasks_to_add.appendleft(task)
                elif task_result.status == TaskAddStatus.client_error and not task_result.error.code == "TaskExists":
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

    :param results_queue: Queue containing results of attempted add_collection's
    :type results_queue: collections.deque
    :return: list of TaskAddResults
    :rtype: list[~TaskAddResult]
    """
    results = []
    while results_queue:
        queue_item = results_queue.pop()
        results.append(queue_item)
    return results


def build_new_add_collection(original_add_collection):
    def bulk_add_collection(
        self,
        job_id: str,
        task_collection: BatchTaskCollection,
        *,
        time_out: Optional[int] = None,
        client_request_id: Optional[str] = None,
        return_client_request_id: Optional[bool] = None,
        ocp_date: Optional[str] = None,
        content_type: str = "application/json; odata=minimalmetadata",
        threads=0,
        **kwargs: Any
    ) -> TaskAddCollectionResult:

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
        :type task_collection: ~azure.batch.models.BatchTaskCollection
        :keyword time_out: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out: int
        :keyword client_request_id: The caller-generated request identity, in the form of a GUID with
         no decoration
         such as curly braces, e.g. 9C4D50EE-2D56-4CD3-8152-34347DC9F2B0. Default value is None.
        :paramtype client_request_id: str
        :keyword return_client_request_id: Whether the server should return the client-request-id in
         the response. Default value is None.
        :paramtype return_client_request_id: bool
        :keyword ocp_date: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocp_date: str
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json; odata=minimalmetadata".
        :paramtype content_type: str
        :param int threads: number of threads to use in parallel when adding tasks. If specified
            and greater than 0, will start additional threads to submit requests and wait for them to finish.
            Otherwise will submit add_collection requests sequentially on main thread
        :return: :class:`TaskAddCollectionResult
            <azure.batch.models.TaskAddCollectionResult>` or
            :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>` if
            raw=true
        :rtype: :class:`TaskAddCollectionResult
            <azure.batch.models.TaskAddCollectionResult>` or
            :class:`ClientRawResponse<msrest.pipeline.ClientRawResponse>`
        :raises:
            :class:`CreateTasksErrorException<azure.batch.custom.CreateTasksErrorException>`
        """

        results_queue = collections.deque()  # deque operations(append/pop) are thread-safe
        task_workflow_manager = _TaskWorkflowManager(
            self, original_add_collection, job_id, task_collection, time_out,client_request_id, 
            return_client_request_id , ocp_date, content_type, **kwargs
        )

        # multi-threaded behavior
        if threads:
            if threads < 0:
                raise ValueError("Threads must be positive or 0")

            active_threads = []
            for i in range(threads):
                active_threads.append(
                    threading.Thread(target=task_workflow_manager.task_collection_thread_handler, args=(results_queue,))
                )
                active_threads[-1].start()
            for thread in active_threads:
                thread.join()
        # single-threaded behavior
        else:
            task_workflow_manager.task_collection_thread_handler(results_queue)

        # Only define error if all threads have finished and there were failures
        if task_workflow_manager.failure_tasks or task_workflow_manager.errors:
            raise CreateTasksErrorException(
                task_workflow_manager.tasks_to_add, task_workflow_manager.failure_tasks, task_workflow_manager.errors
            )
        else:
            submitted_tasks = _handle_output(results_queue)
            return TaskAddCollectionResult(value=submitted_tasks)

    bulk_add_collection.metadata = {"url": "/jobs/{jobId}/addtaskcollection"}
    return bulk_add_collection


def batch_error_exception_string(self):
    ret = "Request encountered an exception.\nCode: {}\nMessage: {}\n".format(self.error.code, self.error.message)
    if self.error.values:
        for error_detail in self.error.values:
            ret += "{}: {}\n".format(error_detail.key, error_detail.value)
    return ret


def build_new_get_properties_from_compute_node(original_get):
    def new_get_properties_from_compute_node( 
        self,
        pool_id: str,
        node_id: str,
        file_path: str,
        time_out: Optional[int] = None,
        client_request_id: Optional[str] = None,
        return_client_request_id: Optional[bool] = None,
        ocp_date: Optional[str] = None,
        if__modified__since: Optional[str] = None,
        if__unmodified__since: Optional[str] = None,
        **kwargs: Any
    ) -> HttpResponse:
        """Gets the properties of the specified Compute Node file.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node that contains the file. Required.
        :type node_id: str
        :param file_path: The path to the Compute Node file that you want to get the properties of.
         Required.
        :type file_path: str
        :param file_get_properties_from_compute_node_options: Parameter group. Default value is None.
        :type file_get_properties_from_compute_node_options:
         ~azure-batch.models.FileGetPropertiesFromComputeNodeOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: result of cls(response)
        :rtype: HttpResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        kwargs["cls"] = lambda pipeline_response, json_response, headers: (
            pipeline_response,
            json_response,
            headers,
        )

        get_response = original_get(self=self, pool_id=pool_id, node_id=node_id, file_path=file_path, 
        time_out=time_out, client_request_id=client_request_id, return_client_request_id=return_client_request_id,
        ocp_date=ocp_date, if__modified__since=if__modified__since, if__unmodified__since=if__unmodified__since, **kwargs)
        return get_response[0].http_response

    new_get_properties_from_compute_node.metadata = {"url": "/pools/{poolId}/nodes/{nodeId}/files/{filePath}"}  # type: ignore
    return new_get_properties_from_compute_node


def build_new_get_properties_from_task(original_get):
    def new_get_properties_from_task( 
        self,
        job_id: str,
        task_id: str,
        file_path: str,
        time_out: Optional[int] = None,
        client_request_id: Optional[str] = None,
        return_client_request_id: Optional[bool] = None,
        ocp_date: Optional[str] = None,
        if__modified__since: Optional[str] = None,
        if__unmodified__since: Optional[str] = None,
        **kwargs: Any
    ) -> HttpResponse:
        """Gets the properties of the specified Task file.

        :param job_id: The ID of the Job that contains the Task. Required.
        :type job_id: str
        :param task_id: The ID of the Task whose file you want to get the properties of. Required.
        :type task_id: str
        :param file_path: The path to the Task file that you want to get the properties of. Required.
        :type file_path: str
        :param file_get_properties_from_task_options: Parameter group. Default value is None.
        :type file_get_properties_from_task_options:
         ~azure-batch.models.FileGetPropertiesFromTaskOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: result of cls(response)
        :rtype: HttpResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        kwargs["cls"] = lambda pipeline_response, json_response, headers: (
            pipeline_response,
            json_response,
            headers,
        )

        get_response = original_get(self=self, job_id=job_id, task_id=task_id, file_path=file_path, time_out=time_out,
        client_request_id=client_request_id, return_client_request_id=return_client_request_id, ocp_date=ocp_date, 
        if__modified__since=if__modified__since, if__unmodified__since=if__unmodified__since, **kwargs)
        return get_response[0].http_response

    new_get_properties_from_task.metadata = {"url": "/jobs/{jobId}/tasks/{taskId}/files/{filePath}"}  # type: ignore
    return new_get_properties_from_task



def build_new_get_from_task(original_get):
    def new_get_from_task( 
        self,
        job_id: str,
        task_id: str,
        file_path: str,
        *,
        time_out: Optional[int] = None,
        client_request_id: Optional[str] = None,
        return_client_request_id: Optional[bool] = None,
        ocp_date: Optional[str] = None,
        if__modified__since: Optional[str] = None,
        if__unmodified__since: Optional[str] = None,
        ocp_range: Optional[str] = None,
        **kwargs: Any
    ) -> bytes:
        """Returns the content of the specified Compute Node file.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node from which you want to delete the file. Required.
        :type node_id: str
        :param file_path: The path to the file or directory that you want to delete. Required.
        :type file_path: str
        :keyword time_out: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out: int
        :keyword client_request_id: The caller-generated request identity, in the form of a GUID with
         no decoration
         such as curly braces, e.g. 9C4D50EE-2D56-4CD3-8152-34347DC9F2B0. Default value is None.
        :paramtype client_request_id: str
        :keyword return_client_request_id: Whether the server should return the client-request-id in
         the response. Default value is None.
        :paramtype return_client_request_id: bool
        :keyword ocp_date: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocp_date: str
        :keyword if__modified__since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if__modified__since: str
        :keyword if__unmodified__since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if__unmodified__since: str
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


        kwargs["stream"] = True;

        get_response = original_get(self=self, job_id=job_id, task_id=task_id, file_path=file_path, time_out=time_out,
        client_request_id=client_request_id, return_client_request_id=return_client_request_id, ocp_date=ocp_date, 
        if__modified__since=if__modified__since, if__unmodified__since=if__unmodified__since, ocp_range=ocp_range, **kwargs)
        return get_response

    new_get_from_task.metadata = {"url": "/jobs/{jobId}/tasks/{taskId}/files/{filePath}"}  # type: ignore
    return new_get_from_task


def build_new_get_from_compute_node(original_get):
    def new_get_from_compute_node( 
        self,
        pool_id: str,
        node_id: str,
        file_path: str,
        *,
        time_out: Optional[int] = None,
        client_request_id: Optional[str] = None,
        return_client_request_id: Optional[bool] = None,
        ocp_date: Optional[str] = None,
        if__modified__since: Optional[str] = None,
        if__unmodified__since: Optional[str] = None,
        ocp_range: Optional[str] = None,
        **kwargs: Any
    ) -> bytes:
        """Returns the content of the specified Compute Node file.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node from which you want to delete the file. Required.
        :type node_id: str
        :param file_path: The path to the file or directory that you want to delete. Required.
        :type file_path: str
        :keyword time_out: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out: int
        :keyword client_request_id: The caller-generated request identity, in the form of a GUID with
         no decoration
         such as curly braces, e.g. 9C4D50EE-2D56-4CD3-8152-34347DC9F2B0. Default value is None.
        :paramtype client_request_id: str
        :keyword return_client_request_id: Whether the server should return the client-request-id in
         the response. Default value is None.
        :paramtype return_client_request_id: bool
        :keyword ocp_date: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocp_date: str
        :keyword if__modified__since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if__modified__since: str
        :keyword if__unmodified__since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if__unmodified__since: str
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


        kwargs["stream"] = True;

        get_response = original_get(self=self, pool_id=pool_id, node_id=node_id, file_path=file_path, time_out=time_out,
        client_request_id=client_request_id, return_client_request_id=return_client_request_id, ocp_date=ocp_date, 
        if__modified__since=if__modified__since, if__unmodified__since=if__unmodified__since, ocp_range=ocp_range, **kwargs)
        return get_response

    new_get_from_compute_node.metadata = {"url": "/jobs/{jobId}/tasks/{taskId}/files/{filePath}"}  # type: ignore
    return new_get_from_compute_node


def build_new_get_remote_desktop(original_get):
    def new_get_remote_desktop( 
        self,
        pool_id: str,
        node_id: str,
        *,
        time_out: Optional[int] = None,
        client_request_id: Optional[str] = None,
        return_client_request_id: Optional[bool] = None,
        ocp_date: Optional[str] = None,
        **kwargs: Any
    ) -> bytes:
        """Gets the Remote Desktop Protocol file for the specified Compute Node.

        Before you can access a Compute Node by using the RDP file, you must create a
        user Account on the Compute Node. This API can only be invoked on Pools created
        with a cloud service configuration. For Pools created with a virtual machine
        configuration, see the GetRemoteLoginSettings API.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node for which you want to get the Remote Desktop
         Protocol file. Required.
        :type node_id: str
        :keyword time_out: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out: int
        :keyword client_request_id: The caller-generated request identity, in the form of a GUID with
         no decoration
         such as curly braces, e.g. 9C4D50EE-2D56-4CD3-8152-34347DC9F2B0. Default value is None.
        :paramtype client_request_id: str
        :keyword return_client_request_id: Whether the server should return the client-request-id in
         the response. Default value is None.
        :paramtype return_client_request_id: bool
        :keyword ocp_date: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocp_date: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: bytes
        :rtype: bytes
        :raises ~azure.core.exceptions.HttpResponseError:
        """


        kwargs["stream"] = True;

        get_response = original_get(self=self, pool_id=pool_id, node_id=node_id, time_out=time_out,
        client_request_id=client_request_id, return_client_request_id=return_client_request_id, ocp_date=ocp_date, 
        **kwargs)
        return get_response

    new_get_remote_desktop.metadata = {"url": "/pools/{poolId}/nodes/{nodeId}/rdp"}  # type: ignore
    return new_get_remote_desktop



def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

    try:
        models = sys.modules["azure.batch.models"]
    except KeyError:
        models = importlib.import_module("azure.batch.models")
    setattr(models, "CreateTasksErrorException", CreateTasksErrorException)
    sys.modules["azure.batch.models"] = models

    operations_modules = importlib.import_module("azure.batch.operations")
    operations_modules.TaskOperations.add_collection = build_new_add_collection(
        operations_modules.TaskOperations.add_collection
    )

    operations_modules.FileOperations.get_from_task = build_new_get_from_task(operations_modules.FileOperations.get_from_task)
    operations_modules.FileOperations.get_from_compute_node = build_new_get_from_compute_node(operations_modules.FileOperations.get_from_compute_node)
    operations_modules.FileOperations.get_properties_from_compute_node = build_new_get_properties_from_compute_node(operations_modules.FileOperations.get_properties_from_compute_node)
    operations_modules.FileOperations.get_properties_from_task = build_new_get_properties_from_task(operations_modules.FileOperations.get_properties_from_task)

    operations_modules.ComputeNodesOperations.get_remote_desktop = build_new_get_remote_desktop(operations_modules.ComputeNodesOperations.get_remote_desktop)
    models = importlib.import_module("azure.batch.models")
    # models.BatchErrorException.__str__ = batch_error_exception_string
