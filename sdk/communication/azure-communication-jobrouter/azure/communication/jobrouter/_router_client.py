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
    QueueStatistics
)
from ._models import (
    LabelCollection,
    JobQueue,
)
from ._shared.user_credential import CommunicationTokenCredential
from ._shared.utils import parse_connection_str, get_authentication_policy
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.paging import ItemPaged


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
        #  type: (...) -> ItemPaged[JobQueue]
        """Retrieves existing queues.

        :keyword int results_per_page: The maximum number of results to be returned per page.
        :return: An iterator like instance of JobQueue
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.JobQueue]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

        results_per_page = kwargs.pop("results_per_page", None)

        return self._client.job_router.list_queues(
            maxpagesize = results_per_page,
            cls = lambda objs: [JobQueue._from_generated(x) for x in objs],  # pylint:disable=protected-access
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
