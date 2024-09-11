# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
from typing import Any, List, Optional
import collections
import logging
import threading

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.core.rest import HttpResponse

from .. import models as _models
from ._operations import (
    BatchClientOperationsMixin as BatchClientOperationsMixinGenerated,
)

MAX_TASKS_PER_REQUEST = 100
_LOGGER = logging.getLogger(__name__)

__all__: List[str] = [
    "BatchClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


class BatchClientOperationsMixin(BatchClientOperationsMixinGenerated):
    """Customize generated code"""

    def create_task_collection(
        self,
        job_id: str,
        task_collection: List[_models.BatchTaskCreateContent],
        concurrencies: int = 0,
        *,
        time_out_in_seconds: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> _models.BatchTaskAddCollectionResult:
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
        :keyword time_out_in_seconds: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out_in_seconds: int
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

        kwargs.update({"time_out_in_seconds": time_out_in_seconds, "ocpdate": ocpdate})

        results_queue = collections.deque()  # deque operations(append/pop) are thread-safe
        task_workflow_manager = _TaskWorkflowManager(
            super().create_task_collection, job_id=job_id, task_collection=task_collection, **kwargs
        )

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
            return _models.BatchTaskAddCollectionResult(value=submitted_tasks)

    def get_node_file(
        self,
        pool_id: str,
        node_id: str,
        file_path: str,
        *,
        time_out_in_seconds: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
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
        :keyword time_out_in_seconds: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out_in_seconds: int
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
                "time_out_in_seconds": time_out_in_seconds,
                "ocpdate": ocpdate,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
                "ocp_range": ocp_range,
            }
        )
        kwargs["stream"] = True
        return super().get_node_file(*args, **kwargs)

    def get_node_file_properties(
        self,
        pool_id: str,
        node_id: str,
        file_path: str,
        *,
        time_out_in_seconds: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> HttpResponse:
        """Gets the properties of the specified Compute Node file.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node from which you want to delete the file. Required.
        :type node_id: str
        :param file_path: The path to the file or directory that you want to delete. Required.
        :type file_path: str
        :keyword time_out_in_seconds: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out_in_seconds: int
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
        :return: HttpResponse
        :rtype: HttpResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        args = [pool_id, node_id, file_path]
        kwargs.update(
            {
                "time_out_in_seconds": time_out_in_seconds,
                "ocpdate": ocpdate,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
            }
        )

        kwargs["cls"] = lambda pipeline_response, json_response, headers: (
            pipeline_response,
            json_response,
            headers,
        )
        get_response = super().get_node_file_properties(*args, **kwargs)

        return get_response[0].http_response

    def get_task_file_properties(
        self,
        job_id: str,
        task_id: str,
        file_path: str,
        *,
        time_out_in_seconds: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> HttpResponse:
        """Gets the properties of the specified Task file.

        :param job_id: The ID of the Job that contains the Task. Required.
        :type job_id: str
        :param task_id: The ID of the Task whose file you want to retrieve. Required.
        :type task_id: str
        :param file_path: The path to the Task file that you want to get the content of. Required.
        :type file_path: str
        :keyword time_out_in_seconds: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out_in_seconds: int
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
        :return: HttpResponse
        :rtype: HttpResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        args = [job_id, task_id, file_path]
        kwargs.update(
            {
                "time_out_in_seconds": time_out_in_seconds,
                "ocpdate": ocpdate,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
            }
        )

        kwargs["cls"] = lambda pipeline_response, json_response, headers: (
            pipeline_response,
            json_response,
            headers,
        )
        get_response = super().get_task_file_properties(*args, **kwargs)

        return get_response[0].http_response

    def get_task_file(
        self,
        job_id: str,
        task_id: str,
        file_path: str,
        *,
        time_out_in_seconds: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        ocp_range: Optional[str] = None,
        **kwargs: Any
    ) -> bytes:
        """Returns the content of the specified Task file.

        :param job_id: The ID of the Job that contains the Task. Required.
        :type job_id: str
        :param task_id: The ID of the Task whose file you want to retrieve. Required.
        :type task_id: str
        :param file_path: The path to the Task file that you want to get the content of. Required.
        :type file_path: str
        :keyword time_out_in_seconds: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype time_out_in_seconds: int
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
                "time_out_in_seconds": time_out_in_seconds,
                "ocpdate": ocpdate,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
                "ocp_range": ocp_range,
            }
        )
        kwargs["stream"] = True
        return super().get_task_file(*args, **kwargs)
    
    def disable_node_scheduling(
        self,
        pool_id: str,
        node_id: str,
        parameters: Optional[_models.BatchNodeDisableSchedulingOption] = None,
        *,
        time_out_in_seconds: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> None:
        """Disables Task scheduling on the specified Compute Node.

        You can disable Task scheduling on a Compute Node only if its current
        scheduling state is enabled.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node on which you want to disable Task scheduling.
         Required.
        :type node_id: str
        :param parameters: The options to use for disabling scheduling on the Compute Node. Default
         value is None.
        :type parameters: ~azure.batch.models.BatchNodeDisableSchedulingContent
        :keyword time_out_in_seconds: The maximum time that the server can spend processing the
         request, in seconds. The default is 30 seconds. If the value is larger than 30, the default
         will be used instead.". Default value is None.
        :paramtype time_out_in_seconds: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                parameters = {
                    "nodeDisableSchedulingOption": "str"  # Optional. What to do with currently
                      running Tasks when disabling Task scheduling on the Compute Node. The default
                      value is requeue. Known values are: "requeue", "terminate", and "taskcompletion".
                }
        """
        content = _models.BatchNodeDisableSchedulingContent(
            node_disable_scheduling_option=parameters
        )
        args = [pool_id, node_id, content]
        kwargs.update(
            {
                "time_out_in_seconds": time_out_in_seconds,
                "ocpdate": ocpdate,
            }
        )
        return super().disable_node_scheduling(*args, **kwargs)

    def enable_pool_auto_scale(  # pylint: disable=inconsistent-return-statements
        self,
        pool_id: str,
        *,
        auto_scale_formula: Optional[str] = None,
        auto_scale_evaluation_interval: Optional[datetime.timedelta] = None,
        time_out_in_seconds: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> None:
        # pylint: disable=line-too-long
        """Enables automatic scaling for a Pool.

        You cannot enable automatic scaling on a Pool if a resize operation is in
        progress on the Pool. If automatic scaling of the Pool is currently disabled,
        you must specify a valid autoscale formula as part of the request. If automatic
        scaling of the Pool is already enabled, you may specify a new autoscale formula
        and/or a new evaluation interval. You cannot call this API for the same Pool
        more than once every 30 seconds.

        :param pool_id: The ID of the Pool to get. Required.
        :type pool_id: str
        :param content: The options to use for enabling automatic scaling. Required.
        :type content: ~azure.batch.models.BatchPoolEnableAutoScaleContent
        :keyword time_out_in_seconds: The maximum time that the server can spend processing the
         request, in seconds. The default is 30 seconds. If the value is larger than 30, the default
         will be used instead.". Default value is None.
        :paramtype time_out_in_seconds: int
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
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                content = {
                    "autoScaleEvaluationInterval": "1 day, 0:00:00",  # Optional. The time
                      interval at which to automatically adjust the Pool size according to the
                      autoscale formula. The default value is 15 minutes. The minimum and maximum value
                      are 5 minutes and 168 hours respectively. If you specify a value less than 5
                      minutes or greater than 168 hours, the Batch service rejects the request with an
                      invalid property value error; if you are calling the REST API directly, the HTTP
                      status code is 400 (Bad Request). If you specify a new interval, then the
                      existing autoscale evaluation schedule will be stopped and a new autoscale
                      evaluation schedule will be started, with its starting time being the time when
                      this request was issued.
                    "autoScaleFormula": "str"  # Optional. The formula for the desired number of
                      Compute Nodes in the Pool. The formula is checked for validity before it is
                      applied to the Pool. If the formula is not valid, the Batch service rejects the
                      request with detailed error information. For more information about specifying
                      this formula, see Automatically scale Compute Nodes in an Azure Batch Pool
                      (https://azure.microsoft.com/en-us/documentation/articles/batch-automatic-scaling).
                }
        """
        content = _models.BatchPoolEnableAutoScaleContent(
            auto_scale_formula=auto_scale_formula,
            auto_scale_evaluation_interval=auto_scale_evaluation_interval
        )
        args = [pool_id, content]
        kwargs.update(
            {
                "time_out_in_seconds": time_out_in_seconds,
                "ocpdate": ocpdate,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
                "etag": etag,
                "match_condition": match_condition,
            }
        )
        return super().enable_pool_auto_scale(*args, **kwargs)
    
    def terminate_job(  # pylint: disable=inconsistent-return-statements
        self,
        job_id: str,
        reason: Optional[str] = None,
        *,
        time_out_in_seconds: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> None:
        # pylint: disable=line-too-long
        """Terminates the specified Job, marking it as completed.

        When a Terminate Job request is received, the Batch service sets the Job to the
        terminating state. The Batch service then terminates any running Tasks
        associated with the Job and runs any required Job release Tasks. Then the Job
        moves into the completed state. If there are any Tasks in the Job in the active
        state, they will remain in the active state. Once a Job is terminated, new
        Tasks cannot be added and any remaining active Tasks will not be scheduled.

        :param job_id: The ID of the Job to terminate. Required.
        :type job_id: str
        :param parameters: The options to use for terminating the Job. Default value is None.
        :type parameters: ~azure.batch.models.BatchJobTerminateContent
        :keyword time_out_in_seconds: The maximum time that the server can spend processing the
         request, in seconds. The default is 30 seconds. If the value is larger than 30, the default
         will be used instead.". Default value is None.
        :paramtype time_out_in_seconds: int
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
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                parameters = {
                    "terminateReason": "str"  # Optional. The text you want to appear as the
                      Job's TerminationReason. The default is 'UserTerminate'.
                }
        """
        content = _models.BatchJobTerminateContent(
            termination_reason=reason,
        )
        args = [job_id, content]
        kwargs.update(
            {
                "time_out_in_seconds": time_out_in_seconds,
                "ocpdate": ocpdate,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
                "etag": etag,
                "match_condition": match_condition,
            }
        )
        return super().terminate_job(*args, **kwargs)

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class _TaskWorkflowManager():
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
        self, original_create_task_collection, job_id: str, task_collection: _models.BatchTaskAddCollectionResult, **kwargs
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

        # Variables to be used for task create_task_collection requests
        self._original_create_task_collection = original_create_task_collection
        self._job_id = job_id

        self._kwargs = kwargs

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
            create_task_collection_response: _models.BatchTaskAddCollectionResult = (
                self._original_create_task_collection(
                    job_id=self._job_id,
                    task_collection=_models.BatchTaskAddCollectionResult(value=chunk_tasks_to_add),
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
            try:
                create_task_collection_response = create_task_collection_response.output
            except AttributeError:
                pass

            for task_result in create_task_collection_response.value:  # pylint: disable=no-member
                if task_result.status == _models.BatchTaskAddStatus.SERVER_ERROR:
                    # Server error will be retried
                    with self._pending_queue_lock:
                        for task in chunk_tasks_to_add:
                            if task.id == task_result.task_id:
                                self.tasks_to_add.appendleft(task)
                elif (
                    task_result.status == _models.BatchTaskAddStatus.CLIENT_ERROR
                    and not task_result.error.code == "TaskExists"
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
