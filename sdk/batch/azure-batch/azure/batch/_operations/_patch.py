# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Callable, Dict, Iterable, List, Optional, TypeVar
from .. import models as _models
from ._operations import (
    BatchClientOperationsMixin as BatchClientOperationsMixinGenerated,
)
import collections
import logging
import threading
from azure.core.exceptions import HttpResponseError
from azure.core.rest import HttpResponse

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
        collection: _models.BatchTaskCollection,
        threads: Optional[int] = 0,
        **kwargs: Any
    ) -> _models.TaskAddCollectionResult:
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
        :param collection: The Tasks to be added. Required.
        :type collection: ~azure.batch.models.BatchTaskCollection
        :param threads: number of threads to use in parallel when adding tasks. If specified
        and greater than 0, will start additional threads to submit requests and wait for them to finish.
        Otherwise will submit create_task_collection requests sequentially on main thread
        :type threads: int
        :param kwargs: Additional parameters for the operation, see : `super().create_task_collection`
        :return: TaskAddCollectionResult. The TaskAddCollectionResult is compatible with MutableMapping
        :rtype: ~azure.batch.models.TaskAddCollectionResult
        :raises ~azure.batch.custom.CreateTasksErrorException
        """

        results_queue = (
            collections.deque()
        )  # deque operations(append/pop) are thread-safe
        task_workflow_manager = _TaskWorkflowManager(
            super().create_task_collection,
            job_id=job_id,
            collection=collection,
            **kwargs
        )

        # multi-threaded behavior
        if threads:
            if threads < 0:
                raise ValueError("Threads must be positive or 0")

            active_threads = []
            for i in range(threads):
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
            raise _models.CreateTasksErrorException(
                task_workflow_manager.tasks_to_add,
                task_workflow_manager.failure_tasks,
                task_workflow_manager.errors,
            )
        else:
            submitted_tasks = _handle_output(results_queue)
            return _models.TaskAddCollectionResult(value=submitted_tasks)

    def get_node_file(self, *args, **kwargs) -> Iterable[bytes]:
        kwargs["stream"] = True
        return super().get_node_file(*args, **kwargs)

    def get_node_file_properties(self, *args, **kwargs) -> HttpResponse:
        kwargs["cls"] = lambda pipeline_response, json_response, headers: (
            pipeline_response,
            json_response,
            headers,
        )
        get_response = super().get_node_file_properties(*args, **kwargs)

        return get_response[0].http_response

    def get_task_file_properties(self, *args, **kwargs) -> HttpResponse:
        kwargs["cls"] = lambda pipeline_response, json_response, headers: (
            pipeline_response,
            json_response,
            headers,
        )
        get_response = super().get_task_file_properties(*args, **kwargs)

        return get_response[0].http_response

    def get_node_remote_desktop_file(self, *args, **kwargs) -> Iterable[bytes]:
        kwargs["stream"] = True
        return super().get_node_remote_desktop_file(*args, **kwargs)

    def get_task_file(self, *args, **kwargs) -> Iterable[bytes]:
        kwargs["stream"] = True
        return super().get_task_file(*args, **kwargs)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class _TaskWorkflowManager(object):
    """Worker class for one create_task_collection request

    :param ~TaskOperations task_operations: Parent object which instantiated this
    :param str job_id: The ID of the job to which the task collection is to be
        added.
    :param tasks_to_add: The collection of tasks to add.
    :type tasks_to_add: list of :class:`TaskAddParameter
        <azure.batch.models.TaskAddParameter>`
    :param task_create_task_collection_options: Additional parameters for the
        operation
    :type task_create_task_collection_options: :class:`TaskAddCollectionOptions
        <azure.batch.models.TaskAddCollectionOptions>`
    """

    def __init__(
        self,
        original_create_task_collection,
        job_id: str,
        collection: _models.BatchTaskCollection,
        **kwargs
    ):
        # Append operations thread safe - Only read once all threads have completed
        # List of tasks which failed to add due to a returned client error
        self.failure_tasks = collections.deque()
        # List of unknown exceptions which occurred during requests.
        self.errors = collections.deque()

        # synchronized through lock variables
        self._max_tasks_per_request = MAX_TASKS_PER_REQUEST
        self.tasks_to_add = collections.deque(collection)
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
            create_task_collection_response = self._original_create_task_collection(
                job_id=self._job_id,
                collection=_models.BatchTaskCollection(value=chunk_tasks_to_add),
                **self._kwargs
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
                        "Failed to add task with ID %s due to the body"
                        " exceeding the maximum request size",
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

            for (
                task_result
            ) in create_task_collection_response.value:  # pylint: disable=no-member
                if task_result.status == _models.TaskAddStatus.server_error:
                    # Server error will be retried
                    with self._pending_queue_lock:
                        for task in chunk_tasks_to_add:
                            if task.id == task_result.task_id:
                                self.tasks_to_add.appendleft(task)
                elif (
                    task_result.status == _models.TaskAddStatus.client_error
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
