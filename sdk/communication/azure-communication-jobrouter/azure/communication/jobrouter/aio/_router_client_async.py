# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from urllib.parse import urlparse
# pylint: disable=unused-import,ungrouped-imports
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError
from azure.core.async_paging import AsyncItemPaged

from .._shared.user_credential_async import CommunicationTokenCredential
from .._shared.utils import parse_connection_str, get_authentication_policy
from .._generated.aio import AzureCommunicationJobRouterService
from .._generated.models import (
    ClassificationPolicy,
    DistributionPolicy,
    ExceptionPolicy,
    QueueStatistics,
    WorkerStateSelector
)
from .._models import (
    LabelCollection,
    JobQueue,
    RouterWorker
)

from .._version import SDK_MONIKER
from .._utils import _add_repeatability_headers


class RouterClient(object):  # pylint: disable=client-accepts-api-version-keyword,too-many-public-methods
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
        :rtype: ~azure.communication.RouterClient
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    # region ExceptionPolicyAio

    @distributed_trace_async
    async def upsert_exception_policy(
            self,
            identifier: str,
            **kwargs: Any
    ) -> ExceptionPolicy:
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

        return await self._client.job_router.upsert_exception_policy(
            id = identifier,
            patch = exception_policy,
            **kwargs
        )

    @distributed_trace_async
    async def get_exception_policy(
            self,
            identifier: str,
            **kwargs: Any
    ) -> ExceptionPolicy:
        #  type: (...) -> ExceptionPolicy
        """Retrieves an existing distribution policy by Id.

        :param str identifier: Id of the policy.

        :return DistributionPolicy
        :rtype ~azure.communication.jobrouter.ExceptionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return await self._client.job_router.get_exception_policy(
            id = identifier,
            **kwargs
        )

    @distributed_trace
    def list_exception_policies(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[ExceptionPolicy]:
        #  type: (...) -> AsyncItemPaged[ExceptionPolicy]
        """Retrieves existing exception policies.

        :keyword int results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of ExceptionPolicy
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.ExceptionPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        return self._client.job_router.list_exception_policies(
            maxpagesize = results_per_page,
            **kwargs
        )

    @distributed_trace_async
    async def delete_exception_policy(
            self,
            identifier: str,
            **kwargs: Any
    ) -> None:
        # type: (...) -> None
        """Delete an exception policy by Id.

        :param str identifier: Id of the policy to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("identifier cannot be None.")

        return await self._client.job_router.delete_exception_policy(
            id = identifier,
            **kwargs
        )

    # endregion ExceptionPolicyAio

#region DistributionPolicyAio

    @distributed_trace_async
    async def upsert_distribution_policy(
            self,
            **kwargs: Any
    ) -> DistributionPolicy:
        #  type: (...) -> DistributionPolicy
        """Create or update a new distribution policy.

        :keyword str identifier: Id of the distribution policy.
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
        identifier = kwargs.pop("identifier", None)
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

        return await self._client.job_router.upsert_distribution_policy(
            id = identifier,
            patch = distribution_policy,
            **kwargs
        )

    @distributed_trace_async
    async def get_distribution_policy(
            self,
            identifier: str,
            **kwargs: Any
    ) -> DistributionPolicy:
        #  type: (...) -> DistributionPolicy
        """Retrieves an existing distribution policy by Id.

        :param str identifier: Id of the policy.

        :return DistributionPolicy
        :rtype ~azure.communication.jobrouter.DistributionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("id cannot be None.")

        return await self._client.job_router.get_distribution_policy(
            id = identifier,
            **kwargs
        )

    @distributed_trace
    def list_distribution_policies(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[DistributionPolicy]:
        #  type: (...) -> AsyncItemPaged[DistributionPolicy]
        """Retrieves existing distribution policies.

        :keyword int results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of DistributionPolicy
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.DistributionPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        return self._client.job_router.list_distribution_policies(
            maxpagesize = results_per_page,
            **kwargs
        )

    @distributed_trace_async
    async def delete_distribution_policy(
            self,
            identifier: str,
            **kwargs: Any
    ) -> None:
        # type: (...) -> None
        """Delete a distribution policy by Id.

        :param str identifier: Id of the policy to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("id cannot be None.")

        return await self._client.job_router.delete_distribution_policy(
            id = identifier,
            **kwargs
        )

#endregion DistributionPolicyAio

#region QueueAio

    @distributed_trace_async
    async def upsert_queue(
            self,
            identifier: str,
            **kwargs: Any
    ) -> JobQueue:
        #  type: (...) -> JobQueue
        """Creates or update a job queue

        :param str identifier: Id of the queue.

        :keyword ~azure.communication.jobrouter.JobQueue queue: An instance of JobQueue

        :keyword str distribution_policy_id: The ID of the distribution policy that will determine
        how a job is distributed to workers.

        :keyword str name: The name of this queue.

        :keyword Union[~azure.communication.jobrouter.LabelCollection, Dict] labels: A set of key/value pairs that are
        identifying attributes used by the rules engines to make decisions.

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

        return await self._client.job_router.upsert_queue(
            id = identifier,
            patch = queue._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: JobQueue._from_generated(deserialized_response),
            **kwargs)

    @distributed_trace_async
    async def get_queue(
            self,
            identifier: str,
            **kwargs: Any
    ) -> JobQueue:
        #  type: (...) -> JobQueue
        """Retrieves an existing queue by Id.

        :param str identifier: Id of the queue.

        :return JobQueue
        :rtype ~azure.communication.jobrouter.JobQueue
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("id cannot be None.")

        return await self._client.job_router.get_queue(
            id = identifier,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: JobQueue._from_generated(deserialized_response),
            **kwargs
        )

    @distributed_trace_async
    async def get_queue_statistics(
            self,
            identifier: str,
            **kwargs: Any
    ) -> QueueStatistics:
        #  type: (...) -> QueueStatistics
        """Retrieves a queue's statistics.

        :param str identifier: Id of the queue.

        :return QueueStatistics
        :rtype ~azure.communication.jobrouter.QueueStatistics
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return await self._client.job_router.get_queue_statistics(
            id = identifier,
            **kwargs
        )

    @distributed_trace
    def list_queues(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[JobQueue]:
        #  type: (...) -> AsyncItemPaged[JobQueue]
        """Retrieves existing queues.

        :keyword int results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of JobQueue
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.JobQueue]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        return self._client.job_router.list_queues(
            maxpagesize = results_per_page,
            cls = lambda objs: [JobQueue._from_generated(x) for x in objs],  # pylint:disable=protected-access
            **kwargs
        )

    @distributed_trace_async
    async def delete_queue(
            self,
            identifier: str,
            **kwargs: Any
    ) -> None:
        # type: (...) -> None
        """Deletes a queue by Id.

        :param str identifier: Id of the queue to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("id cannot be None.")

        return await self._client.job_router.delete_queue(
            id = identifier,
            **kwargs
        )

#endregion QueueAio

#region ClassificationPolicyAio

    @distributed_trace_async
    async def upsert_classification_policy(
            self,
            identifier: str,
            **kwargs: Any
    ) -> ClassificationPolicy:
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

        return await self._client.job_router.upsert_classification_policy(
            id = identifier,
            patch = classification_policy,
            **kwargs)

    @distributed_trace_async
    async def get_classification_policy(
            self,
            identifier: str,
            **kwargs: Any
    ) -> ClassificationPolicy:
        # type: (...) -> ClassificationPolicy
        """Retrieves an existing classification policy by Id.

        :param str identifier: The id of classification policy.
        :return ClassificationPolicy
        :rtype ~azure.communication.jobrouter.ClassificationPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return await self._client.job_router.get_classification_policy(
            identifier,
            **kwargs)

    @distributed_trace
    def list_classification_policies(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[ClassificationPolicy]:
        # type: (...) -> AsyncItemPaged[ClassificationPolicy]
        """Retrieves existing classification policies.

        :keyword int results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of ClassificationPolicy
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.ClassificationPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        results_per_page = kwargs.pop("results_per_page", None)

        return self._client.job_router.list_classification_policies(
            maxpagesize = results_per_page,
            **kwargs)

    @distributed_trace_async
    async def delete_classification_policy(
            self,
            identifier: str,
            **kwargs: Any
    ) -> None:
        # type: (...) -> None
        """Delete a classification policy by Id.

        :param str identifier: The id of classification policy.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return await self._client.job_router.delete_classification_policy(
            id = identifier,
            **kwargs)

#endregion ClassificationPolicyAio

    # region WorkerAio

    @distributed_trace_async
    async def upsert_worker(
            self,
            identifier: str,
            **kwargs: Any
    ) -> RouterWorker:
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

        return await self._client.job_router.upsert_worker(
            worker_id = identifier,
            patch = router_worker._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: RouterWorker._from_generated(
                deserialized_response),
            **kwargs
        )

    @distributed_trace_async
    async def get_worker(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ) -> RouterWorker:
        #  type: (...) -> RouterWorker
        """Retrieves an existing worker by Id.

        :param str identifier: Id of the worker.

        :return RouterWorker
        :rtype ~azure.communication.jobrouter.RouterWorker
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not identifier:
            raise ValueError("identifier cannot be None.")

        return await self._client.job_router.get_worker(
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
    ) -> AsyncItemPaged[RouterWorker]:
        #  type: (...) -> AsyncItemPaged[RouterWorker]
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

        :return: An iterator like instance of RouterWorker
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.RouterWorker]
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
            cls = lambda objs: [RouterWorker._from_generated(x) for x in objs],
            **kwargs
        )

    @distributed_trace_async
    async def delete_worker(
            self,
            identifier,  # type: str
            **kwargs  # type: Any
    ) -> None:
        # type: (...) -> None
        """Delete a worker by Id.

        :param str identifier: Id of the worker to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("identifier cannot be None.")

        return await self._client.job_router.delete_worker(
            worker_id = identifier,
            **kwargs
        )
    # endRegion WorkerAio

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "RouterClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)
