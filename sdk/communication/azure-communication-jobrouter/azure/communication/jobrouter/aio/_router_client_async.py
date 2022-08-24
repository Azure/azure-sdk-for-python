# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports
from typing import Any
from urllib.parse import urlparse

from azure.core.async_paging import AsyncItemPaged
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .._generated._serialization import Serializer  # pylint:disable=protected-access
from .._generated.aio import AzureCommunicationJobRouterService
from .._generated.models import (
    QueueStatistics,
    WorkerStateSelector,
    JobStateSelector,
    AcceptJobOfferResult,
    JobPositionDetails,
    CancelJobRequest,
    CompleteJobRequest,
    CloseJobRequest,
)
from .._models import (
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
from .._shared.user_credential_async import CommunicationTokenCredential
from .._shared.utils import parse_connection_str, get_authentication_policy
from .._utils import _get_value
from .._version import SDK_MONIKER

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
            endpoint: str,
            credential: CommunicationTokenCredential,
            **kwargs: Any
    ) -> None:
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
            authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(
            cls,
            conn_str: str,
            **kwargs: Any
    ) -> "RouterClient":
        # type: (...) -> RouterClient
        """Create RouterClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of RouterClient.
        :rtype: ~azure.communication.jobrouter.aio.RouterClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_authentication_async.py
                :start-after: [START auth_from_connection_string_async]
                :end-before: [END auth_from_connection_string_async]
                :language: python
                :dedent: 8
                :caption: Authenticating a RouterClient from a connection_string
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    # region QueueAio

    @distributed_trace_async
    async def get_queue_statistics(
            self,
            queue_id: str,
            **kwargs: Any
    ) -> QueueStatistics:
        #  type: (...) -> QueueStatistics
        """Retrieves a queue's statistics.

        :param str queue_id: Id of the queue.

        :return QueueStatistics
        :rtype ~azure.communication.jobrouter.QueueStatistics
        :raises ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops_async.py
                :start-after: [START get_queue_statistics_async]
                :end-before: [END get_queue_statistics_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to fetch queue statistics
        """
        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        return await self._client.job_router.get_queue_statistics(
            id = queue_id,
            **kwargs
        )

    # endregion QueueAio

    # region WorkerAio

    @distributed_trace_async
    async def create_worker(
            self,
            worker_id: str,
            total_capacity: int,
            **kwargs: Any
    ) -> RouterWorker:
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops_async.py
                :start-after: [START create_worker_async]
                :end-before: [END create_worker_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to create a worker
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

        return await self._client.job_router.upsert_worker(
            worker_id = worker_id,
            patch = router_worker._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterWorker._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace_async
    async def update_worker(
            self,
            worker_id: str,
            **kwargs: Any
    ) -> RouterWorker:
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops_async.py
                :start-after: [START update_worker_async]
                :end-before: [END update_worker_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to update a worker

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops_async.py
                :start-after: [START register_worker_async]
                :end-before: [END register_worker_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to register a worker

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops_async.py
                :start-after: [START deregister_worker_async]
                :end-before: [END deregister_worker_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to de-register a worker
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

        return await self._client.job_router.upsert_worker(
            worker_id = worker_id,
            patch = patch._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterWorker._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace_async
    async def get_worker(
            self,
            worker_id: str,
            **kwargs: Any
    ) -> RouterWorker:
        #  type: (...) -> RouterWorker
        """Retrieves an existing worker by Id.

        :param str worker_id: Id of the worker.

        :return RouterWorker
        :rtype ~azure.communication.jobrouter.RouterWorker
        :raises ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops_async.py
                :start-after: [START get_worker_async]
                :end-before: [END get_worker_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to get a worker
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        return await self._client.job_router.get_worker(
            worker_id = worker_id,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterWorker._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def list_workers(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[RouterWorkerItem]:
        #  type: (...) -> AsyncItemPaged[RouterWorkerItem]
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

        :return: An iterator like instance of PagedWorker
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.PagedWorker]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops_async.py
                :start-after: [START list_workers_async]
                :end-before: [END list_workers_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to retrieve workers
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

    @distributed_trace_async
    async def delete_worker(
            self,
            worker_id,  # type: str
            **kwargs  # type: Any
    ) -> None:
        # type: (...) -> None
        """Delete a worker by Id.

        :param str worker_id: Id of the worker to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops_async.py
                :start-after: [START delete_worker_async]
                :end-before: [END delete_worker_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to delete an existing worker
        """

        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        return await self._client.job_router.delete_worker(
            worker_id = worker_id,
            **kwargs
        )

    # endregion WorkerAio

    # region JobAio

    @distributed_trace_async
    async def create_job(
            self,
            job_id: str,
            channel_id: str,
            **kwargs: Any
    ) -> RouterJob:
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START create_job_async]
                :end-before: [END create_job_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to create a job
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

        return await self._client.job_router.upsert_job(
            id = job_id,
            patch = router_job._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterJob._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace_async
    async def update_job(
            self,
            job_id: str,
            **kwargs: Any
    ) -> RouterJob:
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START update_job_async]
                :end-before: [END update_job_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to update a job
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

        return await self._client.job_router.upsert_job(
            id = job_id,
            patch = patch._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterJob._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace_async
    async def get_job(
            self,
            job_id: str,
            **kwargs: Any
    ) -> RouterJob:
        #  type: (...) -> RouterJob
        """Retrieves an existing worker by Id.

        :param str job_id: Id of the job.

        :return RouterJob
        :rtype ~azure.communication.jobrouter.RouterJob
        :raises ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START get_job_async]
                :end-before: [END get_job_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to get a job
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        return await self._client.job_router.get_job(
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
    ) -> AsyncItemPaged[RouterJobItem]:
        #  type: (...) -> AsyncItemPaged[RouterJobItem]
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
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.RouterJobItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START list_jobs_async]
                :end-before: [END list_jobs_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to retrieve jobs
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

    @distributed_trace_async
    async def delete_job(
            self,
            job_id: str,
            **kwargs: Any
    ) -> None:
        # type: (...) -> None
        """Delete a job by Id.

        :param str job_id: Id of the job to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START delete_job_async]
                :end-before: [END delete_job_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to delete a job
        """

        if not job_id:
            raise ValueError("identifier cannot be None.")

        return await self._client.job_router.delete_job(
            id = job_id,
            **kwargs
        )

    @distributed_trace_async
    async def get_queue_position(
            self,
            job_id: str,
            **kwargs: Any
    ) -> JobPositionDetails:
        #  type: (...) -> JobPositionDetails
        """Gets a job's position details.

        :param str job_id: Id of the job.

        :return: JobPositionDetails
        :rtype: ~azure.communication.jobrouter.JobPositionDetails
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START get_job_position_async]
                :end-before: [END get_job_position_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to get a job position in queue
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        return await self._client.job_router.get_in_queue_position(
            id = job_id,
            **kwargs
        )

    @distributed_trace_async
    async def close_job(
            self,
            job_id: str,
            assignment_id: str,
            **kwargs: Any
    ) -> CloseJobResult:
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START close_job_async]
                :end-before: [END close_job_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to close a job
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

        return await self._client.job_router.close_job_action(
            id = job_id,
            close_job_request = close_job_request,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: CloseJobResult(deserialized_response),
            **kwargs
        )

    @distributed_trace_async
    async def complete_job(
            self,
            job_id: str,
            assignment_id: str,
            **kwargs: Any
    ) -> CompleteJobResult:
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START complete_job_async]
                :end-before: [END complete_job_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to complete a job
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

        return await self._client.job_router.complete_job_action(
            id = job_id,
            complete_job_request = complete_job_request,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: CompleteJobResult(deserialized_response),
            **kwargs
        )

    @distributed_trace_async
    async def cancel_job(
            self,
            job_id: str,
            **kwargs: Any
    ) -> CancelJobResult:
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START cancel_job_async]
                :end-before: [END cancel_job_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to cancel a job
        """

        if not job_id:
            raise ValueError("job_id cannot be None.")

        note = kwargs.pop('note', None)
        disposition_code = kwargs.pop('disposition_code', None)

        cancel_job_request = CancelJobRequest(
            note = note,
            disposition_code = disposition_code
        )

        return await self._client.job_router.cancel_job_action(
            id = job_id,
            cancel_job_request = cancel_job_request,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: CancelJobResult(deserialized_response),
            **kwargs
        )

    @distributed_trace_async
    async def reclassify_job(
            self,
            job_id: str,
            **kwargs: Any
    ) -> ReclassifyJobResult:
        #  type: (...) -> ReclassifyJobResult
        """Reclassify a job.

        :param str job_id: Id of the job.

        :return: ReclassifyJobResult
        :rtype: ~azure.communication.jobrouter.ReclassifyJobResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START reclassify_job_async]
                :end-before: [END reclassify_job_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to re-classify a job
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        return await self._client.job_router.reclassify_job_action(
            id = job_id,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: ReclassifyJobResult(deserialized_response),
            **kwargs
        )

    # endregion JobAio

    # region OfferAio

    @distributed_trace_async
    async def accept_job_offer(
            self,
            worker_id: str,
            offer_id: str,
            **kwargs: Any
    ) -> AcceptJobOfferResult:
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

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START accept_job_offer_async]
                :end-before: [END accept_job_offer_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to accept a job offer
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        if not offer_id:
            raise ValueError("offer_id cannot be None.")

        return await self._client.job_router.accept_job_action(
            worker_id = worker_id,
            offer_id = offer_id,
            **kwargs
        )

    @distributed_trace_async
    async def decline_job_offer(
            self,
            worker_id: str,
            offer_id: str,
            **kwargs: Any
    ) -> DeclineJobOfferResult:
        #  type: (...) -> DeclineJobOfferResult
        """Declines an offer to work on a job.

        :param worker_id: Id of the worker.
        :type worker_id: str
        :param offer_id: Id of the offer.
        :type offer_id: str

        :return: DeclineJobOfferResult
        :rtype: ~azure.communication.jobrouter.DeclineJobOfferResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START decline_job_offer_async]
                :end-before: [END decline_job_offer_async]
                :language: python
                :dedent: 8
                :caption: Use a RouterClient to decline a job offer
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        if not offer_id:
            raise ValueError("offer_id cannot be None.")

        return await self._client.job_router.decline_job_action(
            worker_id = worker_id,
            offer_id = offer_id,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: DeclineJobOfferResult(deserialized_response),
            **kwargs
        )

    # endregion OfferAio

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "RouterClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)
