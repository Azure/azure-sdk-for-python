# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from urllib.parse import urlparse
# pylint: disable=unused-import,ungrouped-imports
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union, Tuple

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError  # pylint: disable=unused-import
from azure.core.async_paging import AsyncItemPaged

from .._shared.user_credential_async import CommunicationTokenCredential
from .._shared.utils import parse_connection_str, get_authentication_policy

from .._generated._serialization import Serializer  # pylint:disable=protected-access
from .._generated.aio import AzureCommunicationJobRouterService
from .._generated.models import (
    ClassificationPolicy,
    DistributionPolicy,
    ExceptionPolicy,
    ClassificationPolicyItem,
    DistributionPolicyItem,
    ExceptionPolicyItem,
    ExceptionRule,
    BestWorkerMode,
    LongestIdleMode,
    RoundRobinMode,
)
from .._models import (
    JobQueue,
    JobQueueItem,
)

from .._version import SDK_MONIKER
from .._utils import _get_value

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


class RouterAdministrationClient(object):  # pylint: disable=client-accepts-api-version-keyword,too-many-public-methods,too-many-lines
    """A client to interact with the AzureCommunicationService JobRouter service.

    This client provides operations to create, update, list and delete the following entities: classification policy,
    exception policy, distribution policy and queue.

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
    ) -> "RouterAdministrationClient":
        # type: (...) -> RouterAdministrationClient
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
    async def create_exception_policy(
            self,
            exception_policy_id: str,
            exception_rules: Dict[str, ExceptionRule],  # pylint: disable=used-before-assignment
            **kwargs: Any
    ) -> ExceptionPolicy:
        #  type: (...) -> ExceptionPolicy
        """Create a new exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :param exception_rules: (Optional) A dictionary collection of exception rules on the exception
          policy. Key is the Id of each exception rule.
        :type exception_rules: Dict[str, ~azure.communication.jobrouter.models.ExceptionRule]

        :keyword Optional[str] name: The name of this policy.

        :return ExceptionPolicy
        :rtype ~azure.communication.jobrouter.ExceptionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not exception_policy_id:
            raise ValueError("exception_policy_id cannot be None.")

        if not exception_rules or any(exception_rules) is False:
            raise ValueError("exception_rules cannot be None or empty.")

        exception_policy = ExceptionPolicy(
            name = kwargs.pop('name', None),
            exception_rules = exception_rules
        )

        return await self._client.job_router_administration.upsert_exception_policy(
            id = exception_policy_id,
            patch = exception_policy,
            **kwargs
        )

    @distributed_trace_async
    async def update_exception_policy(
            self,
            exception_policy_id: str,
            **kwargs: Any
    ) -> ExceptionPolicy:
        #  type: (...) -> ExceptionPolicy
        """Update an exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :keyword exception_rules: (Optional) A dictionary collection of exception rules on the exception
          policy. Key is the Id of each exception rule.
        :paramtype exception_rules: Optional[Dict[str, ~azure.communication.jobrouter.models.ExceptionRule]]

        :keyword Optional[str] name: The name of this policy.

        :keyword exception_policy: An instance of exception policy. Properties defined in
          class instance will not be considered if they are also specified in keyword arguments.
        :paramtype exception_policy: Optional[~azure.communication.jobrouter.ExceptionPolicy]

        :return ExceptionPolicy
        :rtype ~azure.communication.jobrouter.ExceptionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not exception_policy_id:
            raise ValueError("exception_policy_id cannot be None.")

        exception_policy = kwargs.pop("exception_policy", None)

        # pylint:disable=protected-access
        exception_rules = _get_value(
            kwargs.pop("exception_rules", None),
            getattr(exception_policy, 'exception_rules', None)
        )

        # pylint:disable=protected-access
        name = _get_value(
            kwargs.pop('name', None),
            getattr(exception_policy, 'name', None)
        )

        patch = ExceptionPolicy(
            name = name,
            exception_rules = exception_rules
        )

        return await self._client.job_router_administration.upsert_exception_policy(
            id = exception_policy_id,
            patch = patch,
            **kwargs
        )

    @distributed_trace_async
    async def get_exception_policy(
            self,
            exception_policy_id: str,
            **kwargs: Any
    ) -> ExceptionPolicy:
        #  type: (...) -> ExceptionPolicy
        """Retrieves an existing distribution policy by Id.

        :param str exception_policy_id: Id of the policy.

        :return ExceptionPolicy
        :rtype ~azure.communication.jobrouter.ExceptionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not exception_policy_id:
            raise ValueError("exception_policy_id cannot be None.")

        return await self._client.job_router_administration.get_exception_policy(
            id = exception_policy_id,
            **kwargs
        )

    @distributed_trace
    def list_exception_policies(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[ExceptionPolicyItem]:
        #  type: (...) -> AsyncItemPaged[ExceptionPolicyItem]
        """Retrieves existing exception policies.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of ExceptionPolicy

        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.ExceptionPolicyItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        return self._client.job_router_administration.list_exception_policies(
            params = params,
            **kwargs
        )

    @distributed_trace_async
    async def delete_exception_policy(
            self,
            exception_policy_id: str,
            **kwargs: Any
    ) -> None:
        # type: (...) -> None
        """Delete an exception policy by Id.

        :param str exception_policy_id: Id of the policy to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not exception_policy_id:
            raise ValueError("exception_policy_id cannot be None.")

        return await self._client.job_router_administration.delete_exception_policy(
            id = exception_policy_id,
            **kwargs
        )

    # endregion ExceptionPolicyAio

    # region DistributionPolicyAio

    @distributed_trace_async
    async def create_distribution_policy(
            self,
            distribution_policy_id: str,
            offer_ttl_seconds: float,
            mode: Union[BestWorkerMode, LongestIdleMode, RoundRobinMode],  # pylint: disable=used-before-assignment
            **kwargs: Any
    ) -> DistributionPolicy:
        #  type: (...) -> DistributionPolicy
        """Create a new distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.
        :param float offer_ttl_seconds: The expiry time of any offers created under this policy will
        be governed by the offer time to live.

        :param mode: Specified distribution mode
        :type mode: Union[~azure.communication.jobrouter.BestWorkerMode,
            ~azure.communication.jobrouter.LongestIdleMode, ~azure.communication.jobrouter.RoundRobinMode]

        :keyword Optional[str] name: The name of this policy.

        :return DistributionPolicy
        :rtype ~azure.communication.jobrouter.DistributionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not distribution_policy_id:
            raise ValueError("distribution_policy_id cannot be None.")

        if not offer_ttl_seconds:
            raise ValueError("offer_ttl_seconds cannot be None.")

        if not mode:
            raise ValueError("mode cannot be None.")

        distribution_policy = DistributionPolicy(
            name = kwargs.pop('name', None),
            offer_ttl_seconds = offer_ttl_seconds,
            mode = mode
        )

        return await self._client.job_router_administration.upsert_distribution_policy(
            id = distribution_policy_id,
            patch = distribution_policy,
            **kwargs
        )

    @distributed_trace_async
    async def update_distribution_policy(
            self,
            distribution_policy_id: str,
            **kwargs: Any
    ) -> DistributionPolicy:
        #  type: (...) -> DistributionPolicy
        """Update a distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :keyword Optional[float] offer_ttl_seconds: The expiry time of any offers created under this policy will
        be governed by the offer time to live.

        :keyword mode: Specified distribution mode
        :paramtype mode: Optional[Union[~azure.communication.jobrouter.BestWorkerMode,
            ~azure.communication.jobrouter.LongestIdleMode, ~azure.communication.jobrouter.RoundRobinMode]]

        :keyword Optional[str] name: The name of this policy.

        :keyword distribution_policy: An instance of distribution policy. Properties defined in
            class instance will not be considered if they are also specified in keyword arguments.
        :paramtype distribution_policy: Optional[~azure.communication.jobrouter.DistributionPolicy]

        :return DistributionPolicy
        :rtype ~azure.communication.jobrouter.DistributionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not distribution_policy_id:
            raise ValueError("distribution_policy_id cannot be None.")

        distribution_policy = kwargs.pop("distribution_policy", None)

        # pylint:disable=protected-access
        name = _get_value(
            kwargs.pop('name', None),
            getattr(distribution_policy, 'name', None)
        )

        # pylint:disable=protected-access
        offer_ttl_seconds = _get_value(
            kwargs.pop("offer_ttl_seconds", None),
            getattr(distribution_policy, 'offer_ttl_seconds', None)
        )

        # pylint:disable=protected-access
        mode = _get_value(
            kwargs.pop("mode", None),
            getattr(distribution_policy, 'mode', None)
        )

        patch = DistributionPolicy(
            name = name,
            offer_ttl_seconds = offer_ttl_seconds,
            mode = mode
        )

        return await self._client.job_router_administration.upsert_distribution_policy(
            id = distribution_policy_id,
            patch = patch,
            **kwargs
        )

    @distributed_trace_async
    async def get_distribution_policy(
            self,
            distribution_policy_id: str,
            **kwargs: Any
    ) -> DistributionPolicy:
        #  type: (...) -> DistributionPolicy
        """Retrieves an existing distribution policy by Id.

        :param str distribution_policy_id: Id of the policy.

        :return DistributionPolicy
        :rtype ~azure.communication.jobrouter.DistributionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not distribution_policy_id:
            raise ValueError("distribution_policy_id cannot be None.")

        return await self._client.job_router_administration.get_distribution_policy(
            id = distribution_policy_id,
            **kwargs
        )

    @distributed_trace
    def list_distribution_policies(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[DistributionPolicyItem]:
        #  type: (...) -> AsyncItemPaged[DistributionPolicyItem]
        """Retrieves existing distribution policies.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of DistributionPolicyItem
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.DistributionPolicyItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        return self._client.job_router_administration.list_distribution_policies(
            params = params,
            **kwargs
        )

    @distributed_trace_async
    async def delete_distribution_policy(
            self,
            distribution_policy_id: str,
            **kwargs: Any
    ) -> None:
        # type: (...) -> None
        """Delete a distribution policy by Id.

        :param str distribution_policy_id: Id of the policy to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not distribution_policy_id:
            raise ValueError("id cannot be None.")

        return await self._client.job_router_administration.delete_distribution_policy(
            id = distribution_policy_id,
            **kwargs
        )

    # endregion DistributionPolicyAio

    # region QueueAio

    @distributed_trace_async
    async def create_queue(
            self,
            queue_id: str,
            distribution_policy_id: str,
            **kwargs: Any
    ) -> JobQueue:
        #  type: (...) -> JobQueue
        """Create a job queue

        :param str queue_id: Id of the queue.

        :param str distribution_policy_id: The ID of the distribution policy that will determine
          how a job is distributed to workers.

        :keyword Optional[str] name: The name of this queue.

        :keyword labels: A set of key/value pairs that are
          identifying attributes used by the rules engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool]]]

        :keyword Optional[str] exception_policy_id: The ID of the exception policy that determines various
          job escalation rules.

        :return JobQueue
        :rtype ~azure.communication.jobrouter.JobQueue
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        if not distribution_policy_id:
            raise ValueError("distribution_policy_id cannot be None.")

        queue = JobQueue(
            name = kwargs.pop('name', None),
            distribution_policy_id = distribution_policy_id,
            labels = kwargs.pop('labels', None),
            exception_policy_id = kwargs.pop('exception_policy_id', None)
        )

        return await self._client.job_router_administration.upsert_queue(
            id = queue_id,
            patch = queue._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: JobQueue._from_generated(deserialized_response),
            **kwargs)

    @distributed_trace_async
    async def update_queue(
            self,
            queue_id: str,
            **kwargs: Any
    ) -> JobQueue:
        #  type: (...) -> JobQueue
        """Update a job queue

        :param str queue_id: Id of the queue.

        :keyword queue: An instance of JobQueue. Properties defined in
          class instance will not be considered if they are also specified in keyword arguments.
        :paramtype queue: Optional[~azure.communication.jobrouter.JobQueue]

        :keyword Optional[str] distribution_policy_id: The ID of the distribution policy that will determine
          how a job is distributed to workers.

        :keyword Optional[str] name: The name of this queue.

        :keyword labels: A set of key/value pairs that are
          identifying attributes used by the rules engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool]]]

        :keyword Optional[str] exception_policy_id: The ID of the exception policy that determines various
        job escalation rules.

        :return JobQueue
        :rtype ~azure.communication.jobrouter.JobQueue
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not queue_id:
            raise ValueError("identifier cannot be None.")

        queue = kwargs.pop('queue', None)

        # pylint:disable=protected-access
        name = _get_value(
            kwargs.pop('name', None),
            getattr(queue, 'name', None)
        )

        # pylint:disable=protected-access
        distribution_policy_id = _get_value(
            kwargs.pop('distribution_policy_id', None),
            getattr(queue, 'distribution_policy_id', None)
        )

        # pylint:disable=protected-access
        queue_labels = _get_value(
            kwargs.pop('labels', None),
            getattr(queue, 'labels', None)
        )

        # pylint:disable=protected-access
        exception_policy_id = _get_value(
            kwargs.pop('exception_policy_id', None),
            getattr(queue, 'exception_policy_id', None)
        )

        patch = JobQueue(
            name = name,
            distribution_policy_id = distribution_policy_id,
            labels = queue_labels,
            exception_policy_id = exception_policy_id
        )

        return await self._client.job_router_administration.upsert_queue(
            id = queue_id,
            patch = patch._to_generated(),  # pylint:disable=protected-access
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: JobQueue._from_generated(deserialized_response),
            **kwargs)

    @distributed_trace_async
    async def get_queue(
            self,
            queue_id: str,
            **kwargs: Any
    ) -> JobQueue:
        #  type: (...) -> JobQueue
        """Retrieves an existing queue by Id.

        :param str queue_id: Id of the queue.

        :return JobQueue
        :rtype ~azure.communication.jobrouter.JobQueue
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        return await self._client.job_router_administration.get_queue(
            id = queue_id,
            # pylint:disable=protected-access
            cls = lambda http_response, deserialized_response, args: JobQueue._from_generated(deserialized_response),
            **kwargs
        )

    @distributed_trace
    def list_queues(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[JobQueueItem]:
        #  type: (...) -> AsyncItemPaged[JobQueueItem]
        """Retrieves existing queues.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of JobQueueItem
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.JobQueueItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        return self._client.job_router_administration.list_queues(
            params = params,
            cls = lambda objs: [JobQueueItem._from_generated(x) for x in objs],  # pylint:disable=protected-access
            **kwargs
        )

    @distributed_trace_async
    async def delete_queue(
            self,
            queue_id: str,
            **kwargs: Any
    ) -> None:
        # type: (...) -> None
        """Deletes a queue by Id.

        :param str queue_id: Id of the queue to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        return await self._client.job_router_administration.delete_queue(
            id = queue_id,
            **kwargs
        )

    # endregion QueueAio

    # region ClassificationPolicyAio

    @distributed_trace_async
    async def create_classification_policy(
            self,
            classification_policy_id: str,
            **kwargs: Any
    ) -> ClassificationPolicy:
        # type: (...) -> ClassificationPolicy
        """ Create a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :keyword Optional[str] name: Friendly name of this policy.

        :keyword fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.
        :paramtype fallback_queue_id: Optional[str]

        :keyword queue_selectors: The queue selectors to resolve a queue for a given job.
        :paramtype queue_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticQueueSelector,
          ~azure.communication.jobrouter.ConditionalQueueSelector,
          ~azure.communication.jobrouter.RuleEngineQueueSelector,
          ~azure.communication.jobrouter.PassThroughQueueSelector,
          ~azure.communication.jobrouter.WeightedAllocationQueueSelector]]]

        :keyword prioritization_rule: The rule to determine a priority score for a given job.
        :paramtype prioritization_rule: Optional[Union[~azure.communication.jobrouter.StaticRule,
          ~azure.communication.jobrouter.ExpressionRule, ~azure.communication.jobrouter.AzureFunctionRule]]

        :keyword worker_selectors: The worker label selectors to attach to a given job.
        :paramtype worker_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticWorkerSelector,
          ~azure.communication.jobrouter.ConditionalWorkerSelector,
          ~azure.communication.jobrouter.RuleEngineWorkerSelector,
          ~azure.communication.jobrouter.PassThroughWorkerSelector,
          ~azure.communication.jobrouter.WeightedAllocationWorkerSelector]]]

        :return ClassificationPolicy
        :rtype ~azure.communication.jobrouter.ClassificationPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not classification_policy_id:
            raise ValueError("classification_policy_id cannot be None.")

        classification_policy = ClassificationPolicy(
            name = kwargs.pop("name", None),
            fallback_queue_id = kwargs.pop("fallback_queue_id", None),
            queue_selectors = kwargs.pop("queue_selectors", None),
            prioritization_rule = kwargs.pop("prioritization_rule", None),
            worker_selectors = kwargs.pop("worker_selectors", None))

        return await self._client.job_router_administration.upsert_classification_policy(
            id = classification_policy_id,
            patch = classification_policy,
            **kwargs)

    @distributed_trace_async
    async def update_classification_policy(
            self,
            classification_policy_id: str,
            **kwargs: Any
    ) -> ClassificationPolicy:
        # type: (...) -> ClassificationPolicy
        """ Update a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :keyword classification_policy: An instance of Classification policy. Properties defined in
            class instance will not be considered if they are also specified in keyword arguments.
        :paramtype classification_policy: Optional[~azure.communication.jobrouter.ClassificationPolicy]

        :keyword Optional[str] name: Friendly name of this policy.

        :keyword fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.
        :paramtype fallback_queue_id: Optional[str]

        :keyword queue_selectors: The queue selectors to resolve a queue for a given job.
        :paramtype queue_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticQueueSelector,
          ~azure.communication.jobrouter.ConditionalQueueSelector,
          ~azure.communication.jobrouter.RuleEngineQueueSelector,
          ~azure.communication.jobrouter.PassThroughQueueSelector,
          ~azure.communication.jobrouter.WeightedAllocationQueueSelector]]]

        :keyword prioritization_rule: The rule to determine a priority score for a given job.
        :paramtype prioritization_rule: Optional[Union[~azure.communication.jobrouter.StaticRule,
          ~azure.communication.jobrouter.ExpressionRule, ~azure.communication.jobrouter.AzureFunctionRule]]

        :keyword worker_selectors: The worker label selectors to attach to a given job.
        :paramtype worker_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticWorkerSelector,
          ~azure.communication.jobrouter.ConditionalWorkerSelector,
          ~azure.communication.jobrouter.RuleEngineWorkerSelector,
          ~azure.communication.jobrouter.PassThroughWorkerSelector,
          ~azure.communication.jobrouter.WeightedAllocationWorkerSelector]]]

        :return ClassificationPolicy
        :rtype ~azure.communication.jobrouter.ClassificationPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not classification_policy_id:
            raise ValueError("classification_policy_id cannot be None.")

        classification_policy = kwargs.pop('classification_policy', None)

        # pylint:disable=protected-access
        name = _get_value(
            kwargs.pop('name', None),
            getattr(classification_policy, 'name', None)
        )

        # pylint:disable=protected-access
        fallback_queue_id = _get_value(
            kwargs.pop('fallback_queue_id', None),
            getattr(classification_policy, 'fallback_queue_id', None)
        )

        # pylint:disable=protected-access
        queue_selectors = _get_value(
            kwargs.pop('queue_selectors', None),
            getattr(classification_policy, 'queue_selectors', None)
        )

        # pylint:disable=protected-access
        prioritization_rule = _get_value(
            kwargs.pop('prioritization_rule', None),
            getattr(classification_policy, 'prioritization_rule', None)
        )

        # pylint:disable=protected-access
        worker_selectors = _get_value(
            kwargs.pop('worker_selectors', None),
            getattr(classification_policy, 'worker_selectors', None)
        )

        patch = ClassificationPolicy(
            name = name,
            fallback_queue_id = fallback_queue_id,
            queue_selectors = queue_selectors,
            prioritization_rule = prioritization_rule,
            worker_selectors = worker_selectors)

        return await self._client.job_router_administration.upsert_classification_policy(
            id = classification_policy_id,
            patch = patch,
            **kwargs)

    @distributed_trace_async
    async def get_classification_policy(
            self,
            classification_policy_id: str,
            **kwargs: Any
    ) -> ClassificationPolicy:
        # type: (...) -> ClassificationPolicy
        """Retrieves an existing classification policy by Id.

        :param str classification_policy_id: The id of classification policy.

        :return ClassificationPolicy
        :rtype ~azure.communication.jobrouter.ClassificationPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if not classification_policy_id:
            raise ValueError("identifier cannot be None.")

        return await self._client.job_router_administration.get_classification_policy(
            classification_policy_id,
            **kwargs)

    @distributed_trace
    def list_classification_policies(
            self,
            **kwargs: Any
    ) -> AsyncItemPaged[ClassificationPolicyItem]:
        # type: (...) -> AsyncItemPaged[ClassificationPolicyItem]
        """Retrieves existing classification policies.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of ClassificationPolicy
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.PagedClassificationPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        results_per_page = kwargs.pop("results_per_page", None)

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        return self._client.job_router_administration.list_classification_policies(
            params = params,
            **kwargs)

    @distributed_trace_async
    async def delete_classification_policy(
            self,
            classification_policy_id: str,
            **kwargs: Any
    ) -> None:
        # type: (...) -> None
        """Delete a classification policy by Id.

        :param str classification_policy_id: The id of classification policy.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if not classification_policy_id:
            raise ValueError("classification_policy_id cannot be None.")

        return await self._client.job_router_administration.delete_classification_policy(
            id = classification_policy_id,
            **kwargs)

    # endregion ClassificationPolicyAio

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "RouterAdministrationClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)
