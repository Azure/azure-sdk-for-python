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
    JobQueue,
    DistributionPolicy,
    BestWorkerMode,
    LongestIdleMode,
    RoundRobinMode
)
from .._models import (
    LabelCollection
)

from .._version import SDK_MONIKER
from .._utils import _add_repeatability_headers


class RouterClient(object):  # pylint: disable=client-accepts-api-version-keyword
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

#region DistributionPolicyAio

    @distributed_trace_async
    async def create_distribution_policy(
            self,
            offer_ttl_seconds: float,
            mode: Union[BestWorkerMode, LongestIdleMode, RoundRobinMode],
            **kwargs: Any
    ) -> DistributionPolicy:
        #  type: (...) -> DistributionPolicy
        """Creates a new distribution policy.

        :param float offer_ttl_seconds: The expiry time of any offers created under this policy will
        be governed by the offer time to live.

        :param mode: Specified distribution mode
        :type mode: Union[~azure.communication.jobrouter.BestWorkerMode, ~azure.communication.jobrouter.LongestIdleMode,
        ~azure.communication.jobrouter.RoundRobinMode]

        :keyword str name: The name of this policy.

        :return DistributionPolicy
        :rtype ~azure.communication.jobrouter.DistributionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """
        repeatability_headers = _add_repeatability_headers(**kwargs)

        if not offer_ttl_seconds:
            raise ValueError("offer_ttl_seconds cannot be None.")

        if not mode:
            raise ValueError("mode cannot be None.")

        distribution_policy = DistributionPolicy(
            name = kwargs.pop('name', None),
            offer_ttl_seconds = offer_ttl_seconds,
            mode = mode
        )

        return await self._client.job_router.create_distribution_policy(
            distribution_policy = distribution_policy,
            repeatability_request_id = repeatability_headers['repeatability_request_id'],
            repeatability_first_sent = repeatability_headers['repeatability_first_sent'],
            **kwargs
        )

    @distributed_trace_async
    async def update_distribution_policy(
            self,
            identifier: str,
            distribution_policy: DistributionPolicy,
            **kwargs: Any
    ) -> DistributionPolicy:
        #  type: (...) -> DistributionPolicy
        """Updates a distribution policy.

        :param str identifier: Id of the distribution policy.

        :param ~azure.communication.jobrouter.DistributionPolicy distribution_policy: Updated policy

        :return DistributionPolicy
        :rtype ~azure.communication.jobrouter.DistributionPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("id cannot be None.")

        return await self._client.job_router.update_distribution_policy(
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
    async def create_queue(
            self,
            distribution_policy_id: str,
            **kwargs: Any
    ) -> JobQueue:
        #  type: (...) -> JobQueue
        """Creates new queue

        :param str distribution_policy_id: The ID of the distribution policy that will determine
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
        repeatability_headers = _add_repeatability_headers(**kwargs)

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

        return await self._client.job_router.create_queue(
            queue,
            repeatability_request_id = repeatability_headers['repeatability_request_id'],
            repeatability_first_sent = repeatability_headers['repeatability_first_sent'],
            **kwargs)

    @distributed_trace_async
    async def update_queue(
            self,
            identifier: str,
            queue: JobQueue,
            **kwargs: Any
    ) -> JobQueue:
        #  type: (...) -> JobQueue
        """Updates a queue.

        :param str identifier: Id of the queue.

        :param ~azure.communication.jobrouter.JobQueue queue: Updated queue

        :return JobQueue
        :rtype ~azure.communication.jobrouter.JobQueue
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("id cannot be None.")

        return await self._client.job_router.update_queue(
            id = identifier,
            patch = queue,
            **kwargs
        )

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
    async def create_classification_policy(
            self,
            **kwargs: Any
    ) -> ClassificationPolicy:
        # type: (...) -> ClassificationPolicy
        """ Creates a new classification policy

        :keyword str name: Friendly name of this policy.

        :keyword str fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.

        :keyword List[~azure.communication.jobrouter.QueueSelectorAttachment] queue_selectors: The queue selectors
        to resolve a queue for a given job.

        :keyword ~azure.communication.jobrouter.RouterRule prioritization_rule: The rule to determine a priority
        score for a given job.

        :keyword List[~azure.communication.jobrouter.WorkerSelectorAttachment] worker_selectors: The worker label
        selectors to attach to a given job.

        :keyword Union[str, datetime] repeatability_request_id: As described in
        https://docs.oasis-open.org/odata/repeatable-requests/v1.0/cs01/repeatable-requests-v1.0-cs01.html.
        If not provided, one will be generated.

        :keyword str repeatability_first_sent: As described in
         https://docs.oasis-open.org/odata/repeatable-requests/v1.0/cs01/repeatable-requests-v1.0-cs01.html.
         If not provided, one will be generated.
        """

        repeatability_headers = _add_repeatability_headers(**kwargs)

        classification_policy = ClassificationPolicy(
            name = kwargs.pop("name", None),
            fallback_queue_id = kwargs.pop("fallback_queue_id", None),
            queue_selectors = kwargs.pop("queue_selectors", None),
            prioritization_rule = kwargs.pop("prioritization_rule", None),
            worker_selectors = kwargs.pop("worker_selectors", None))

        return await self._client.job_router.create_classification_policy(
            classification_policy,
            repeatability_request_id = repeatability_headers['repeatability_request_id'],
            repeatability_first_sent = repeatability_headers['repeatability_first_sent'],
            **kwargs)

    @distributed_trace_async
    async def update_classification_policy(
            self,
            identifier: str,
            classification_policy: ClassificationPolicy,
            **kwargs: Any
    ) -> ClassificationPolicy:
        # type: (...) -> ClassificationPolicy
        """Updates a classification policy

        :param str identifier: The id of classification policy.
        :param ~azure.communication.jobrouter.ClassificationPolicy classification_policy: Updated classification policy
        :return ClassificationPolicy
        :rtype ~azure.communication.jobrouter.ClassificationPolicy
        :raises ~azure.core.exceptions.HttpResponseError, ValueError
        """

        if not identifier:
            raise ValueError("id cannot be None.")

        return await self._client.job_router.update_classification_policy(
            identifier,
            classification_policy = classification_policy,
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
            raise ValueError("id cannot be None.")

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
            raise ValueError("id cannot be None.")

        return await self._client.job_router.delete_classification_policy(
            id = identifier,
            **kwargs)

#endregion ClassificationPolicyAio

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "RouterClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)
