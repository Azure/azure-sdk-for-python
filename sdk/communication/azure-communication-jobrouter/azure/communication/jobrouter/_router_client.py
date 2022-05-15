# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING
from urllib.parse import urlparse

from azure.core.tracing.decorator import distributed_trace

from ._generated import AzureCommunicationJobRouterService
from ._generated.models import (
    ClassificationPolicy,
    DistributionPolicy,
    ExceptionPolicy,
    QueueStatistics,
    WorkerStateSelector,
    JobStateSelector,
    AcceptJobOfferResponse,
    JobPositionDetails
)
from ._models import (
    LabelCollection,
    JobQueue,
    RouterWorker,
    PagedWorker,
    PagedQueue,
    RouterJob,
    PagedJob,
    DeclineJobOfferResponse,
    ReclassifyJobResponse,
    CancelJobResponse,
    CompleteJobResponse,
    CloseJobResponse,
)
from ._shared.user_credential import CommunicationTokenCredential
from ._shared.utils import parse_connection_str, get_authentication_policy
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.paging import ItemPaged


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
        :rtype: ~azure.communication.RouterClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    # region ExceptionPolicy

    @distributed_trace
    def upsert_exception_policy(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> ExceptionPolicy
        """Create or update a new exception policy.

        :param str identifier: Id of the exception policy.

        :keyword exception_rules: (Optional) A dictionary collection of exception rules on the exception
        policy. Key is the Id of each exception rule.
        :paramtype exception_rules:
                Dict[str, ~azure.communication.jobrouter.models.ExceptionRule]

        :keyword str name: The name of this policy.

        :keyword exception_policy: An instance of exception policy
        :paramtype exception_policy: ~azure.communication.jobrouter.ExceptionPolicy

        :return ExceptionPolicy
        :rtype ~azure.communication.jobrouter.ExceptionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        exception_policy = kwargs.pop("exception_policy", None)

        if not exception_policy:
            exception_rules = kwargs.pop("exception_rules", None)
            if not exception_rules or any(exception_rules) is False:
                raise ValueError("exception_rules cannot be None or empty.")

            exception_policy = ExceptionPolicy(
                name = kwargs.pop('name', None),
                exception_rules = exception_rules
            )

        return self._client.job_router.upsert_exception_policy(
            id = identifier,
            patch = exception_policy,
            **kwargs
        )

    @distributed_trace
    def get_exception_policy(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> ExceptionPolicy
        """Retrieves an existing distribution policy by Id.

        :param str identifier: Id of the policy.

        :return DistributionPolicy
        :rtype ~azure.communication.jobrouter.ExceptionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.get_exception_policy(
            id = identifier,
            **kwargs
        )

    @distributed_trace
    def list_exception_policies(
            self,
            **kwargs  # type: Any
    ):
        #  type: (...) -> ItemPaged[ExceptionPolicy]
        """Retrieves existing exception policies.

        :keyword int results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of ExceptionPolicy
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.ExceptionPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        return self._client.job_router.list_exception_policies(
            maxpagesize = results_per_page,
            **kwargs
        )

    @distributed_trace
    def delete_exception_policy(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete an exception policy by Id.

        :param str identifier: Id of the policy to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.delete_exception_policy(
            id = identifier,
            **kwargs
        )

    # endregion ExceptionPolicy

    # region DistributionPolicy

    @distributed_trace
    def upsert_distribution_policy(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> DistributionPolicy
        """Create or update a new distribution policy.

        :param str identifier: Id of the distribution policy.
        :keyword float offer_ttl_seconds: The expiry time of any offers created under this policy will
        be governed by the offer time to live.

        :keyword mode: Specified distribution mode
        :type mode: Union[~azure.communication.jobrouter.BestWorkerMode, ~azure.communication.jobrouter.LongestIdleMode,
        ~azure.communication.jobrouter.RoundRobinMode]

        :keyword str name: The name of this policy.

        :keyword DistributionPolicy distribution_policy: An instance of distribution policy

        :return DistributionPolicy
        :rtype ~azure.communication.jobrouter.DistributionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        distribution_policy = kwargs.pop("distribution_policy", None)

        if not distribution_policy:
            offer_ttl_seconds = kwargs.pop("offer_ttl_seconds", None)
            if not offer_ttl_seconds:
                raise ValueError("offer_ttl_seconds cannot be None.")

            mode = kwargs.pop("mode", None)
            if not mode:
                raise ValueError("mode cannot be None.")

            distribution_policy = DistributionPolicy(
                name = kwargs.pop('name', None),
                offer_ttl_seconds = offer_ttl_seconds,
                mode = mode
            )

        return self._client.job_router.upsert_distribution_policy(
            id = identifier,
            patch = distribution_policy,
            **kwargs
        )

    @distributed_trace
    def get_distribution_policy(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> DistributionPolicy
        """Retrieves an existing distribution policy by Id.

        :param str identifier: Id of the policy.

        :return DistributionPolicy
        :rtype ~azure.communication.jobrouter.DistributionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("id cannot be None.")

        return self._client.job_router.get_distribution_policy(
            id = identifier,
            **kwargs
        )

    @distributed_trace
    def list_distribution_policies(
            self,
            **kwargs  # type: Any
    ):
        #  type: (...) -> ItemPaged[DistributionPolicy]
        """Retrieves existing distribution policies.

        :keyword int results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of DistributionPolicy
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.DistributionPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        return self._client.job_router.list_distribution_policies(
            maxpagesize = results_per_page,
            **kwargs
        )

    @distributed_trace
    def delete_distribution_policy(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete a distribution policy by Id.

        :param str identifier: Id of the policy to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("id cannot be None.")

        return self._client.job_router.delete_distribution_policy(
            id = identifier,
            **kwargs
        )

    # endregion DistributionPolicy

    # region Queue

    @distributed_trace
    def upsert_queue(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> JobQueue
        """Creates or update a job queue

        :param str identifier: Id of the queue.

        :keyword ~azure.communication.jobrouter.JobQueue queue: An instance of JobQueue

        :keyword str distribution_policy_id: The ID of the distribution policy that will determine
        how a job is distributed to workers.

        :keyword str name: The name of this queue.

        :keyword labels: A set of key/value pairs that are
          identifying attributes used by the rules engines to make decisions.
        :paramtype labels: Union[~azure.communication.jobrouter.LabelCollection, Dict[str, Any]]

        :keyword str exception_policy_id: The ID of the exception policy that determines various
        job escalation rules.

        :return JobQueue
        :rtype ~azure.communication.jobrouter.JobQueue
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        queue = kwargs.pop('queue', None)
        if not queue:
            distribution_policy_id = kwargs.pop('distribution_policy_id', None)
            if not distribution_policy_id:
                raise ValueError("distribution_policy_id cannot be None.")

            queue_labels = kwargs.pop('labels', None)
            if not queue_labels:
                queue_labels = LabelCollection(queue_labels)

            queue = JobQueue(
                name = kwargs.pop('name', None),
                distribution_policy_id = distribution_policy_id,
                labels = queue_labels,
                exception_policy_id = kwargs.pop('exception_policy_id', None)
            )

        return self._client.job_router.upsert_queue(
            id = identifier,
            patch = queue._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: JobQueue._from_generated(deserialized_response),
            **kwargs)

    @distributed_trace
    def get_queue(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> JobQueue
        """Retrieves an existing queue by Id.

        :param str identifier: Id of the queue.

        :return JobQueue
        :rtype ~azure.communication.jobrouter.JobQueue
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("id cannot be None.")

        return self._client.job_router.get_queue(
            id = identifier,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: JobQueue._from_generated(deserialized_response),
            **kwargs
        )

    @distributed_trace
    def get_queue_statistics(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> QueueStatistics
        """Retrieves a queue's statistics.

        :param str identifier: Id of the queue.

        :return QueueStatistics
        :rtype ~azure.communication.jobrouter.QueueStatistics
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.get_queue_statistics(
            id = identifier,
            **kwargs
        )

    @distributed_trace
    def list_queues(
            self,
            **kwargs  # type: Any
    ):
        #  type: (...) -> ItemPaged[PagedQueue]
        """Retrieves existing queues.

        :keyword int results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of PagedQueue
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.PagedQueue]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        return self._client.job_router.list_queues(
            maxpagesize = results_per_page,
            cls = lambda objs: [PagedQueue._from_generated(x) for x in objs],  # pylint:disable=protected-access
            **kwargs
        )

    @distributed_trace
    def delete_queue(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes a queue by Id.

        :param str identifier: Id of the queue to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("id cannot be None.")

        return self._client.job_router.delete_queue(
            id = identifier,
            **kwargs
        )

    # endregion Queue

    # region ClassificationPolicy

    @distributed_trace
    def upsert_classification_policy(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> ClassificationPolicy
        """ Create or update a classification policy

        :param str identifier: Id of the classification policy.

        :keyword ~azure.communication.jobrouter.ClassificationPolicy classification_policy:
            An instance of Classification policy

        :keyword str name: Friendly name of this policy.

        :keyword str fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.

        :keyword queue_selectors: The queue selectors
        to resolve a queue for a given job.
        :paramtype queue_selectors: List[Union[
                ~azure.communication.jobrouter.StaticQueueSelector,
                ~azure.communication.jobrouter.ConditionalQueueSelector,
                ~azure.communication.jobrouter.RuleEngineQueueSelector,
                ~azure.communication.jobrouter.PassThroughQueueSelector,
                ~azure.communication.jobrouter.WeightedAllocationQueueSelector
            ]]

        :keyword prioritization_rule: The rule to determine a priority score for a given job.
        :paramtype prioritization_rule: Union[
                ~azure.communication.jobrouter.StaticRule,
                ~azure.communication.jobrouter.ExpressionRule,
                ~azure.communication.jobrouter.AzureFunctionRule,
            ]

        :keyword worker_selectors: The worker label
        selectors to attach to a given job.
        :paramtype worker_selectors: List[Union[
                ~azure.communication.jobrouter.StaticWorkerSelector,
                ~azure.communication.jobrouter.ConditionalWorkerSelector,
                ~azure.communication.jobrouter.RuleEngineWorkerSelector,
                ~azure.communication.jobrouter.PassThroughWorkerSelector,
                ~azure.communication.jobrouter.WeightedAllocationWorkerSelector
            ]]

        :return ClassificationPolicy
        :rtype ~azure.communication.jobrouter.ClassificationPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        classification_policy = kwargs.pop('classification_policy', None)
        if not classification_policy:
            fallback_queue_id = kwargs.pop("fallback_queue_id", None)
            if not fallback_queue_id:
                raise ValueError("fallback_queue_id cannot be None")

            classification_policy = ClassificationPolicy(
                name = kwargs.pop("name", None),
                fallback_queue_id = fallback_queue_id,
                queue_selectors = kwargs.pop("queue_selectors", None),
                prioritization_rule = kwargs.pop("prioritization_rule", None),
                worker_selectors = kwargs.pop("worker_selectors", None))

        return self._client.job_router.upsert_classification_policy(
            id = identifier,
            patch = classification_policy,
            **kwargs)

    @distributed_trace
    def get_classification_policy(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> ClassificationPolicy
        """Retrieves an existing classification policy by Id.

        :param str identifier: The id of classification policy.
        :return ClassificationPolicy
        :rtype ~azure.communication.jobrouter.ClassificationPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.get_classification_policy(
            identifier,
            **kwargs)

    @distributed_trace
    def list_classification_policies(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[ClassificationPolicy]
        """Retrieves existing classification policies.

        :keyword int results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of ClassificationPolicy
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.ClassificationPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        results_per_page = kwargs.pop("results_per_page", None)

        return self._client.job_router.list_classification_policies(
            maxpagesize = results_per_page,
            **kwargs)

    @distributed_trace
    def delete_classification_policy(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete a classification policy by Id.

        :param str identifier: The id of classification policy.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.delete_classification_policy(
            id = identifier,
            **kwargs)

    # endregion ClassificationPolicy

    # region Worker

    @distributed_trace
    def upsert_worker(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> RouterWorker
        """Create or update a new exception policy.

        :keyword queue_assignments: The queue(s) that this worker can receive work from.
        :paramtype queue_assignments: dict[str, ~azure.communication.jobrouter.QueueAssignment]
        :keyword total_capacity: The total capacity score this worker has to manage multiple concurrent
         jobs.
        :paramtype total_capacity: int
        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Union[~azure.communication.jobrouter.LabelCollection, Dict[str, Any]]
        :keyword tags: A set of tags. A set of non-identifying attributes attached to this worker.
        :paramtype tags: Union[~azure.communication.jobrouter.LabelCollection, Dict[str, Any]]
        :keyword channel_configurations: The channel(s) this worker can handle and their impact on the
         workers capacity.
        :paramtype channel_configurations: dict[str, ~azure.communication.jobrouter.ChannelConfiguration]
        :keyword available_for_offers: A flag indicating this worker is open to receive offers or not.
        :paramtype available_for_offers: bool

        :return RouterWorker
        :rtype ~azure.communication.jobrouter.RouterWorker
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        router_worker = kwargs.pop("router_worker", None)

        if not router_worker:
            total_capacity = kwargs.pop('total_capacity', None)
            if not total_capacity:
                raise ValueError("total_capacity cannot be None")

            labels = kwargs.pop('labels', None)
            if labels is not None:
                labels = LabelCollection(labels)

            tags = kwargs.pop('tags', None)
            if tags is not None:
                tags = LabelCollection(tags)

            router_worker = RouterWorker(
                queue_assignments = kwargs.pop('queue_assignments', None),
                total_capacity = total_capacity,
                labels = labels,
                tags = tags,
                channel_configurations = kwargs.pop('channel_configurations', None),
                available_for_offers = kwargs.pop('available_for_offers', None)
            )

        return self._client.job_router.upsert_worker(
            worker_id = identifier,
            patch = router_worker._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterWorker._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def get_worker(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> RouterWorker
        """Retrieves an existing worker by Id.

        :param str identifier: Id of the worker.

        :return RouterWorker
        :rtype ~azure.communication.jobrouter.RouterWorker
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.get_worker(
            worker_id = identifier,
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
        #  type: (...) -> ItemPaged[PagedWorker]
        """Retrieves existing workers.

        :keyword status: If specified, select workers by worker status. Default value is "all".
        :paramtype status: Union[str, ~azure.communication.jobrouter.WorkerStateSelector]
          Accepted value(s): active, draining, inactive, all

        :keyword channel_id: If specified, select workers who have a channel configuration
         with this channel. Default value is None.
        :paramtype channel_id: str

        :keyword queue_id: If specified, select workers who are assigned to this queue.
         Default value is None.
        :paramtype queue_id: str

        :keyword has_capacity: If set to true, select only workers who have capacity for the
         channel specified by ``channelId`` or for any channel
        :paramtype has_capacity: bool

        :keyword int results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of PagedWorker
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.PagedWorker]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

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
            maxpagesize = results_per_page,
            status = status,
            channel_id = channel_id,
            queue_id = queue_id,
            has_capacity = has_capacity,
            # pylint:disable=protected-access
            cls = lambda objs: [PagedWorker._from_generated(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def delete_worker(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete a worker by Id.

        :param str identifier: Id of the worker to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.delete_worker(
            worker_id = identifier,
            **kwargs
        )
    # endregion Worker

    # region Job

    @distributed_trace
    def upsert_job(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> RouterJob
        """Create or update a job.

        :keyword router_job: An instance of RouterJob
        :paramtype router_job: ~azure.communication.jobrouter.RouterJob

        :keyword channel_reference: Reference to an external parent context, eg. call ID.
        :paramtype channel_reference: str

        :keyword channel_id: The channel identifier. eg. voice, chat, etc.
        :paramtype channel_id: str

        :keyword classification_policy_id: The Id of the Classification policy used for classifying a
         job.
        :paramtype classification_policy_id: str

        :keyword queue_id: The Id of the Queue that this job is queued to.
        :paramtype queue_id: str

        :keyword priority: The priority of this job.
        :paramtype priority: int

        :keyword disposition_code: Reason code for cancelled or closed jobs.
        :paramtype disposition_code: str

        :keyword requested_worker_selectors: A collection of manually specified label selectors, which
         a worker must satisfy in order to process this job.
        :paramtype requested_worker_selectors: List[~azure.communication.jobrouter.WorkerSelector]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: ~azure.communication.jobrouter.LabelCollection

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this job.
        :paramtype tags: ~azure.communication.jobrouter.LabelCollection

        :keyword notes: Notes attached to a job, sorted by timestamp.
        :paramtype notes: Dict[~datetime.datetime, str]


        :return RouterJob
        :rtype ~azure.communication.jobrouter.RouterJob
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        router_job = kwargs.pop("router_job", None)

        if not router_job:
            channel_id = kwargs.pop('channel_id', None)
            if not channel_id:
                raise ValueError("channel_id cannot be None")

            labels = kwargs.pop('labels', None)
            if labels is not None:
                labels = LabelCollection(labels)

            tags = kwargs.pop('tags', None)
            if tags is not None:
                tags = LabelCollection(tags)

            router_job = RouterJob(
                channel_reference = kwargs.pop('channel_reference', None),
                channel_id = channel_id,
                classification_policy_id = kwargs.pop('classification_policy_id', None),
                queue_id = kwargs.pop('queue_id', None),
                priority = kwargs.pop('priority', None),
                disposition_code = kwargs.pop('disposition_code', None),
                requested_worker_selectors = kwargs.pop('requested_worker_selectors', None),
                labels = labels,
                tags = tags,
                notes = kwargs.pop('notes', None)
            )

        return self._client.job_router.upsert_job(
            id = identifier,
            patch = router_job._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterJob._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def get_job(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> RouterJob
        """Retrieves an existing worker by Id.

        :param str identifier: Id of the worker.

        :return RouterJob
        :rtype ~azure.communication.jobrouter.RouterJob
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.get_job(
            id = identifier,
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
        #  type: (...) -> ItemPaged[PagedJob]
        """Retrieves list of jobs based on filter parameters.

        :keyword status: If specified, filter jobs by status. Default value is "all".
        :paramtype status: Union[str, ~azure.communication.jobrouter.JobStateSelector]
          Accepted value(s): pendingClassification, queued, assigned, completed, closed, cancelled,
            classificationFailed, active, all

        :keyword channel_id: If specified, filter jobs by channel. Default value is None.
        :paramtype channel_id: str

        :keyword queue_id: If specified, filter jobs by queue. Default value is None.
        :paramtype queue_id: str

        :keyword int results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of PagedJob
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.PagedJob]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

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

        return self._client.job_router.list_jobs(
            maxpagesize = results_per_page,
            status = status,
            channel_id = channel_id,
            queue_id = queue_id,
            # pylint:disable=protected-access
            cls = lambda objs: [PagedJob._from_generated(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def delete_job(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete a job by Id.

        :param str identifier: Id of the job to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.delete_job(
            id = identifier,
            **kwargs
        )

    @distributed_trace
    def get_in_queue_position(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ):
        #  type: (...) -> JobPositionDetails
        """Gets a job's position details.

        :param str identifier: Id of the job.

        :return: JobPositionDetails
        :rtype: ~azure.communication.jobrouter.JobPositionDetails
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.get_in_queue_position(
            id = identifier,
            **kwargs
        )

    @distributed_trace
    def close_job_action(
            self,
            identifier,  # type: str
            assignment_id,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> CloseJobResponse
        """Closes a completed job.

        :param str identifier: Id of the job.

        :param str assignment_id: The assignment within which the job is to be closed.

        :keyword disposition_code: Indicates the outcome of the job, populate this field with your own
         custom values. Default value is None.
        :paramtype disposition_code: str

        :keyword close_time: If not provided, worker capacity is released immediately along with a
         JobClosedEvent notification. If provided, worker capacity is released along with a JobClosedEvent notification
         at a future time. Default value is None.
        :paramtype close_time: ~datetime.datetime

        :keyword note: (Optional) A note that will be appended to the jobs' Notes collection with the
         current timestamp. Default value is None.
        :paramtype note: str

        :return: CloseJobResponse
        :rtype: ~azure.communication.jobrouter.CloseJobResponse
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        if not assignment_id:
            raise ValueError("assignment_id cannot be None.")

        disposition_code = kwargs.pop('disposition_code', None)
        close_time = kwargs.pop('close_time', None)
        note = kwargs.pop('note', None)

        return self._client.job_router.close_job_action(
            id = identifier,
            assignment_id = assignment_id,
            disposition_code = disposition_code,
            close_time = close_time,
            note = note,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: CloseJobResponse._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def complete_job_action(
            self,
            identifier,  # type: str
            assignment_id,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> CompleteJobResponse
        """Completes an assigned job.

        :param str identifier: Id of the job.

        :param str assignment_id: The assignment within the job to complete.

        :keyword note: (Optional) A note that will be appended to the jobs' Notes collection with th
         current timestamp. Default value is None.
        :paramtype note: str

        :return: CompleteJobResponse
        :rtype: ~azure.communication.jobrouter.CompleteJobResponse
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        if not assignment_id:
            raise ValueError("assignment_id cannot be None.")

        note = kwargs.pop('note', None)

        return self._client.job_router.complete_job_action(
            id = identifier,
            assignment_id = assignment_id,
            note = note,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: CompleteJobResponse._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def cancel_job_action(
            self,
            identifier,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> CancelJobResponse
        """Submits request to cancel an existing job by Id while supplying free-form cancellation reason.

        :param str identifier: Id of the job.

        :keyword note: (Optional) A note that will be appended to the jobs' Notes collection with the
         current timestamp. Default value is None.
        :paramtype note: str

        :keyword disposition_code: Indicates the outcome of the job, populate this field with your own
         custom values.
         If not provided, default value of "Cancelled" is set. Default value is None.
        :paramtype disposition_code: str

        :return: CancelJobResponse
        :rtype: ~azure.communication.jobrouter.CancelJobResponse
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("identifier cannot be None.")

        note = kwargs.pop('note', None)
        disposition_code = kwargs.pop('disposition_code', None)

        return self._client.job_router.cancel_job_action(
            id = identifier,
            note = note,
            disposition_code = disposition_code,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: CancelJobResponse._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace
    def reclassify_job_action(
            self,
            identifier,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> ReclassifyJobResponse
        """Reclassify a job.

        :param str identifier: Id of the job.

        :return: ReclassifyJobResponse
        :rtype: ~azure.communication.jobrouter.ReclassifyJobResponse
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.reclassify_job_action(
            id = identifier,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: ReclassifyJobResponse._from_generated(
                deserialized_response),
            **kwargs
        )

    # endregion Job

    # region Offer

    @distributed_trace
    def accept_job_action(
            self,
            worker_id,  # type: str
            offer_id,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> AcceptJobOfferResponse
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
    def decline_job_action(
            self,
            worker_id,  # type: str
            offer_id,  # type: str
            **kwargs,  # type: Any
    ):
        #  type: (...) -> DeclineJobOfferResponse
        """Declines an offer to work on a job.

        :param worker_id: Id of the worker.
        :type worker_id: str
        :param offer_id: Id of the offer.
        :type offer_id: str

        :return: DeclineJobOfferResponse
        :rtype: ~azure.communication.jobrouter.DeclineJobOfferResponse
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
            cls = lambda http_response, deserialized_response, args: DeclineJobOfferResponse._from_generated(
                deserialized_response),
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
