import collections
import importlib
import logging
import threading
import types
import sys

from ..models import BatchErrorException, TaskAddCollectionResult, TaskAddStatus
from ..custom.custom_errors import CreateTasksErrorException
from ..operations._task_operations import TaskOperations

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
    :param dict custom_headers: headers that will be added to the request
    :param bool raw: returns the direct response alongside the
        deserialized response
    """

    def __init__(
            self,
            client,
            original_add_collection,
            job_id,
            tasks_to_add,
            task_add_collection_options=None,
            custom_headers=None,
            raw=False,
            **kwargs):
        # Append operations thread safe - Only read once all threads have completed
        # List of tasks which failed to add due to a returned client error
        self.failure_tasks = collections.deque()
        # List of unknown exceptions which occurred during requests.
        self.errors = collections.deque()

        # synchronized through lock variables
        self._max_tasks_per_request = MAX_TASKS_PER_REQUEST
        self.tasks_to_add = collections.deque(tasks_to_add)

        self._error_lock = threading.Lock()
        self._max_tasks_lock = threading.Lock()
        self._pending_queue_lock = threading.Lock()

        # Variables to be used for task add_collection requests
        self._client = client
        self._original_add_collection = original_add_collection
        self._job_id = job_id
        self._task_add_collection_options = task_add_collection_options
        self._custom_headers = custom_headers
        self._raw = raw
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
                self._job_id,
                chunk_tasks_to_add,
                self._task_add_collection_options,
                self._custom_headers,
                self._raw)
        except BatchErrorException as e:
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
                    _LOGGER.error("Failed to add task with ID %s due to the body"
                                  " exceeding the maximum request size", failed_task.id)
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
                            _LOGGER.info("Amount of tasks per request reduced from %s to %s due to the"
                                         " request body being too large", str(self._max_tasks_per_request),
                                         str(midpoint))

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
                elif (task_result.status == TaskAddStatus.client_error
                        and not task_result.error.code == "TaskExists"):
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
            job_id,
            value,
            task_add_collection_options=None,
            custom_headers=None,
            raw=False,
            threads=0,
            **operation_config):
        """Adds a collection of tasks to the specified job.

        Note that each task must have a unique ID. The Batch service may not
        return the results for each task in the same order the tasks were
        submitted in this request. If the server times out or the connection is
        closed during the request, the request may have been partially or fully
        processed, or not at all. In such cases, the user should re-issue the
        request. Note that it is up to the user to correctly handle failures
        when re-issuing a request. For example, you should use the same task
        IDs during a retry so that if the prior operation succeeded, the retry
        will not create extra tasks unexpectedly. If the response contains any
        tasks which failed to add, a client can retry the request. In a retry,
        it is most efficient to resubmit only tasks that failed to add, and to
        omit tasks that were successfully added on the first attempt. The 
        maximum lifetime of a task from addition to completion is 180 days.
        If a task has not completed within 180 days of being added it will be
        terminated by the Batch service and left in whatever state it was in at
        that time.

        :param job_id: The ID of the job to which the task collection is to be
            added.
        :type job_id: str
        :param value: The collection of tasks to add. The total serialized
            size of this collection must be less than 4MB. If it is greater than
            4MB (for example if each task has 100's of resource files or
            environment variables), the request will fail with code
            'RequestBodyTooLarge' and should be retried again with fewer tasks.
        :type value: list of :class:`TaskAddParameter
            <azure.batch.models.TaskAddParameter>`
        :param task_add_collection_options: Additional parameters for the
            operation
        :type task_add_collection_options: :class:`TaskAddCollectionOptions
            <azure.batch.models.TaskAddCollectionOptions>`
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
            deserialized response
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
            self,
            original_add_collection,
            job_id,
            value,
            task_add_collection_options,
            custom_headers,
            raw,
            **operation_config)

        # multi-threaded behavior
        if threads:
            if threads < 0:
                raise ValueError("Threads must be positive or 0")

            active_threads = []
            for i in range(threads):
                active_threads.append(threading.Thread(
                    target=task_workflow_manager.task_collection_thread_handler,
                    args=(results_queue,)))
                active_threads[-1].start()
            for thread in active_threads:
                thread.join()
        # single-threaded behavior
        else:
            task_workflow_manager.task_collection_thread_handler(results_queue)

        # Only define error if all threads have finished and there were failures
        if task_workflow_manager.failure_tasks or task_workflow_manager.errors:
            raise CreateTasksErrorException(
                    task_workflow_manager.tasks_to_add,
                    task_workflow_manager.failure_tasks,
                    task_workflow_manager.errors)
        else:
            submitted_tasks = _handle_output(results_queue)
            return TaskAddCollectionResult(value=submitted_tasks)
    bulk_add_collection.metadata = {'url': '/jobs/{jobId}/addtaskcollection'}
    return bulk_add_collection


def batch_error_exception_string(self):
    ret = "Request encountered an exception.\nCode: {}\nMessage: {}\n".format(
        self.error.code,
        self.error.message)
    if self.error.values:
        for error_detail in self.error.values:
            ret += "{}: {}\n".format(error_detail.key, error_detail.value)
    return ret


def patch_client():
    try:
        models = sys.modules['azure.batch.models']
    except KeyError:
        models = importlib.import_module('azure.batch.models')
    setattr(models, 'CreateTasksErrorException', CreateTasksErrorException)
    sys.modules['azure.batch.models'] = models

    operations_modules = importlib.import_module('azure.batch.operations')
    operations_modules.TaskOperations.add_collection = build_new_add_collection(operations_modules.TaskOperations.add_collection)
    models = importlib.import_module('azure.batch.models')
    models.BatchErrorException.__str__ = batch_error_exception_string