# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
from typing import (
    List,
    Any,
    Optional,
    Dict,
    Union,
    overload,
)

from azure.core import MatchConditions
from .. import models as _models
from azure.core.tracing.decorator import distributed_trace
from ._operations import (
    JobRouterClientOperationsMixin as JobRouterClientOperationsMixinGenerated,
    JobRouterAdministrationClientOperationsMixin as JobRouterAdministrationClientOperationsMixinGenerated,
)
from ._operations import JSON


class JobRouterAdministrationClientOperationsMixin(JobRouterAdministrationClientOperationsMixinGenerated):
    # region DistributionPolicy
    @distributed_trace
    def create_exception_policy(
        self,
        exception_policy_id: str,
        exception_policy: _models.ExceptionPolicy,
        *,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> _models.ExceptionPolicy:
        """Create a new exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :param exception_policy: An instance of exception policy.
        :type exception_policy: ~azure.communication.jobrouter.ExceptionPolicy

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.ExceptionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError


        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops.py
                :start-after: [START create_exception_policy]
                :end-before: [END create_exception_policy]
                :language: python
                :dedent: 8
                :caption: Using a JobRouterAdministrationClient to create an exception policy
        """
        if not exception_policy_id:
            raise ValueError("exception_policy_id cannot be None.")

        return super().upsert_exception_policy(id=exception_policy_id, resource=exception_policy, **kwargs)

    @overload
    def update_exception_policy(
        self,
        exception_policy_id: str,
        exception_policy: _models.ExceptionPolicy,
        *,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> _models.ExceptionPolicy:
        """Update an exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :param exception_policy: An instance of exception policy. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type exception_policy: ~azure.communication.jobrouter.ExceptionPolicy

        :return: Instance of ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.ExceptionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    def update_exception_policy(
        self,
        exception_policy_id: str,
        *,
        exception_rules: Optional[Dict[str, _models.ExceptionRule]],
        name: Optional[str],
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any
    ) -> _models.ExceptionPolicy:
        """Update an exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :keyword exception_rules: (Optional) A dictionary collection of exception rules on the exception
          policy. Key is the Id of each exception rule.
        :paramtype exception_rules: Optional[Dict[str, ~azure.communication.jobrouter.ExceptionRule]]

        :keyword Optional[str] name: The name of this policy.

        :return: Instance of ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.ExceptionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace
    def update_exception_policy(
        self, exception_policy_id: str, *args: _models.ExceptionPolicy, **kwargs: Any
    ) -> _models.ExceptionPolicy:
        """Update an exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :param exception_policy: An instance of exception policy. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type exception_policy: ~azure.communication.jobrouter.ExceptionPolicy

        :keyword exception_rules: (Optional) A dictionary collection of exception rules on the exception
          policy. Key is the Id of each exception rule.
        :paramtype exception_rules: Optional[Dict[str, ~azure.communication.jobrouter.ExceptionRule]]

        :keyword Optional[str] name: The name of this policy.

        :return: Instance of ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.ExceptionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError


        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops.py
                :start-after: [START update_exception_policy]
                :end-before: [END update_exception_policy]
                :language: python
                :dedent: 8
                :caption: Using a JobRouterAdministrationClient to update an exception policy
        """
        if not exception_policy_id:
            raise ValueError("exception_policy_id cannot be None.")

        exception_policy = _models.ExceptionPolicy()
        if len(args) == 1:
            exception_policy = args[0]

        patch = _models.ExceptionPolicy(
            name=kwargs.pop("name", exception_policy.name),
            exception_rules=kwargs.pop("exception_rules", exception_policy.exception_rules),
        )

        return super().upsert_exception_policy(id=exception_policy_id, resource=patch, **kwargs)

    # endregion ExceptionPolicy

    # region DistributionPolicy

    @distributed_trace
    def create_distribution_policy(
        self, distribution_policy_id: str, distribution_policy: _models.DistributionPolicy, **kwargs: Any
    ) -> _models.DistributionPolicy:
        """Create a new distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :param distribution_policy: An instance of distribution policy.
        :type distribution_policy: ~azure.communication.jobrouter.DistributionPolicy

        :return: Instance of DistributionPolicy
        :rtype: ~azure.communication.jobrouter.DistributionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops.py
                :start-after: [START create_distribution_policy]
                :end-before: [END create_distribution_policy]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to create a distribution policy
        """
        if not distribution_policy_id:
            raise ValueError("distribution_policy_id cannot be None.")

        return super().upsert_distribution_policy(id=distribution_policy_id, resource=distribution_policy, **kwargs)

    @overload
    def update_distribution_policy(
        self, distribution_policy_id: str, distribution_policy: _models.DistributionPolicy, **kwargs: Any
    ) -> _models.DistributionPolicy:
        """Update a distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :param distribution_policy: An instance of distribution policy. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type distribution_policy: ~azure.communication.jobrouter.DistributionPolicy

        :return: Instance of DistributionPolicy
        :rtype: ~azure.communication.jobrouter.DistributionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    def update_distribution_policy(
        self,
        distribution_policy_id: str,
        *,
        name: Optional[str],
        offer_expires_after_seconds: Optional[float],
        mode: Optional[Union[_models.BestWorkerMode, _models.LongestIdleMode, _models.RoundRobinMode]],
        **kwargs: Any
    ) -> _models.DistributionPolicy:
        """Update a distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :keyword Optional[float] offer_expires_after_seconds: The expiry time of any offers created under this policy
          will be governed by the offer time to live.

        :keyword mode: Specified distribution mode
        :paramtype mode: Optional[Union[~azure.communication.jobrouter.BestWorkerMode,
            ~azure.communication.jobrouter.LongestIdleMode, ~azure.communication.jobrouter.RoundRobinMode]]

        :keyword Optional[str] name: The name of this policy.

        :return: Instance of DistributionPolicy
        :rtype: ~azure.communication.jobrouter.DistributionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace
    def update_distribution_policy(
        self, distribution_policy_id: str, *args: _models.DistributionPolicy, **kwargs: Any
    ) -> _models.DistributionPolicy:
        """Update a distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :param distribution_policy: An instance of distribution policy. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type distribution_policy: ~azure.communication.jobrouter.DistributionPolicy

        :keyword Optional[float] offer_expires_after_seconds: The expiry time of any offers created under this policy
          will be governed by the offer time to live.

        :keyword mode: Specified distribution mode
        :paramtype mode: Optional[Union[~azure.communication.jobrouter.BestWorkerMode,
            ~azure.communication.jobrouter.LongestIdleMode, ~azure.communication.jobrouter.RoundRobinMode]]

        :keyword Optional[str] name: The name of this policy.

        :return: Instance of DistributionPolicy
        :rtype: ~azure.communication.jobrouter.DistributionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops.py
                :start-after: [START update_distribution_policy]
                :end-before: [END update_distribution_policy]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to update a distribution policy
        """
        if not distribution_policy_id:
            raise ValueError("distribution_policy_id cannot be None.")

        distribution_policy = _models.DistributionPolicy()
        if len(args) == 1:
            distribution_policy = args[0]

        patch = _models.DistributionPolicy(
            name=kwargs.pop("name", distribution_policy.name),
            offer_expires_after_seconds=kwargs.pop(
                "offer_expires_after_seconds", distribution_policy.offer_expires_after_seconds
            ),
            mode=kwargs.pop("mode", distribution_policy.mode),
        )

        return super().upsert_distribution_policy(id=distribution_policy_id, resource=patch, **kwargs)

    # endregion DistributionPolicy

    # region Queue

    @distributed_trace
    def create_queue(self, queue_id: str, queue: _models.RouterQueue, **kwargs: Any) -> _models.RouterQueue:
        """Create a job queue

        :param str queue_id: Id of the queue.

        :param queue: An instance of JobQueue.
        :type queue: ~azure.communication.jobrouter.RouterQueue

        :return: Instance of RouterQueue
        :rtype: ~azure.communication.jobrouter.RouterQueue
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops.py
                :start-after: [START create_queue]
                :end-before: [END create_queue]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to create a queue
        """
        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        return super().upsert_queue(id=queue_id, resource=queue, **kwargs)

    @overload
    def update_queue(self, queue_id: str, queue: _models.RouterQueue, **kwargs: Any) -> _models.RouterQueue:
        """Update a job queue

        :param str queue_id: Id of the queue.

        :param queue: An instance of JobQueue. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type queue: ~azure.communication.jobrouter.RouterQueue

        :return: Instance of RouterQueue
        :rtype: ~azure.communication.jobrouter.RouterQueue
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    def update_queue(
        self,
        queue_id: str,
        *,
        distribution_policy_id: Optional[str],
        name: Optional[str],
        labels: Optional[Dict[str, Union[int, float, str, bool]]],
        exception_policy_id: Optional[str],
        **kwargs: Any
    ) -> _models.RouterQueue:
        """Update a job queue

        :param str queue_id: Id of the queue.

        :keyword Optional[str] distribution_policy_id: The ID of the distribution policy that will determine
          how a job is distributed to workers.

        :keyword Optional[str] name: The name of this queue.

        :keyword labels: A set of key/value pairs that are
          identifying attributes used by the rules engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool]]]

        :keyword Optional[str] exception_policy_id: The ID of the exception policy that determines various
          job escalation rules.

        :return: Instance of RouterQueue
        :rtype: ~azure.communication.jobrouter.RouterQueue
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace
    def update_queue(self, queue_id: str, *args: _models.RouterQueue, **kwargs: Any) -> _models.RouterQueue:
        """Update a job queue

        :param str queue_id: Id of the queue.

        :param queue: An instance of JobQueue. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type queue: ~azure.communication.jobrouter.RouterQueue

        :keyword Optional[str] distribution_policy_id: The ID of the distribution policy that will determine
          how a job is distributed to workers.

        :keyword Optional[str] name: The name of this queue.

        :keyword labels: A set of key/value pairs that are
          identifying attributes used by the rules engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool]]]

        :keyword Optional[str] exception_policy_id: The ID of the exception policy that determines various
          job escalation rules.

        :return: Instance of RouterQueue
        :rtype: ~azure.communication.jobrouter.RouterQueue
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops.py
                :start-after: [START update_queue]
                :end-before: [END update_queue]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to update a queue
        """
        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        queue = _models.RouterQueue()
        if len(args) == 1:
            queue = args[0]

        patch = _models.RouterQueue(
            name=kwargs.pop("name", queue.name),
            distribution_policy_id=kwargs.pop("distribution_policy_id", queue.distribution_policy_id),
            labels=kwargs.pop("labels", queue.labels),
            exception_policy_id=kwargs.pop("exception_policy_id", queue.exception_policy_id),
        )

        return super().upsert_queue(id=queue_id, resource=patch, **kwargs)

    # endregion Queue

    # region ClassificationPolicy

    @distributed_trace
    def create_classification_policy(
        self, classification_policy_id: str, classification_policy: _models.ClassificationPolicy, **kwargs: Any
    ) -> _models.ClassificationPolicy:
        """Create a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :param classification_policy: An instance of Classification policy.
        :type classification_policy: ~azure.communication.jobrouter.ClassificationPolicy

        :return: Instance of ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.ClassificationPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops.py
                :start-after: [START create_classification_policy]
                :end-before: [END create_classification_policy]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to create a classification policy
        """
        if not classification_policy_id:
            raise ValueError("classification_policy_id cannot be None.")

        return super().upsert_classification_policy(
            id=classification_policy_id, resource=classification_policy, **kwargs
        )

    @overload
    def update_classification_policy(
        self, classification_policy_id: str, classification_policy: _models.ClassificationPolicy, **kwargs: Any
    ) -> _models.ClassificationPolicy:
        """Update a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :param classification_policy: An instance of Classification policy. This is a positional-only
         parameter. Please provide either this or individual keyword parameters.
        :type classification_policy: ~azure.communication.jobrouter.ClassificationPolicy

        :return: Instance of ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.ClassificationPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    def update_classification_policy(
        self,
        classification_policy_id: str,
        *,
        name: Optional[str],
        fallback_queue_id: Optional[str],
        queue_selectors: Optional[
            List[
                Union[
                    _models.StaticQueueSelectorAttachment,
                    _models.ConditionalQueueSelectorAttachment,
                    _models.RuleEngineQueueSelectorAttachment,
                    _models.PassThroughQueueSelectorAttachment,
                    _models.WeightedAllocationQueueSelectorAttachment,
                ]
            ]
        ],  # pylint: disable=line-too-long
        prioritization_rule: Optional[
            Union[
                _models.StaticRouterRule,
                _models.ExpressionRouterRule,
                _models.FunctionRouterRule,
                _models.WebhookRouterRule,
            ]
        ],  # pylint: disable=line-too-long
        worker_selectors: Optional[
            List[
                Union[
                    _models.StaticWorkerSelectorAttachment,
                    _models.ConditionalWorkerSelectorAttachment,
                    _models.RuleEngineWorkerSelectorAttachment,
                    _models.PassThroughWorkerSelectorAttachment,
                    _models.WeightedAllocationWorkerSelectorAttachment,
                ]
            ]
        ],  # pylint: disable=line-too-long
        **kwargs: Any
    ) -> _models.ClassificationPolicy:
        """Update a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :keyword Optional[str] name: Friendly name of this policy.

        :keyword fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.
        :paramtype fallback_queue_id: Optional[str]

        :keyword queue_selectors: The queue selectors to resolve a queue for a given job.
        :paramtype queue_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticQueueSelectorAttachment,
          ~azure.communication.jobrouter.ConditionalQueueSelectorAttachment,
          ~azure.communication.jobrouter.RuleEngineQueueSelectorAttachment,
          ~azure.communication.jobrouter.PassThroughQueueSelectorAttachment,
          ~azure.communication.jobrouter.WeightedAllocationQueueSelectorAttachment]]]

        :keyword prioritization_rule: The rule to determine a priority score for a given job.
        :paramtype prioritization_rule: Optional[Union[~azure.communication.jobrouter.StaticRouterRule,
          ~azure.communication.jobrouter.ExpressionRouterRule,
          ~azure.communication.jobrouter.FunctionRouterRule,
          ~azure.communication.jobrouter.WebhookRouterRule]]

        :keyword worker_selectors: The worker label selectors to attach to a given job.
        :paramtype worker_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticWorkerSelectorAttachment,
          ~azure.communication.jobrouter.ConditionalWorkerSelectorAttachment,
          ~azure.communication.jobrouter.RuleEngineWorkerSelectorAttachment,
          ~azure.communication.jobrouter.PassThroughWorkerSelectorAttachment,
          ~azure.communication.jobrouter.WeightedAllocationWorkerSelectorAttachment]]]

        :return: Instance of ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.ClassificationPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace
    def update_classification_policy(
        self, classification_policy_id: str, *args: _models.ClassificationPolicy, **kwargs: Any
    ) -> _models.ClassificationPolicy:
        """Update a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :param classification_policy: An instance of Classification policy. This is a positional-only
         parameter. Please provide either this or individual keyword parameters.
        :type classification_policy: ~azure.communication.jobrouter.ClassificationPolicy

        :keyword Optional[str] name: Friendly name of this policy.

        :keyword fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.
        :paramtype fallback_queue_id: Optional[str]

        :keyword queue_selectors: The queue selectors to resolve a queue for a given job.
        :paramtype queue_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticQueueSelectorAttachment,
          ~azure.communication.jobrouter.ConditionalQueueSelectorAttachment,
          ~azure.communication.jobrouter.RuleEngineQueueSelectorAttachment,
          ~azure.communication.jobrouter.PassThroughQueueSelectorAttachment,
          ~azure.communication.jobrouter.WeightedAllocationQueueSelectorAttachment]]]

        :keyword prioritization_rule: The rule to determine a priority score for a given job.
        :paramtype prioritization_rule: Optional[Union[~azure.communication.jobrouter.StaticRouterRule,
          ~azure.communication.jobrouter.ExpressionRouterRule,
          ~azure.communication.jobrouter.FunctionRouterRule,
          ~azure.communication.jobrouter.WebhookRouterRule]]

        :keyword worker_selectors: The worker label selectors to attach to a given job.
        :paramtype worker_selectors: Optional[List[Union[~azure.communication.jobrouter.StaticWorkerSelectorAttachment,
          ~azure.communication.jobrouter.ConditionalWorkerSelectorAttachment,
          ~azure.communication.jobrouter.RuleEngineWorkerSelectorAttachment,
          ~azure.communication.jobrouter.PassThroughWorkerSelectorAttachment,
          ~azure.communication.jobrouter.WeightedAllocationWorkerSelectorAttachment]]]

        :return: Instance of ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.ClassificationPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops.py
                :start-after: [START update_classification_policy]
                :end-before: [END update_classification_policy]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to update a classification policy
        """
        if not classification_policy_id:
            raise ValueError("classification_policy_id cannot be None.")

        classification_policy = _models.ClassificationPolicy()
        if len(args) == 1:
            classification_policy = args[0]

        patch = _models.ClassificationPolicy(
            name=kwargs.pop("name", classification_policy.name),
            fallback_queue_id=kwargs.pop("fallback_queue_id", classification_policy.fallback_queue_id),
            queue_selectors=kwargs.pop("queue_selectors", classification_policy.queue_selectors),
            prioritization_rule=kwargs.pop("prioritization_rule", classification_policy.prioritization_rule),
            worker_selectors=kwargs.pop("worker_selectors", classification_policy.worker_selectors),
        )

        return super().upsert_classification_policy(id=classification_policy_id, resource=patch, **kwargs)

    # endregion ClassificationPolicy


