# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from azure.core.tracing.decorator import distributed_trace

from ._generated._serialization import Serializer  # pylint:disable=protected-access
from ._generated import AzureCommunicationJobRouterService
from ._generated.models import (
    QueueStatistics,
    WorkerStateSelector,
    JobStateSelector,
    AcceptJobOfferResult,
    JobPositionDetails,
    CancelJobRequest,
    CompleteJobRequest,
    CloseJobRequest,
)
from ._models import (
    RouterWorker,
    RouterWorkerItem,
    RouterJob,
    RouterJobItem,
    DeclineJobOfferResult,
    ReclassifyJobResult,
    CancelJobResult,
    CompleteJobResult,
    CloseJobResult,
)
from ._shared.user_credential import CommunicationTokenCredential
from ._shared.utils import parse_connection_str, get_authentication_policy
from ._version import SDK_MONIKER
from ._utils import _get_value  # pylint:disable=protected-access

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union, Tuple
    from azure.core.paging import ItemPaged

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


class RouterClient(object):  # pylint: disable=client-accepts-api-version-keyword,too-many-public-methods,too-many-lines
    """A client to interact with the AzureCommunicationService JobRouter service.

    This client provides operations to create and update jobs, policies and workers.

    :param str endpoint:
        The endpoint of the Azure Communication resource.
    :param CommunicationTokenCredential credential:
        The credentials with which to authenticate
    """

    def __init__(
            self,
            endpoint,  # type: str
            credential,  # type: CommunicationTokenCredential
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        if not credential:
            raise ValueError("credential can not be None")

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._authentication_policy = get_authentication_policy(endpoint, credential)
        self._client = AzureCommunicationJobRouterService(
            self._endpoint,
            authentication_policy = self._authentication_policy,
            sdk_moniker = SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(cls, conn_str,  # type: str
                               **kwargs  # type: Any
                               ):  # type: (...) -> RouterClient
        """Create RouterClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of RouterClient.
        :rtype: ~azure.communication.jobrouter.RouterClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_authentication.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Authenticating a RouterClient from a connection_string
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    # region Queue

    @distributed_trace
    def get_queue_statistics(
            self,
            queue_id,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> QueueStatistics
        """Retrieves a queue's statistics.

        :param str queue_id: Id of the queue.

        :return QueueStatistics
        :rtype ~azure.communication.jobrouter.QueueStatistics
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        return self._client.job_router.get_queue_statistics(
            id = queue_id,
            **kwargs
        )

    # endregion Queue

    # region Worker

    @distributed_trace
    def create_worker(
            self,
            worker_id,  # type: str
            total_capacity,  # type: int
            **kwargs  # type: Any
    ):
        #  type: (...) -> RouterWorker
        """Create a new worker.

        :param str worker_id: Id of the worker.

        :param int total_capacity: The total capacity score this worker has to manage multiple concurrent
            jobs.

        :keyword queue_assignments: The queue(s) that this worker can receive work from.
        :paramtype queue_assignments: Optional[dict[str, ~azure.communication.jobrouter.QueueAssignment]]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
            engines to make decisions.
        :paramtype labels: Optional[dict[str, Union[int, float, str, bool]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this worker.
        :paramtype tags: Optional[dict[str, Union[int, float, str, bool]]]

        :keyword channel_configurations: The channel(s) this worker can handle and their impact on the
            capacity of the worker.
        :paramtype channel_configurations: Optional[dict[str, ~azure.communication.jobrouter.ChannelConfiguration]]

        :keyword available_for_offers: A flag indicating whether the worker is open to receive offers or not.
        :paramtype available_for_offers: Optional[bool]

        :return RouterWorker
        :rtype ~azure.communication.jobrouter.RouterWorker
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        if not total_capacity:
            raise ValueError("total_capacity cannot be None")

        router_worker = RouterWorker(
            queue_assignments = kwargs.pop('queue_assignments', None),
            total_capacity = total_capacity,
            labels = kwargs.pop('labels', None),
            tags = kwargs.pop('tags', None),
            channel_configurations = kwargs.pop('channel_configurations', None),
            available_for_offers = kwargs.pop('available_for_offers', None)
        )

        return self._client.job_router.upsert_worker(
            worker_id = worker_id,
            patch = router_worker._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterWorker._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def update_worker(
            self,
            worker_id,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> RouterWorker
        """Update a router worker.

        :param str worker_id: Id of the worker.

        :keyword queue_assignments: The queue(s) that this worker can receive work from.
        :paramtype queue_assignments: Optional[dict[str, ~azure.communication.jobrouter.QueueAssignment]]

        :keyword total_capacity: The total capacity score this worker has to manage multiple concurrent
         jobs.
        :paramtype total_capacity: Optional[int]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[dict[str, Union[int, float, str, bool]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this worker.
        :paramtype tags: Optional[dict[str, Union[int, float, str, bool]]]

        :keyword channel_configurations: The channel(s) this worker can handle and their impact on the
         workers capacity.
        :paramtype channel_configurations: Optional[dict[str, ~azure.communication.jobrouter.ChannelConfiguration]]

        :keyword available_for_offers: A flag indicating this worker is open to receive offers or not.
        :paramtype available_for_offers: Optional[bool]

        :keyword router_worker: An instance of RouterWorker. Properties defined in
            class instance will not be considered if they are also specified in keyword arguments.
        :paramtype router_worker: Optional[~azure.communication.jobrouter.RouterWorker]

        :return RouterWorker
        :rtype ~azure.communication.jobrouter.RouterWorker
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        router_worker = kwargs.pop("router_worker", None)

        # pylint:disable=protected-access
        queue_assignments = _get_value(
            kwargs.pop('queue_assignments', None),
            getattr(router_worker, 'queue_assignments', None)
        )

        # pylint:disable=protected-access
        total_capacity = _get_value(
            kwargs.pop('total_capacity', None),
            getattr(router_worker, 'total_capacity', None)
        )

        # pylint:disable=protected-access
        labels = _get_value(
            kwargs.pop('labels', None),
            getattr(router_worker, 'labels', None)
        )

        # pylint:disable=protected-access
        tags = _get_value(
            kwargs.pop('tags', None),
            getattr(router_worker, 'tags', None)
        )

        # pylint:disable=protected-access
        channel_configurations = _get_value(
            kwargs.pop('channel_configurations', None),
            getattr(router_worker, 'channel_configurations', None)
        )

        # pylint:disable=protected-access
        available_for_offers = _get_value(
            kwargs.pop('available_for_offers', None),
            getattr(router_worker, 'available_for_offers', None)
        )

        patch = RouterWorker(
            queue_assignments = queue_assignments,
            total_capacity = total_capacity,
            labels = labels,
            tags = tags,
            channel_configurations = channel_configurations,
            available_for_offers = available_for_offers
        )

        return self._client.job_router.upsert_worker(
            worker_id = worker_id,
            patch = patch._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterWorker._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def get_worker(
            self,
            worker_id,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> RouterWorker
        """Retrieves an existing worker by Id.

        :param str worker_id: Id of the worker.

        :return RouterWorker
        :rtype ~azure.communication.jobrouter.RouterWorker
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not worker_id:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.get_worker(
            worker_id = worker_id,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterWorker._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def list_workers(
            self,
            **kwargs  # type: Any
    ):
        #  type: (...) -> ItemPaged[RouterWorkerItem]
        """Retrieves existing workers.

        :keyword status: If specified, select workers by worker status. Default value is "all".
          Accepted value(s): active, draining, inactive, all
        :paramtype status: Optional[Union[str, ~azure.communication.jobrouter.WorkerStateSelector]]

        :keyword channel_id: If specified, select workers who have a channel configuration
           with this channel. Default value is None.
        :paramtype channel_id: Optional[str]

        :keyword queue_id: If specified, select workers who are assigned to this queue.
           Default value is None.
        :paramtype queue_id: Optional[str]

        :keyword has_capacity: If set to true, select only workers who have capacity for the
           channel specified by ``channelId`` or for any channel
        :paramtype has_capacity: Optional[bool]

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of RouterWorkerItem
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.RouterWorkerItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        status = kwargs.pop('status', None)
        if status is None:
            status = WorkerStateSelector.ALL
        elif not isinstance(status, WorkerStateSelector):
            try:
                status = WorkerStateSelector.__getattr__(status)
            except Exception:
                raise ValueError(f"status: {status} is not acceptable")

        channel_id = kwargs.pop('channel_id', None)
        queue_id = kwargs.pop('queue_id', None)
        has_capacity = kwargs.pop('has_capacity', None)

        return self._client.job_router.list_workers(
            params = params,
            status = status,
            channel_id = channel_id,
            queue_id = queue_id,
            has_capacity = has_capacity,
            # pylint:disable=protected-access
            cls = lambda objs: [RouterWorkerItem._from_generated(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def delete_worker(
            self,
            worker_id,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete a worker by Id.

        :param str worker_id: Id of the worker to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        return self._client.job_router.delete_worker(
            worker_id = worker_id,
            **kwargs
        )
    # endregion Worker

    # region Job

    @distributed_trace
    def create_job(
            self,
            job_id,  # type: str
            channel_id,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> RouterJob
        """Create a job.

        :param str job_id: Id of the job.

        :param str channel_id: The channel identifier. eg. voice, chat, etc.

        :keyword channel_reference: Reference to an external parent context, eg. call ID.
        :paramtype channel_reference: Optional[str]

        :keyword classification_policy_id: The Id of the Classification policy used for classifying a
         job.
        :paramtype classification_policy_id: Optional[str]

        :keyword queue_id: The Id of the Queue that this job is queued to.
        :paramtype queue_id: Optional[str]

        :keyword priority: The priority of this job.
        :paramtype priority: Optional[int]

        :keyword requested_worker_selectors: A collection of manually specified label selectors, which
         a worker must satisfy in order to process this job.
        :paramtype requested_worker_selectors: Optional[List[~azure.communication.jobrouter.WorkerSelector]]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this job.
        :paramtype tags: Optional[Dict[str, Union[int, float, str, bool]]]

        :keyword notes: Notes attached to a job, sorted by timestamp.
        :paramtype notes: Optional[Dict[~datetime.datetime, str]]


        :return RouterJob
        :rtype ~azure.communication.jobrouter.RouterJob
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        if not channel_id:
            raise ValueError("channel_id cannot be None")

        router_job = RouterJob(
            channel_reference = kwargs.pop('channel_reference', None),
            channel_id = channel_id,
            classification_policy_id = kwargs.pop('classification_policy_id', None),
            queue_id = kwargs.pop('queue_id', None),
            priority = kwargs.pop('priority', None),
            requested_worker_selectors = kwargs.pop('requested_worker_selectors', None),
            labels = kwargs.pop('labels', None),
            tags = kwargs.pop('tags', None),
            notes = kwargs.pop('notes', None)
        )

        return self._client.job_router.upsert_job(
            id = job_id,
            patch = router_job._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterJob._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def update_job(
            self,
            job_id,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> RouterJob
        """Update a job.

        :param str job_id: Id of the job.

        :keyword router_job: An instance of RouterJob. Properties defined in
          class instance will not be considered if they are also specified in keyword arguments.
        :paramtype router_job: Optional[~azure.communication.jobrouter.RouterJob]

        :keyword channel_reference: Reference to an external parent context, eg. call ID.
        :paramtype channel_reference: Optional[str]

        :keyword channel_id: The channel identifier. eg. voice, chat, etc.
        :paramtype channel_id: Optional[str]

        :keyword classification_policy_id: The Id of the Classification policy used for classifying a
         job.
        :paramtype classification_policy_id: Optional[str]

        :keyword queue_id: The Id of the Queue that this job is queued to.
        :paramtype queue_id: Optional[str]

        :keyword priority: The priority of this job.
        :paramtype priority: Optional[int]

        :keyword disposition_code: Reason code for cancelled or closed jobs.
        :paramtype disposition_code: Optional[str]

        :keyword requested_worker_selectors: A collection of manually specified label selectors, which
         a worker must satisfy in order to process this job.
        :paramtype requested_worker_selectors: Optional[List[~azure.communication.jobrouter.WorkerSelector]]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this job.
        :paramtype tags: Optional[Dict[str, Union[int, float, str, bool]]]

        :keyword notes: Notes attached to a job, sorted by timestamp.
        :paramtype notes: Optional[Dict[~datetime.datetime, str]]


        :return RouterJob
        :rtype ~azure.communication.jobrouter.RouterJob
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        router_job = kwargs.pop("router_job", None)

        # pylint:disable=protected-access
        channel_reference = _get_value(
            kwargs.pop('channel_reference', None),
            getattr(router_job, 'channel_reference', None)
        )

        # pylint:disable=protected-access
        channel_id = _get_value(
            kwargs.pop('channel_id', None),
            getattr(router_job, 'channel_id', None)
        )

        # pylint:disable=protected-access
        classification_policy_id = _get_value(
            kwargs.pop('classification_policy_id', None),
            getattr(router_job, 'classification_policy_id', None)
        )

        # pylint:disable=protected-access
        queue_id = _get_value(
            kwargs.pop('queue_id', None),
            getattr(router_job, 'queue_id', None)
        )

        # pylint:disable=protected-access
        priority = _get_value(
            kwargs.pop('priority', None),
            getattr(router_job, 'priority', None)
        )

        # pylint:disable=protected-access
        disposition_code = _get_value(
            kwargs.pop('disposition_code', None),
            getattr(router_job, 'disposition_code', None)
        )

        # pylint:disable=protected-access
        requested_worker_selectors = _get_value(
            kwargs.pop('requested_worker_selectors', None),
            getattr(router_job, 'requested_worker_selectors', None)
        )

        # pylint:disable=protected-access
        labels = _get_value(
            kwargs.pop('labels', None),
            getattr(router_job, 'labels', None)
        )

        # pylint:disable=protected-access
        tags = _get_value(
            kwargs.pop('tags', None),
            getattr(router_job, 'tags', None)
        )

        # pylint:disable=protected-access
        notes = _get_value(
            kwargs.pop('notes', None),
            getattr(router_job, 'notes', None)
        )

        patch = RouterJob(
            channel_reference = channel_reference,
            channel_id = channel_id,
            classification_policy_id = classification_policy_id,
            queue_id = queue_id,
            priority = priority,
            disposition_code = disposition_code,
            requested_worker_selectors = requested_worker_selectors,
            labels = labels,
            tags = tags,
            notes = notes
        )

        return self._client.job_router.upsert_job(
            id = job_id,
            patch = patch._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterJob._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def get_job(
            self,
            job_id,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> RouterJob
        """Retrieves an existing worker by Id.

        :param str job_id: Id of the job.

        :return RouterJob
        :rtype ~azure.communication.jobrouter.RouterJob
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        return self._client.job_router.get_job(
            id = job_id,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterJob._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def list_jobs(
            self,
            **kwargs  # type: Any
    ):
        #  type: (...) -> ItemPaged[RouterJobItem]
        """Retrieves list of jobs based on filter parameters.

        :keyword status: If specified, filter jobs by status. Default value is "all".
            Accepted value(s): pendingClassification, queued, assigned, completed, closed, cancelled,
            classificationFailed, active, all
        :paramtype status: Optional[Union[str, ~azure.communication.jobrouter.JobStateSelector]]

        :keyword channel_id: If specified, filter jobs by channel. Default value is None.
        :paramtype channel_id: Optional[str]

        :keyword queue_id: If specified, filter jobs by queue. Default value is None.
        :paramtype queue_id: Optional[str]

        :keyword classification_policy_id: If specified, filter jobs by classificationPolicy. Default value is None.
        :paramtype classification_policy_id: Optional[str]

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of RouterJobItem
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.RouterJobItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        status = kwargs.pop('status', None)
        if status is None:
            status = JobStateSelector.ALL
        elif not isinstance(status, JobStateSelector):
            try:
                status = JobStateSelector.__getattr__(status)
            except Exception:
                raise ValueError(f"status: {status} is not acceptable")

        channel_id = kwargs.pop('channel_id', None)
        queue_id = kwargs.pop('queue_id', None)
        classification_policy_id = kwargs.pop('classification_policy_id', None)

        return self._client.job_router.list_jobs(
            params = params,
            status = status,
            channel_id = channel_id,
            queue_id = queue_id,
            classification_policy_id = classification_policy_id,
            # pylint:disable=protected-access
            cls = lambda objs: [RouterJobItem._from_generated(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def delete_job(
            self,
            job_id,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete a job by Id.

        :param str job_id: Id of the job to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not job_id:
            raise ValueError("job_id cannot be None.")

        return self._client.job_router.delete_job(
            id = job_id,
            **kwargs
        )

    @distributed_trace
    def get_queue_position(
            self,
            job_id,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> JobPositionDetails
        """Gets a job's position details.

        :param str job_id: Id of the job.

        :return: JobPositionDetails
        :rtype: ~azure.communication.jobrouter.JobPositionDetails
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        return self._client.job_router.get_in_queue_position(
            id = job_id,
            **kwargs
        )

    @distributed_trace
    def close_job(
            self,
            job_id,  # type: str
            assignment_id,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> CloseJobResult
        """Closes a completed job.

        :param str job_id: Id of the job.

        :param str assignment_id: The assignment within which the job is to be closed.

        :keyword disposition_code: Indicates the outcome of the job, populate this field with your own
         custom values. Default value is None.
        :paramtype disposition_code: Optional[str]

        :keyword close_time: If not provided, worker capacity is released immediately along with a
         JobClosedEvent notification. If provided, worker capacity is released along with a JobClosedEvent notification
         at a future time. Default value is None.
        :paramtype close_time: Optional[~datetime.datetime]

        :keyword note: (Optional) A note that will be appended to the jobs' Notes collection with the
         current timestamp. Default value is None.
        :paramtype note: Optional[str]

        :return: CloseJobResult
        :rtype: ~azure.communication.jobrouter.CloseJobResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        if not assignment_id:
            raise ValueError("assignment_id cannot be None.")

        disposition_code = kwargs.pop('disposition_code', None)
        close_time = kwargs.pop('close_time', None)
        note = kwargs.pop('note', None)

        close_job_request = CloseJobRequest(
            assignment_id = assignment_id,
            disposition_code = disposition_code,
            close_time = close_time,
            note = note
        )

        return self._client.job_router.close_job_action(
            id = job_id,
            close_job_request = close_job_request,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: CloseJobResult(deserialized_response),
            **kwargs
        )

    @distributed_trace
    def complete_job(
            self,
            job_id,  # type: str
            assignment_id,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> CompleteJobResult
        """Completes an assigned job.

        :param str job_id: Id of the job.

        :param str assignment_id: The assignment within the job to complete.

        :keyword note: (Optional) A note that will be appended to the jobs' Notes collection with th
         current timestamp. Default value is None.
        :paramtype note: Optional[str]

        :return: CompleteJobResult
        :rtype: ~azure.communication.jobrouter.CompleteJobResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        if not assignment_id:
            raise ValueError("assignment_id cannot be None.")

        note = kwargs.pop('note', None)

        complete_job_request = CompleteJobRequest(
            assignment_id = assignment_id,
            note = note
        )

        return self._client.job_router.complete_job_action(
            id = job_id,
            complete_job_request = complete_job_request,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: CompleteJobResult(deserialized_response),
            **kwargs
        )

    @distributed_trace
    def cancel_job(
            self,
            job_id,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> CancelJobResult
        """Submits request to cancel an existing job by Id while supplying free-form cancellation reason.

        :param str job_id: Id of the job.

        :keyword note: A note that will be appended to the jobs' Notes collection with the
         current timestamp. Default value is None.
        :paramtype note: Optional[str]

        :keyword disposition_code: Indicates the outcome of the job, populate this field with your own
         custom values.
         If not provided, default value of "Cancelled" is set. Default value is None.
        :paramtype disposition_code: Optional[str]

        :return: CancelJobResult
        :rtype: ~azure.communication.jobrouter.CancelJobResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not job_id:
            raise ValueError("job_id cannot be None.")

        note = kwargs.pop('note', None)
        disposition_code = kwargs.pop('disposition_code', None)

        cancel_job_request = CancelJobRequest(
            note = note,
            disposition_code = disposition_code
        )

        return self._client.job_router.cancel_job_action(
            id = job_id,
            cancel_job_request = cancel_job_request,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: CancelJobResult(deserialized_response),
            **kwargs
        )

    @distributed_trace
    def reclassify_job(
            self,
            job_id,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> ReclassifyJobResult
        """Reclassify a job.

        :param str job_id: Id of the job.

        :return: ReclassifyJobResult
        :rtype: ~azure.communication.jobrouter.ReclassifyJobResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not job_id:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.reclassify_job_action(
            id = job_id,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: ReclassifyJobResult(deserialized_response),
            **kwargs
        )

    # endregion Job

    # region Offer

    @distributed_trace
    def accept_job_offer(
            self,
            worker_id,  # type: str
            offer_id,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> AcceptJobOfferResult
        """Accepts an offer to work on a job and returns a 409/Conflict if another agent accepted the job
        already.

        :param worker_id: Id of the worker.
        :type worker_id: str
        :param offer_id: Id of the offer.
        :type offer_id: str

        :return: AcceptJobOfferResponse
        :rtype: ~azure.communication.jobrouter.AcceptJobOfferResponse
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        if not offer_id:
            raise ValueError("offer_id cannot be None.")

        return self._client.job_router.accept_job_action(
            worker_id = worker_id,
            offer_id = offer_id,
            **kwargs
        )

    @distributed_trace
    def decline_job_offer(
            self,
            worker_id,  # type: str
            offer_id,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> DeclineJobOfferResult
        """Declines an offer to work on a job.

        :param worker_id: Id of the worker.
        :type worker_id: str
        :param offer_id: Id of the offer.
        :type offer_id: str

        :return: DeclineJobOfferResult
        :rtype: ~azure.communication.jobrouter.DeclineJobOfferResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        if not offer_id:
            raise ValueError("offer_id cannot be None.")

        return self._client.job_router.decline_job_action(
            worker_id = worker_id,
            offer_id = offer_id,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: DeclineJobOfferResult(deserialized_response),
            **kwargs
        )

    # endregion Offer

    def close(self):
        # type: () -> None
        self._client.close()

    def __enter__(self):
        # type: () -> RouterClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
