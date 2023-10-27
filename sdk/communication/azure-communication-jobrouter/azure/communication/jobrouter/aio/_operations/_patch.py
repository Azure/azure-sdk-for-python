# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
import datetime
from typing import (
    List,
    Any,
    Optional,
    Dict,
    Union,
    AsyncIterable,
    overload
)

from azure.core import MatchConditions
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ... import models as _models
from ._operations import (
    JobRouterClientOperationsMixin as JobRouterClientOperationsMixinGenerated,
    JobRouterAdministrationClientOperationsMixin as JobRouterAdministrationClientOperationsMixinGenerated,
)
from ..._model_base import _deserialize_datetime as _convert_str_to_datetime  # pylint:disable=protected-access

if sys.version_info >= (3, 8):
    from typing import Literal  # pylint: disable=no-name-in-module, ungrouped-imports
else:
    from typing_extensions import Literal  # type: ignore  # pylint: disable=ungrouped-imports


class JobRouterAdministrationClientOperationsMixin(
    JobRouterAdministrationClientOperationsMixinGenerated
):  # pylint:disable=too-many-lines,line-too-long,name-too-long,arguments-differ,unused-argument
    # region ExceptionPolicy
    @overload
    async def upsert_exception_policy(  # pylint: disable=arguments-differ,unused-argument
            self,
            exception_policy_id: str,
            *,
            exception_rules: Optional[List[_models.ExceptionRule]],
            name: Optional[str],
            if_unmodified_since: Optional[datetime.datetime] = None,
            etag: Optional[str] = None,
            match_condition: Optional[MatchConditions] = None,
            **kwargs: Any
    ) -> _models.ExceptionPolicy:
        """Update an exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :keyword exception_rules: (Optional) A collection of exception rules on the exception
          policy.
        :paramtype exception_rules: Optional[Dict[str, ~azure.communication.jobrouter.models.ExceptionRule]]

        :keyword Optional[str] name: The name of this policy.

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.models.ExceptionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError


        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops.py
                :start-after: [START update_exception_policy]
                :end-before: [END update_exception_policy]
                :language: python
                :dedent: 8
                :caption: Using a JobRouterAdministrationClient to update an exception policy
        """

    async def upsert_exception_policy(
        self,
        exception_policy_id: str,
        *args: _models.ExceptionPolicy,
        **kwargs: Any
    ) -> _models.ExceptionPolicy:
        """Update an exception policy.

        :param str exception_policy_id: Id of the exception policy.

        :keyword exception_rules: (Optional) A collection of exception rules on the exception
          policy.
        :paramtype exception_rules: Optional[Dict[str, ~azure.communication.jobrouter.models.ExceptionRule]]

        :keyword Optional[str] name: The name of this policy.

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of ExceptionPolicy
        :rtype: ~azure.communication.jobrouter.models.ExceptionPolicy
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

        if_unmodified_since = kwargs.pop('if_unmodified_since', None)
        etag = kwargs.pop('etag', None)
        match_condition = kwargs.pop('match_condition', None)

        return await super().upsert_exception_policy(
            exception_policy_id=exception_policy_id,
            resource=patch,
            if_unmodified_since=if_unmodified_since,
            etag=etag,
            match_condition=match_condition,
            **kwargs
        )

    @distributed_trace
    def list_exception_policies(
        self, *, results_per_page: Optional[int] = None, **kwargs: Any
    ) -> AsyncIterable[_models.ExceptionPolicy]:
        """Retrieves existing exception policies.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of ExceptionPolicyItem
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.models.ExceptionPolicyItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops_async.py
                :start-after: [START list_exception_policies_async]
                :end-before: [END list_exception_policies_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to list exception policies

        .. admonition:: Example:

            .. literalinclude:: ../samples/exception_policy_crud_ops_async.py
                :start-after: [START list_exception_policies_batched_async]
                :end-before: [END list_exception_policies_batched_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to list exception policies in batches
        """
        return super().list_exception_policies(maxpagesize=results_per_page, **kwargs)

    # endregion ExceptionPolicy

    # region DistributionPolicy
    @overload
    async def upsert_distribution_policy(  # pylint: disable=arguments-differ,unused-argument
            self,
            distribution_policy_id: str,
            *,
            name: Optional[str],
            offer_expires_after_seconds: Optional[float],
            mode: Optional[Union[_models.BestWorkerMode, _models.LongestIdleMode, _models.RoundRobinMode]],
            if_unmodified_since: Optional[datetime.datetime] = None,
            etag: Optional[str] = None,
            match_condition: Optional[MatchConditions] = None,
            **kwargs: Any
    ) -> _models.DistributionPolicy:
        """Update a distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :keyword Optional[float] offer_expires_after_seconds: The expiry time of any offers created under this policy
          will be governed by the offer time to live.

        :keyword mode: Specified distribution mode
        :paramtype mode: Optional[Union[~azure.communication.jobrouter.models.BestWorkerMode,
            ~azure.communication.jobrouter.models.LongestIdleMode,
            ~azure.communication.jobrouter.models.RoundRobinMode]]

        :keyword Optional[str] name: The name of this policy.

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of DistributionPolicy
        :rtype: ~azure.communication.jobrouter.models.DistributionPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops.py
                :start-after: [START update_distribution_policy]
                :end-before: [END update_distribution_policy]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to update a distribution policy
        """

    async def upsert_distribution_policy(
        self,
        distribution_policy_id: str,
        *args: _models.DistributionPolicy,
        **kwargs: Any
    ) -> _models.DistributionPolicy:
        """Update a distribution policy.

        :param str distribution_policy_id: Id of the distribution policy.

        :keyword Optional[float] offer_expires_after_seconds: The expiry time of any offers created under this policy
          will be governed by the offer time to live.

        :keyword mode: Specified distribution mode
        :paramtype mode: Optional[Union[~azure.communication.jobrouter.models.BestWorkerMode,
            ~azure.communication.jobrouter.models.LongestIdleMode,
            ~azure.communication.jobrouter.models.RoundRobinMode]]

        :keyword Optional[str] name: The name of this policy.

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of DistributionPolicy
        :rtype: ~azure.communication.jobrouter.models.DistributionPolicy
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

        if_unmodified_since = kwargs.pop('if_unmodified_since', None)
        etag = kwargs.pop('etag', None)
        match_condition = kwargs.pop('match_condition', None)

        return await super().upsert_distribution_policy(
            distribution_policy_id=distribution_policy_id,
            resource=patch,
            if_unmodified_since=if_unmodified_since,
            etag=etag,
            match_condition=match_condition,
            **kwargs
        )

    @distributed_trace
    def list_distribution_policies(
        self, *, results_per_page: Optional[int] = None, **kwargs: Any
    ) -> AsyncIterable[_models.DistributionPolicy]:
        """Retrieves existing distribution policies.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of DistributionPolicy
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.models.DistributionPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops_async.py
                :start-after: [START list_distribution_policies_async]
                :end-before: [END list_distribution_policies_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to list distribution policies

        .. admonition:: Example:

            .. literalinclude:: ../samples/distribution_policy_crud_ops_async.py
                :start-after: [START list_distribution_policies_batched_async]
                :end-before: [END list_distribution_policies_batched_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to list distribution policies in batches
        """
        return super().list_distribution_policies(maxpagesize=results_per_page, **kwargs)

    # endregion DistributionPolicy

    # region Queue
    @overload
    async def upsert_queue(  # pylint: disable=arguments-differ,unused-argument
            self,
            queue_id: str,
            *,
            distribution_policy_id: Optional[str],
            name: Optional[str],
            labels: Optional[Dict[str, Union[int, float, str, bool]]],
            exception_policy_id: Optional[str],
            if_unmodified_since: Optional[datetime.datetime] = None,
            etag: Optional[str] = None,
            match_condition: Optional[MatchConditions] = None,
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

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of RouterQueue
        :rtype: ~azure.communication.jobrouter.models.RouterQueue
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops.py
                :start-after: [START update_queue]
                :end-before: [END update_queue]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to update a queue
        """
    async def upsert_queue(
        self,
        queue_id: str,
        *args: _models.RouterQueue,
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

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of RouterQueue
        :rtype: ~azure.communication.jobrouter.models.RouterQueue
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

        if_unmodified_since = kwargs.pop('if_unmodified_since', None)
        etag = kwargs.pop('etag', None)
        match_condition = kwargs.pop('match_condition', None)

        return await super().upsert_queue(
            queue_id=queue_id,
            resource=patch,
            if_unmodified_since=if_unmodified_since,
            etag=etag,
            match_condition=match_condition,
            **kwargs
        )

    @distributed_trace
    def list_queues(
        self, *, results_per_page: Optional[int] = None, **kwargs: Any
    ) -> AsyncIterable[_models.RouterQueue]:
        """Retrieves existing queues.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of RouterQueue
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.models.RouterQueue]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops_async.py
                :start-after: [START list_queues_async]
                :end-before: [END list_queues_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to list queues

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops_async.py
                :start-after: [START list_queues_batched_async]
                :end-before: [END list_queues_batched_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to list queues in batches
        """

        return super().list_queues(maxpagesize=results_per_page, **kwargs)

    # endregion Queue

    # region ClassificationPolicy
    @overload
    async def upsert_classification_policy(  # pylint: disable=arguments-differ,unused-argument
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
            if_unmodified_since: Optional[datetime.datetime] = None,
            etag: Optional[str] = None,
            match_condition: Optional[MatchConditions] = None,
            **kwargs: Any
    ) -> _models.ClassificationPolicy:
        """Update a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :keyword Optional[str] name: Friendly name of this policy.

        :keyword fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.
        :paramtype fallback_queue_id: Optional[str]

        :keyword queue_selectors: The queue selectors to resolve a queue for a given job.
        :paramtype queue_selectors: Optional[List[Union[
          ~azure.communication.jobrouter.models.StaticQueueSelectorAttachment,
          ~azure.communication.jobrouter.models.ConditionalQueueSelectorAttachment,
          ~azure.communication.jobrouter.models.RuleEngineQueueSelectorAttachment,
          ~azure.communication.jobrouter.models.PassThroughQueueSelectorAttachment,
          ~azure.communication.jobrouter.models.WeightedAllocationQueueSelectorAttachment]]]

        :keyword prioritization_rule: The rule to determine a priority score for a given job.
        :paramtype prioritization_rule: Optional[Union[~azure.communication.jobrouter.models.StaticRouterRule,
          ~azure.communication.jobrouter.models.ExpressionRouterRule,
          ~azure.communication.jobrouter.models.FunctionRouterRule,
          ~azure.communication.jobrouter.models.WebhookRouterRule]]

        :keyword worker_selectors: The worker label selectors to attach to a given job.
        :paramtype worker_selectors: Optional[List[Union[~azure.communication.jobrouter.models.StaticWorkerSelectorAttachment,
          ~azure.communication.jobrouter.models.ConditionalWorkerSelectorAttachment,
          ~azure.communication.jobrouter.models.RuleEngineWorkerSelectorAttachment,
          ~azure.communication.jobrouter.models.PassThroughWorkerSelectorAttachment,
          ~azure.communication.jobrouter.models.WeightedAllocationWorkerSelectorAttachment]]]

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.models.ClassificationPolicy
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops.py
                :start-after: [START update_classification_policy]
                :end-before: [END update_classification_policy]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to update a classification policy
        """
    async def upsert_classification_policy(
        self,
        classification_policy_id: str,
        *args: _models.ClassificationPolicy,
        **kwargs: Any
    ) -> _models.ClassificationPolicy:
        """Update a classification policy

        :param str classification_policy_id: Id of the classification policy.

        :keyword Optional[str] name: Friendly name of this policy.

        :keyword fallback_queue_id: The fallback queue to select if the queue selector doesn't find a match.
        :paramtype fallback_queue_id: Optional[str]

        :keyword queue_selectors: The queue selectors to resolve a queue for a given job.
        :paramtype queue_selectors: Optional[List[Union[
          ~azure.communication.jobrouter.models.StaticQueueSelectorAttachment,
          ~azure.communication.jobrouter.models.ConditionalQueueSelectorAttachment,
          ~azure.communication.jobrouter.models.RuleEngineQueueSelectorAttachment,
          ~azure.communication.jobrouter.models.PassThroughQueueSelectorAttachment,
          ~azure.communication.jobrouter.models.WeightedAllocationQueueSelectorAttachment]]]

        :keyword prioritization_rule: The rule to determine a priority score for a given job.
        :paramtype prioritization_rule: Optional[Union[~azure.communication.jobrouter.models.StaticRouterRule,
          ~azure.communication.jobrouter.models.ExpressionRouterRule,
          ~azure.communication.jobrouter.models.FunctionRouterRule,
          ~azure.communication.jobrouter.models.WebhookRouterRule]]

        :keyword worker_selectors: The worker label selectors to attach to a given job.
        :paramtype worker_selectors: Optional[List[Union[~azure.communication.jobrouter.models.StaticWorkerSelectorAttachment,
          ~azure.communication.jobrouter.models.ConditionalWorkerSelectorAttachment,
          ~azure.communication.jobrouter.models.RuleEngineWorkerSelectorAttachment,
          ~azure.communication.jobrouter.models.PassThroughWorkerSelectorAttachment,
          ~azure.communication.jobrouter.models.WeightedAllocationWorkerSelectorAttachment]]]

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of ClassificationPolicy
        :rtype: ~azure.communication.jobrouter.models.ClassificationPolicy
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
            queue_selector_attachments=kwargs.pop(
                "queue_selector_attachments", classification_policy.queue_selector_attachments
            ),
            prioritization_rule=kwargs.pop("prioritization_rule", classification_policy.prioritization_rule),
            worker_selector_attachments=kwargs.pop(
                "worker_selector_attachments", classification_policy.worker_selector_attachments
            ),
        )

        if_unmodified_since = kwargs.pop('if_unmodified_since', None)
        etag = kwargs.pop('etag', None)
        match_condition = kwargs.pop('match_condition', None)

        return await super().upsert_classification_policy(
            classification_policy_id=classification_policy_id,
            resource=patch,
            if_unmodified_since=if_unmodified_since,
            etag=etag,
            match_condition=match_condition,
            **kwargs
        )

    @distributed_trace
    def list_classification_policies(
        self, *, results_per_page: Optional[int] = None, **kwargs: Any
    ) -> AsyncIterable[_models.ClassificationPolicy]:
        """Retrieves existing classification policies.

        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of ClassificationPolicy
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.models.ClassificationPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops_async.py
                :start-after: [START list_classification_policies_async]
                :end-before: [END list_classification_policies_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to list classification policies

        .. admonition:: Example:

            .. literalinclude:: ../samples/classification_policy_crud_ops_async.py
                :start-after: [START list_classification_policies_batched_async]
                :end-before: [END list_classification_policies_batched_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterAdministrationClient to list classification policies in batches
        """

        return super().list_classification_policies(maxpagesize=results_per_page, **kwargs)

    # endregion ClassificationPolicy


class JobRouterClientOperationsMixin(JobRouterClientOperationsMixinGenerated):
    # region Worker
    @overload
    async def upsert_worker(  # pylint: disable=arguments-differ,unused-argument
            self,
            worker_id: str,
            *,
            queues: Optional[List[str]],
            capacity: Optional[int],
            labels: Optional[Dict[str, Union[int, float, str, bool]]],
            tags: Optional[Dict[str, Union[int, float, str, bool]]],
            channels: Optional[List[_models.RouterChannel]],
            available_for_offers: Optional[bool],
            if_unmodified_since: Optional[datetime.datetime] = None,
            etag: Optional[str] = None,
            match_condition: Optional[MatchConditions] = None,
            **kwargs: Any
    ) -> _models.RouterWorker:
        """Update a router worker.

        :param str worker_id: Id of the worker.

        :keyword queues: The queue(s) that this worker can receive work from.
        :paramtype queues: Optional[List[str]]

        :keyword capacity: The total capacity score this worker has to manage multiple concurrent
         jobs.
        :paramtype capacity: Optional[int]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this worker.
        :paramtype tags: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword channels: The channel(s) this worker can handle and their impact on the
         workers capacity.
        :paramtype channels: Optional[List[~azure.communication.jobrouter.models.RouterChannel]]

        :keyword available_for_offers: A flag indicating this worker is open to receive offers or not.
        :paramtype available_for_offers: Optional[bool]

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of RouterWorker
        :rtype: ~azure.communication.jobrouter.models.RouterWorker
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
    async def upsert_worker(
        self,
        worker_id: str,
        *args: _models.RouterWorker,
        **kwargs: Any
    ) -> _models.RouterWorker:
        """Update a router worker.

        :param str worker_id: Id of the worker.

        :keyword queues: The queue(s) that this worker can receive work from.
        :paramtype queues: Optional[List[str]]

        :keyword capacity: The total capacity score this worker has to manage multiple concurrent
         jobs.
        :paramtype capacity: Optional[int]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this worker.
        :paramtype tags: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword channels: The channel(s) this worker can handle and their impact on the
         workers capacity.
        :paramtype channels: Optional[List[~azure.communication.jobrouter.models.RouterChannel]]

        :keyword available_for_offers: A flag indicating this worker is open to receive offers or not.
        :paramtype available_for_offers: Optional[bool]

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of RouterWorker
        :rtype: ~azure.communication.jobrouter.models.RouterWorker
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
            queues=kwargs.pop("queues", router_worker.queues),
            capacity=kwargs.pop("capacity", router_worker.capacity),
            labels=kwargs.pop("labels", router_worker.labels),
            tags=kwargs.pop("tags", router_worker.tags),
            channels=kwargs.pop("channels", router_worker.channels),
            available_for_offers=kwargs.pop("available_for_offers", router_worker.available_for_offers),
        )

        if_unmodified_since = kwargs.pop('if_unmodified_since', None)
        etag = kwargs.pop('etag', None)
        match_condition = kwargs.pop('match_condition', None)

        return await super().upsert_worker(
            worker_id=worker_id,
            resource=patch,
            if_unmodified_since=if_unmodified_since,
            etag=etag,
            match_condition=match_condition,
            **kwargs
        )

    @distributed_trace
    def list_workers(
        self,
        *,
        state: Optional[Union[str, _models.RouterWorkerState, Literal["all"]]] = "all",
        channel_id: Optional[str] = None,
        queue_id: Optional[str] = None,
        has_capacity: Optional[bool] = None,
        results_per_page: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterable[_models.RouterWorker]:
        """Retrieves existing workers.

        :keyword state: If specified, select workers by worker status. Default value is "all".
          Accepted value(s): active, draining, inactive, all
        :paramtype state: Optional[Union[str, ~azure.communication.jobrouter.models.RouterWorkerState, Literal["all"]]]

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

        :return: An iterator like instance of RouterWorker
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.models.RouterWorker]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops_async.py
                :start-after: [START list_workers_async]
                :end-before: [END list_workers_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to retrieve workers

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops_async.py
                :start-after: [START list_workers_batched_async]
                :end-before: [END list_workers_batched_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to retrieve workers in batches
        """
        return super().list_workers(
            maxpagesize=results_per_page,
            state=state,
            channel_id=channel_id,
            queue_id=queue_id,
            has_capacity=has_capacity,
            **kwargs
        )

    # endregion Worker

    # region Job
    @overload
    async def upsert_job(  # pylint: disable=arguments-differ,unused-argument
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
            notes: Optional[Dict[datetime.datetime, str]],
            matching_mode: Optional[_models.JobMatchingMode],
            if_unmodified_since: Optional[datetime.datetime] = None,
            etag: Optional[str] = None,
            match_condition: Optional[MatchConditions] = None,
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
        :paramtype requested_worker_selectors: Optional[List[
          ~azure.communication.jobrouter.models.RouterWorkerSelector]]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this job.
        :paramtype tags: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword notes: Notes attached to a job, sorted by timestamp.
        :paramtype notes: Optional[Dict[~datetime.datetime, str]]

        :keyword matching_mode: If set, determines how a job will be matched
        :paramtype matching_mode: Optional[~azure.communication.jobrouter.models.JobMatchingMode]

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of RouterJob
        :rtype: ~azure.communication.jobrouter.models.RouterJob
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START update_job]
                :end-before: [END update_job]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to update a job
        """
    async def upsert_job(
        self,
        job_id: str,
        *args: _models.RouterJob,
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
        :paramtype requested_worker_selectors: Optional[List[
          ~azure.communication.jobrouter.models.RouterWorkerSelector]]

        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword tags: A set of tags. A set of non-identifying attributes attached to this job.
        :paramtype tags: Optional[Dict[str, Union[int, float, str, bool, None]]]

        :keyword notes: Notes attached to a job, sorted by timestamp.
        :paramtype notes: Optional[Dict[~datetime.datetime, str]]

        :keyword matching_mode: If set, determines how a job will be matched
        :paramtype matching_mode: Optional[~azure.communication.jobrouter.models.JobMatchingMode]

        :keyword if_unmodified_since: The request should only proceed if the entity was not modified
         after this time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions

        :return: Instance of RouterJob
        :rtype: ~azure.communication.jobrouter.models.RouterJob
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

        if_unmodified_since = kwargs.pop('if_unmodified_since', None)
        etag = kwargs.pop('etag', None)
        match_condition = kwargs.pop('match_condition', None)

        return await super().upsert_job(
            job_id=job_id,
            resource=patch,
            if_unmodified_since=if_unmodified_since,
            etag=etag,
            match_condition=match_condition,
            **kwargs
        )

    @distributed_trace
    def list_jobs(
        self,
        *,
        status: Optional[Union[str, _models.RouterJobStatus, Literal["all", "active"]]] = "all",
        channel_id: Optional[str] = None,
        queue_id: Optional[str] = None,
        classification_policy_id: Optional[str] = None,
        scheduled_before: Optional[Union[str, datetime.datetime]] = None,
        scheduled_after: Optional[Union[str, datetime.datetime]] = None,
        results_per_page: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterable[_models.RouterJob]:
        """Retrieves list of jobs based on filter parameters.

        :keyword status: If specified, filter jobs by status. Default value is "all".
            Accepted value(s): pendingClassification, queued, assigned, completed, closed, cancelled,
            classificationFailed, active, all
        :paramtype status: Optional[Union[
          str, ~azure.communication.jobrouter.models.RouterJobStatus, Literal["all","active"]]]

        :keyword channel_id: If specified, filter jobs by channel. Default value is None.
        :paramtype channel_id: Optional[str]

        :keyword queue_id: If specified, filter jobs by queue. Default value is None.
        :paramtype queue_id: Optional[str]

        :keyword classification_policy_id: If specified, filter jobs by classificationPolicy. Default value is None.
        :paramtype classification_policy_id: Optional[str]

        :keyword scheduled_before: If specified, filter on jobs that was scheduled before or
         at given timestamp. Range: (-Inf, scheduledBefore]. Default value is None.
        :paramtype scheduled_before: Optional[~datetime.datetime]

        :keyword scheduled_after: If specified, filter on jobs that was scheduled at or
         after given value. Range: [scheduledAfter, +Inf). Default value is None.
        :paramtype scheduled_after: Optional[~datetime.datetime]


        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of RouterJob
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.communication.jobrouter.models.RouterJob]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START list_jobs_async]
                :end-before: [END list_jobs_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to retrieve jobs

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START list_jobs_batched_async]
                :end-before: [END list_jobs_batched_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to retrieve jobs in batches

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START list_scheduled_jobs_async]
                :end-before: [END list_scheduled_jobs_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to retrieve scheduled jobs
        """
        if scheduled_before is not None and isinstance(scheduled_before, str):
            scheduled_before = _convert_str_to_datetime(scheduled_before)

        if scheduled_after is not None and isinstance(scheduled_after, str):
            scheduled_after = _convert_str_to_datetime(scheduled_after)

        return super().list_jobs(
            maxpagesize=results_per_page,
            status=status,
            channel_id=channel_id,
            queue_id=queue_id,
            classification_policy_id=classification_policy_id,
            scheduled_before=scheduled_before,
            scheduled_after=scheduled_after,
            **kwargs
        )

    @distributed_trace_async
    async def reclassify_job(self, job_id: str, **kwargs: Any) -> None:  # pylint: disable=arguments-differ
        """Reclassify a job.

        :param str job_id: Id of the job.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops_async.py
                :start-after: [START reclassify_job_async]
                :end-before: [END reclassify_job_async]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to re-classify a job
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        await super()._reclassify_job(job_id=job_id, reclassify_job_options={}, **kwargs)

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