class JobRouterClientOperationsMixin(JobRouterClientOperationsMixinGenerated):
    # region Worker

    @distributed_trace
    def create_worker(self, worker_id: str, router_worker: _models.RouterWorker, **kwargs: Any) -> _models.RouterWorker:
        """Create a new worker.

        :param str worker_id: Id of the worker.

        :param router_worker: An instance of RouterWorker.
        :type router_worker: ~azure.communication.jobrouter.RouterWorker

        :return: Instance of RouterWorker
        :rtype: ~azure.communication.jobrouter.RouterWorker
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops.py
                :start-after: [START create_worker]
                :end-before: [END create_worker]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to create a worker
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        return super().upsert_worker(worker_id=worker_id, resource=router_worker, **kwargs)

    @overload
    def update_worker(self, worker_id: str, router_worker: _models.RouterWorker, **kwargs: Any) -> _models.RouterWorker:
        """Update a router worker.

        :param str worker_id: Id of the worker.

        :param router_worker: An instance of RouterWorker. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type router_worker: ~azure.communication.jobrouter.RouterWorker

        :return: Instance of RouterWorker
        :rtype: ~azure.communication.jobrouter.RouterWorker
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    def update_worker(
        self,
        worker_id: str,
        *,
        queue_assignments: Optional[Dict[str, Union[JSON, None]]],
        total_capacity: Optional[int],
        labels: Optional[Dict[str, Union[int, float, str, bool]]],
        tags: Optional[Dict[str, Union[int, float, str, bool]]],
        channel_configurations: Optional[Dict[str, _models.ChannelConfiguration]],
        available_for_offers: Optional[bool],
        **kwargs: Any
    ) -> _models.RouterWorker:
        """Update a router worker.

        :param str worker_id: Id of the worker.

        :keyword queue_assignments: The queue(s) that this worker can receive work from.
        :paramtype queue_assignments: Optional[Dict[str, Union[~collections.abc.MutableMapping[str, Any], None]]]

        :keyword total_capacity: The total capacity score this worker has to manage multiple concurrent
         jobs.
        :paramtype total_capacity: Optional[int]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this worker.
        :paramtype tags: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword channel_configurations: The channel(s) this worker can handle and their impact on the
         workers capacity.
        :paramtype channel_configurations: Optional[Dict[str, ~azure.communication.jobrouter.ChannelConfiguration]]

        :keyword available_for_offers: A flag indicating this worker is open to receive offers or not.
        :paramtype available_for_offers: Optional[bool]

        :return: Instance of RouterWorker
        :rtype: ~azure.communication.jobrouter.RouterWorker
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace
    def update_worker(self, worker_id: str, *args: _models.RouterWorker, **kwargs: Any) -> _models.RouterWorker:
        """Update a router worker.

        :param str worker_id: Id of the worker.

        :param router_worker: An instance of RouterWorker. This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type router_worker: ~azure.communication.jobrouter.RouterWorker

        :keyword queue_assignments: The queue(s) that this worker can receive work from.
        :paramtype queue_assignments: Optional[Dict[str, Union[~collections.abc.MutableMapping[str, Any], None]]]

        :keyword total_capacity: The total capacity score this worker has to manage multiple concurrent
         jobs.
        :paramtype total_capacity: Optional[int]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[dict[str, Union[int, float, str, bool, None]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this worker.
        :paramtype tags: Optional[dict[str, Union[int, float, str, bool, None]]]

        :keyword channel_configurations: The channel(s) this worker can handle and their impact on the
         workers capacity.
        :paramtype channel_configurations: Optional[Dict[str, ~azure.communication.jobrouter.ChannelConfiguration]]

        :keyword available_for_offers: A flag indicating this worker is open to receive offers or not.
        :paramtype available_for_offers: Optional[bool]

        :return: Instance of RouterWorker
        :rtype: ~azure.communication.jobrouter.RouterWorker
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops.py
                :start-after: [START update_worker]
                :end-before: [END update_worker]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to update a worker

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops.py
                :start-after: [START register_worker]
                :end-before: [END register_worker]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to register a worker

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops.py
                :start-after: [START deregister_worker]
                :end-before: [END deregister_worker]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to de-register a worker
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        router_worker = _models.RouterWorker()
        if len(args) == 1:
            router_worker = args[0]

        patch = _models.RouterWorker(
            queue_assignments=kwargs.pop("queue_assignments", router_worker.queue_assignments),
            total_capacity=kwargs.pop("total_capacity", router_worker.total_capacity),
            labels=kwargs.pop("labels", router_worker.labels),
            tags=kwargs.pop("tags", router_worker.tags),
            channel_configurations=kwargs.pop("channel_configurations", router_worker.channel_configurations),
            available_for_offers=kwargs.pop("available_for_offers", router_worker.available_for_offers),
        )

        return super().upsert_worker(worker_id=worker_id, resource=patch, **kwargs)

    # endregion Worker

    # region Job

    @distributed_trace
    def create_job(self, job_id: str, router_job: _models.RouterJob, **kwargs: Any) -> _models.RouterJob:
        """Create a job.

        :param str job_id: Id of the job.

        :param router_job: An instance of RouterJob.
        :type router_job: ~azure.communication.jobrouter.RouterJob

        :return: Instance of RouterJob
        :rtype: ~azure.communication.jobrouter.RouterJob
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START create_job]
                :end-before: [END create_job]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to create a job
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        return super().upsert_job(id=job_id, resource=router_job, **kwargs)

    @overload
    def update_job(self, job_id: str, router_job: _models.RouterJob, **kwargs: Any) -> _models.RouterJob:
        """Update a job.

        :param str job_id: Id of the job.

        :param router_job: An instance of RouterJob.  This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type router_job: ~azure.communication.jobrouter.RouterJob

        :return: Instance of RouterJob
        :rtype: ~azure.communication.jobrouter.RouterJob
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @overload
    def update_job(
        self,
        job_id: str,
        *,
        channel_reference: Optional[str],
        channel_id: Optional[str],
        classification_policy_id: Optional[str],
        queue_id: Optional[str],
        priority: Optional[int],
        disposition_code: Optional[str],
        requested_worker_selectors: Optional[List[_models.RouterWorkerSelector]],
        labels: Optional[Dict[str, Union[int, float, str, bool, None]]],
        tags: Optional[Dict[str, Union[int, float, str, bool, None]]],
        notes: Optional[Dict[datetime, str]],
        matching_mode: Optional[_models.JobMatchingMode],
        **kwargs: Any
    ) -> _models.RouterJob:
        """Update a job.

        :param str job_id: Id of the job.

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
        :paramtype requested_worker_selectors: Optional[List[~azure.communication.jobrouter.RouterWorkerSelector]]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this job.
        :paramtype tags: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword notes: Notes attached to a job, sorted by timestamp.
        :paramtype notes: Optional[Dict[~datetime.datetime, str]]

        :keyword matching_mode: If set, determines how a job will be matched
        :paramtype matching_mode: Optional[~azure.communication.jobrouter.JobMatchingMode]


        :return: Instance of RouterJob
        :rtype: ~azure.communication.jobrouter.RouterJob
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """

    @distributed_trace
    def update_job(self, job_id: str, *args: _models.RouterJob, **kwargs: Any) -> _models.RouterJob:
        """Update a job.

        :param str job_id: Id of the job.

        :param router_job: An instance of RouterJob.  This is a positional-only parameter.
          Please provide either this or individual keyword parameters.
        :type router_job: ~azure.communication.jobrouter.RouterJob

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
        :paramtype requested_worker_selectors: Optional[List[~azure.communication.jobrouter.RouterWorkerSelector]]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this job.
        :paramtype tags: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword notes: Notes attached to a job, sorted by timestamp.
        :paramtype notes: Optional[Dict[~datetime.datetime, str]]

        :keyword matching_mode: If set, determines how a job will be matched
        :paramtype matching_mode: Optional[~azure.communication.jobrouter.JobMatchingMode]


        :return: Instance of RouterJob
        :rtype: ~azure.communication.jobrouter.RouterJob
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START update_job]
                :end-before: [END update_job]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to update a job
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        router_job = _models.RouterJob()
        if len(args) == 1:
            router_job = args[0]

        patch = _models.RouterJob(
            channel_reference=kwargs.pop("channel_reference", router_job.channel_reference),
            channel_id=kwargs.pop("channel_id", router_job.channel_id),
            classification_policy_id=kwargs.pop("classification_policy_id", router_job.classification_policy_id),
            queue_id=kwargs.pop("queue_id", router_job.queue_id),
            priority=kwargs.pop("priority", router_job.priority),
            disposition_code=kwargs.pop("disposition_code", router_job.disposition_code),
            requested_worker_selectors=kwargs.pop("requested_worker_selectors", router_job.requested_worker_selectors),
            labels=kwargs.pop("labels", router_job.labels),
            tags=kwargs.pop("tags", router_job.tags),
            notes=kwargs.pop("notes", router_job.notes),
            matching_mode=kwargs.pop("matching_mode", router_job.matching_mode),
        )

        return super().upsert_job(id=job_id, resource=patch, **kwargs)

    @distributed_trace
    def close_job(
        self,
        job_id: str,
        assignment_id: str,
        *,
        disposition_code: Optional[str] = None,
        close_at: Optional[datetime] = None,
        note: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Closes a completed job.

        :param str job_id: Id of the job.

        :param str assignment_id: The assignment within which the job is to be closed.

        :keyword disposition_code: Indicates the outcome of the job, populate this field with your own
         custom values. Default value is None.
        :paramtype disposition_code: Optional[str]

        :keyword close_at: If not provided, worker capacity is released immediately along with a
         JobClosedEvent notification. If provided, worker capacity is released along with a JobClosedEvent notification
         at a future time. Default value is None.
        :paramtype close_at: Optional[~datetime.datetime]

        :keyword note: (Optional) A note that will be appended to the jobs' Notes collection with the
         current timestamp. Default value is None.
        :paramtype note: Optional[str]

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START close_job]
                :end-before: [END close_job]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to close a job
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        if not assignment_id:
            raise ValueError("assignment_id cannot be None.")

        close_job_request = _models.CloseJobRequest(
            assignment_id=assignment_id, disposition_code=disposition_code, close_at=close_at, note=note
        )

        super().close_job(id=job_id, close_job_request=close_job_request, **kwargs)

    @distributed_trace
    def complete_job(self, job_id: str, assignment_id: str, *, note: Optional[str] = None, **kwargs: Any) -> None:
        """Completes an assigned job.

        :param str job_id: Id of the job.

        :param str assignment_id: The assignment within the job to complete.

        :keyword note: (Optional) A note that will be appended to the jobs' Notes collection with th
         current timestamp. Default value is None.
        :paramtype note: Optional[str]

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START complete_job]
                :end-before: [END complete_job]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to complete a job
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        if not assignment_id:
            raise ValueError("assignment_id cannot be None.")

        complete_job_request = _models.CompleteJobRequest(assignment_id=assignment_id, note=note)

        super().complete_job(id=job_id, complete_job_request=complete_job_request, **kwargs)

    # endregion Job


__all__: List[str] = [
    "JobRouterClientOperationsMixin",
    "JobRouterAdministrationClientOperationsMixin",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
