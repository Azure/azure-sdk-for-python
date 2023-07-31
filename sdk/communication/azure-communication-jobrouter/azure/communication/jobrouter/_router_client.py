# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
from datetime import datetime
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    overload
)
from urllib.parse import urlparse

from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged
from azure.core.credentials import AzureKeyCredential
from azure.communication.jobrouter._shared.policy import HMACCredentialsPolicy

from ._datetimeutils import _convert_str_to_datetime  # pylint:disable=protected-access
from ._generated import AzureCommunicationJobRouterService
from ._enums import (
    RouterWorkerState,
    RouterJobStatus
)
from ._models import (
    RouterQueueStatistics,
    UnassignJobResult,
    RouterJobPositionDetails,
    CancelJobRequest,
    CompleteJobRequest,
    CloseJobRequest,
    DeclineJobOfferRequest,
    RouterWorkerSelector,
    ChannelConfiguration,
    RouterWorker,
    RouterWorkerItem,
    RouterJob,
    RouterJobItem,
    JobMatchingMode,
    UnassignJobRequest,
    AcceptJobOfferResult
)

from ._router_serializer import (
    _deserialize_from_json, # pylint:disable=protected-access
    _serialize_to_json, # pylint:disable=protected-access
    _SERIALIZER, # pylint:disable=protected-access
)

from ._shared.utils import parse_connection_str
from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


class JobRouterClient(object):  # pylint:disable=too-many-public-methods,too-many-lines
    """A client to interact with the AzureCommunicationService JobRouter service.

    This client provides operations to create and update jobs, policies and workers.

    :param str endpoint:
        The endpoint of the Azure Communication resource.
    :param ~azure.core.credentials.AzureKeyCredential credential:
        The credentials with which to authenticate

    :keyword api_version: Azure Communication Job Router API version.
        Default value is "2022-07-18-preview".
        Note that overriding this default value may result in unsupported behavior.
    """

    def __init__(
            self,
            endpoint: str,
            credential: AzureKeyCredential,
            **kwargs: Any
    ) -> None:
        if not credential:
            raise ValueError("credential can not be None")

        # TokenCredential not supported at the moment
        if hasattr(credential, "get_token"):
            raise TypeError("Unsupported credential: {}. Use an AzureKeyCredential to use HMACCredentialsPolicy"
                            " for authentication".format(type(credential)))

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string") # pylint:disable=raise-missing-from

        parsed_url = urlparse(endpoint.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._authentication_policy = HMACCredentialsPolicy(endpoint, credential.key)
        self._client = AzureCommunicationJobRouterService(
            self._endpoint,
            api_version = self._api_version,
            authentication_policy = self._authentication_policy,
            sdk_moniker = SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(
            cls,
            conn_str: str,
            **kwargs: Any
    ) -> "JobRouterClient":
        """Create JobRouterClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :return: Instance of JobRouterClient.
        :rtype: ~azure.communication.jobrouter.JobRouterClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_authentication.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Authenticating a JobRouterClient from a connection_string
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, AzureKeyCredential(access_key), **kwargs)

    # region Queue

    @distributed_trace
    def get_queue_statistics(
            self,
            queue_id: str,
            **kwargs: Any
    ) -> RouterQueueStatistics:
        """Retrieves a queue's statistics.

        :param str queue_id: Id of the queue.

        :return: Instance of RouterQueueStatistics
        :rtype: ~azure.communication.jobrouter.RouterQueueStatistics
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/job_queue_crud_ops.py
                :start-after: [START get_queue_statistics]
                :end-before: [END get_queue_statistics]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to fetch queue statistics
        """
        if not queue_id:
            raise ValueError("queue_id cannot be None.")

        return self._client.job_router.get_queue_statistics(
            id = queue_id,
            # pylint:disable=protected-access,line-too-long
            cls = lambda http_response, deserialized_json_response, arg: _deserialize_from_json("RouterQueueStatistics", deserialized_json_response),
            **kwargs
        )

    # endregion Queue

    # region Worker

    @distributed_trace
    def create_worker(
            self,
            worker_id: str,
            router_worker: RouterWorker,
            **kwargs: Any
    ) -> RouterWorker:
        """ Create a new worker.

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

        return self._client.job_router.upsert_worker(
            worker_id = worker_id,
            patch = _serialize_to_json(router_worker, "RouterWorker"),  # pylint:disable=protected-access
            # pylint:disable=protected-access,line-too-long
            cls = lambda http_response, deserialized_json_response, arg: _deserialize_from_json("RouterWorker", deserialized_json_response),
            **kwargs
        )

    @overload
    def update_worker(
            self,
            worker_id: str,
            router_worker: RouterWorker,
            **kwargs: Any
    ) -> RouterWorker:
        """ Update a router worker.

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
            channel_configurations: Optional[Dict[str, ChannelConfiguration]],
            available_for_offers: Optional[bool],
            **kwargs: Any
    ) -> RouterWorker:
        """ Update a router worker.

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
    def update_worker(
            self,
            worker_id: str,
            *args: RouterWorker,
            **kwargs: Any
    ) -> RouterWorker:
        """ Update a router worker.

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

        router_worker = RouterWorker()
        if len(args) == 1:
            router_worker = args[0]

        patch = RouterWorker(
            queue_assignments = kwargs.pop('queue_assignments', router_worker.queue_assignments),
            total_capacity = kwargs.pop('total_capacity', router_worker.total_capacity),
            labels = kwargs.pop('labels', router_worker.labels),
            tags = kwargs.pop('tags', router_worker.tags),
            channel_configurations = kwargs.pop('channel_configurations', router_worker.channel_configurations),
            available_for_offers = kwargs.pop('available_for_offers', router_worker.available_for_offers)
        )

        return self._client.job_router.upsert_worker(
            worker_id = worker_id,
            patch = _serialize_to_json(patch, "RouterWorker"),  # pylint:disable=protected-access
            # pylint:disable=protected-access,line-too-long
            cls = lambda http_response, deserialized_json_response, arg: _deserialize_from_json("RouterWorker", deserialized_json_response),
            **kwargs
        )

    @distributed_trace
    def get_worker(
            self,
            worker_id: str,
            **kwargs: Any
    ) -> RouterWorker:
        """Retrieves an existing worker by Id.

        :param str worker_id: Id of the worker.

        :return: Instance of RouterWorker
        :rtype: ~azure.communication.jobrouter.RouterWorker
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops.py
                :start-after: [START get_worker]
                :end-before: [END get_worker]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to get a worker
        """
        if not worker_id:
            raise ValueError("identifier cannot be None.")

        return self._client.job_router.get_worker(
            worker_id = worker_id,
            # pylint:disable=protected-access,line-too-long
            cls = lambda http_response, deserialized_json_response, arg: _deserialize_from_json("RouterWorker", deserialized_json_response),
            **kwargs
        )

    @distributed_trace
    def list_workers(
            self,
            *,
            state: Optional[Union[str, RouterWorkerState, Literal["all"]]] = "all",
            channel_id: Optional[str] = None,
            queue_id: Optional[str] = None,
            has_capacity: Optional[bool] = None,
            results_per_page: Optional[int] = None,
            **kwargs: Any
    ) -> ItemPaged[RouterWorkerItem]:
        """Retrieves existing workers.

        :keyword state: If specified, select workers by worker status. Default value is "all".
          Accepted value(s): active, draining, inactive, all
        :paramtype state: Optional[Union[str, ~azure.communication.jobrouter.RouterWorkerState, Literal["all"]]]

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

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops.py
                :start-after: [START list_workers]
                :end-before: [END list_workers]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to retrieve workers

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops.py
                :start-after: [START list_workers_batched]
                :end-before: [END list_workers_batched]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to retrieve workers in batches
        """

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        return self._client.job_router.list_workers(
            params = params,
            state = state,
            channel_id = channel_id,
            queue_id = queue_id,
            has_capacity = has_capacity,
            # pylint:disable=protected-access
            cls = lambda deserialized_json_array: [_deserialize_from_json("RouterWorkerItem", elem) for elem in
                                                   deserialized_json_array],
            **kwargs
        )

    @distributed_trace
    def delete_worker(
            self,
            worker_id: str,
            **kwargs: Any
    ) -> None:
        """Delete a worker by Id.

        :param str worker_id: Id of the worker to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_worker_crud_ops.py
                :start-after: [START delete_worker]
                :end-before: [END delete_worker]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to delete an existing worker
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
            job_id: str,
            router_job: RouterJob,
            **kwargs: Any
    ) -> RouterJob:
        """ Create a job.

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

        return self._client.job_router.upsert_job(
            id = job_id,
            patch = _serialize_to_json(router_job, "RouterJob"),  # pylint:disable=protected-access
            # pylint:disable=protected-access,line-too-long
            cls = lambda http_response, deserialized_json_response, arg: _deserialize_from_json("RouterJob", deserialized_json_response),
            **kwargs
        )

    @overload
    def update_job(
            self,
            job_id: str,
            router_job: RouterJob,
            **kwargs: Any
    ) -> RouterJob:
        """ Update a job.

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
            requested_worker_selectors: Optional[List[RouterWorkerSelector]],
            labels: Optional[Dict[str, Union[int, float, str, bool, None]]],
            tags: Optional[Dict[str, Union[int, float, str, bool, None]]],
            notes: Optional[Dict[datetime, str]],
            matching_mode: Optional[JobMatchingMode],
            **kwargs: Any
    ) -> RouterJob:
        """ Update a job.

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
    def update_job(
            self,
            job_id: str,
            *args: RouterJob,
            **kwargs: Any
    ) -> RouterJob:
        """ Update a job.

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

        router_job = RouterJob()
        if len(args) == 1:
            router_job = args[0]

        patch = RouterJob(
            channel_reference = kwargs.pop('channel_reference', router_job.channel_reference),
            channel_id = kwargs.pop('channel_id', router_job.channel_id),
            classification_policy_id = kwargs.pop('classification_policy_id', router_job.classification_policy_id),
            queue_id = kwargs.pop('queue_id', router_job.queue_id),
            priority = kwargs.pop('priority', router_job.priority),
            disposition_code = kwargs.pop('disposition_code', router_job.disposition_code),
            requested_worker_selectors = kwargs.pop('requested_worker_selectors',
                                                    router_job.requested_worker_selectors),
            labels = kwargs.pop('labels', router_job.labels),
            tags = kwargs.pop('tags', router_job.tags),
            notes = kwargs.pop('notes', router_job.notes),
            matching_mode = kwargs.pop('matching_mode', router_job.matching_mode)
        )

        return self._client.job_router.upsert_job(
            id = job_id,
            patch = _serialize_to_json(patch, "RouterJob"),  # pylint:disable=protected-access
            # pylint:disable=protected-access,line-too-long
            cls = lambda http_response, deserialized_json_response, arg: _deserialize_from_json("RouterJob", deserialized_json_response),
            **kwargs
        )

    @distributed_trace
    def get_job(
            self,
            job_id: str,
            **kwargs: Any
    ) -> RouterJob:
        """Retrieves an existing worker by Id.

        :param str job_id: Id of the job.

        :return: Instance of RouterJob
        :rtype: ~azure.communication.jobrouter.RouterJob
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START get_job]
                :end-before: [END get_job]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to get a job
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        return self._client.job_router.get_job(
            id = job_id,
            # pylint:disable=protected-access,line-too-long
            cls = lambda http_response, deserialized_json_response, args: _deserialize_from_json("RouterJob", deserialized_json_response),
            **kwargs
        )

    @distributed_trace
    def list_jobs(
            self,
            *,
            status: Optional[Union[str, RouterJobStatus, Literal["all", "active"] ]] = "all",
            channel_id: Optional[str] = None,
            queue_id: Optional[str] = None,
            classification_policy_id: Optional[str] = None,
            scheduled_before: Optional[Union[str, datetime]] = None,
            scheduled_after: Optional[Union[str, datetime]] = None,
            results_per_page: Optional[int] = None,
            **kwargs: Any
    ) -> ItemPaged[RouterJobItem]:
        """Retrieves list of jobs based on filter parameters.

        :keyword status: If specified, filter jobs by status. Default value is "all".
            Accepted value(s): pendingClassification, queued, assigned, completed, closed, cancelled,
            classificationFailed, active, all
        :paramtype status: Optional[Union[str, ~azure.communication.jobrouter.RouterJobStatus, Literal["all","active"]]]

        :keyword channel_id: If specified, filter jobs by channel. Default value is None.
        :paramtype channel_id: Optional[str]

        :keyword queue_id: If specified, filter jobs by queue. Default value is None.
        :paramtype queue_id: Optional[str]

        :keyword classification_policy_id: If specified, filter jobs by classificationPolicy. Default value is None.
        :paramtype classification_policy_id: Optional[str]

        :keyword scheduled_before: If specified, filter on jobs that was scheduled before or
         at given timestamp. Range: (-Inf, scheduledBefore]. Default value is None.
        :paramtype scheduled_before: Optional[Union[str, ~datetime.datetime]]

        :keyword scheduled_after: If specified, filter on jobs that was scheduled at or
         after given value. Range: [scheduledAfter, +Inf). Default value is None.
        :paramtype scheduled_after: Optional[Union[str, ~datetime.datetime]]


        :keyword Optional[int] results_per_page: The maximum number of results to be returned per page.

        :return: An iterator like instance of RouterJobItem
        :rtype: ~azure.core.paging.ItemPaged[~azure.communication.jobrouter.RouterJobItem]
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START list_jobs]
                :end-before: [END list_jobs]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to retrieve jobs

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START list_jobs_batched]
                :end-before: [END list_jobs_batched]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to retrieve jobs in batches

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START list_scheduled_jobs]
                :end-before: [END list_scheduled_jobs]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to retrieve scheduled jobs
        """

        params = {}
        if results_per_page is not None:
            params['maxpagesize'] = _SERIALIZER.query("maxpagesize", results_per_page, 'int')

        if scheduled_before is not None and isinstance(scheduled_before, str):
            scheduled_before = _convert_str_to_datetime(scheduled_before)

        if scheduled_after is not None and isinstance(scheduled_after, str):
            scheduled_after = _convert_str_to_datetime(scheduled_after)

        return self._client.job_router.list_jobs(
            params = params,
            status = status,
            channel_id = channel_id,
            queue_id = queue_id,
            classification_policy_id = classification_policy_id,
            scheduled_before = scheduled_before,
            scheduled_after = scheduled_after,
            # pylint:disable=protected-access
            cls = lambda deserialized_json_array: [_deserialize_from_json("RouterJobItem", elem) for elem in
                                                   deserialized_json_array],
            **kwargs
        )

    @distributed_trace
    def delete_job(
            self,
            job_id: str,
            **kwargs: Any
    ) -> None:
        """Delete a job by Id.

        :param str job_id: Id of the job to delete.
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START delete_job]
                :end-before: [END delete_job]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to delete a job
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
            job_id: str,
            **kwargs: Any
    ) -> RouterJobPositionDetails:
        """Gets a job's position details.

        :param str job_id: Id of the job.

        :return: Instance of RouterJobPositionDetails
        :rtype: ~azure.communication.jobrouter.RouterJobPositionDetails
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START get_job_position]
                :end-before: [END get_job_position]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to get a job position in queue
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        return self._client.job_router.get_in_queue_position(
            id = job_id,
            # pylint:disable=protected-access,line-too-long
            cls = lambda http_response, deserialized_json_response, args: _deserialize_from_json("RouterJobPositionDetails", deserialized_json_response),
            **kwargs
        )

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

        close_job_request = CloseJobRequest(
            assignment_id = assignment_id,
            disposition_code = disposition_code,
            close_at = close_at,
            note = note
        )

        self._client.job_router.close_job_action(
            id = job_id,
            # pylint:disable=protected-access
            close_job_request = _serialize_to_json(close_job_request, "CloseJobRequest"),
            **kwargs
        )

    @distributed_trace
    def complete_job(
            self,
            job_id: str,
            assignment_id: str,
            *,
            note: Optional[str] = None,
            **kwargs: Any
    ) -> None:
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

        complete_job_request = CompleteJobRequest(
            assignment_id = assignment_id,
            note = note
        )

        self._client.job_router.complete_job_action(
            id = job_id,
            # pylint:disable=protected-access
            complete_job_request = _serialize_to_json(complete_job_request, "CompleteJobRequest"),
            **kwargs
        )

    @distributed_trace
    def cancel_job(
            self,
            job_id: str,
            *,
            disposition_code: Optional[str] = None,
            note: Optional[str] = None,
            **kwargs: Any
    ) -> None:
        """Submits request to cancel an existing job by Id while supplying free-form cancellation reason.

        :param str job_id: Id of the job.

        :keyword note: A note that will be appended to the jobs' Notes collection with the
         current timestamp. Default value is None.
        :paramtype note: Optional[str]

        :keyword disposition_code: Indicates the outcome of the job, populate this field with your own
         custom values.
         If not provided, default value of "Cancelled" is set. Default value is None.
        :paramtype disposition_code: Optional[str]

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START cancel_job]
                :end-before: [END cancel_job]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to cancel a job
        """

        if not job_id:
            raise ValueError("job_id cannot be None.")

        cancel_job_request = CancelJobRequest(
            note = note,
            disposition_code = disposition_code
        )

        self._client.job_router.cancel_job_action(
            id = job_id,
            # pylint:disable=protected-access
            cancel_job_request = _serialize_to_json(cancel_job_request, "CancelJobRequest"),
            **kwargs
        )

    @distributed_trace
    def reclassify_job(
            self,
            job_id: str,
            **kwargs: Any
    ) -> None:
        """Reclassify a job.

        :param str job_id: Id of the job.

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START reclassify_job]
                :end-before: [END reclassify_job]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to re-classify a job
        """
        if not job_id:
            raise ValueError("identifier cannot be None.")

        self._client.job_router.reclassify_job_action(
            id = job_id,
            **kwargs
        )

    @distributed_trace
    def unassign_job(
            self,
            job_id: str,
            assignment_id: str,
            *,
            suspend_matching: Optional[bool] = None,
            **kwargs: Any
    ) -> UnassignJobResult:
        """Unassign a job.

        :param str job_id: Id of the job.
        :param str assignment_id: Id of the assignment.

        :keyword suspend_matching: If set to true, then the job is not queued for
         re-matching with a worker.
        :paramtype suspend_matching: Optional[bool]

        :return: Instance of UnassignJobResult
        :rtype: ~azure.communication.jobrouter.UnassignJobResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START unassign_job]
                :end-before: [END unassign_job]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to unassign a job
        """
        if not job_id:
            raise ValueError("job_id cannot be None.")

        if not assignment_id:
            raise ValueError("assignment_id cannot be None.")

        unassign_job_request = UnassignJobRequest(
            suspend_matching = suspend_matching
        )

        return self._client.job_router.unassign_job_action(
            id = job_id,
            assignment_id = assignment_id,
            unassign_job_request = _serialize_to_json(unassign_job_request, "UnassignJobRequest"),  # pylint:disable=protected-access,
            # pylint:disable=protected-access,line-too-long
            cls = lambda http_response, deserialized_json_response, arg: _deserialize_from_json("UnassignJobResult", deserialized_json_response),
            **kwargs
        )

    # endregion Job

    # region Offer

    @distributed_trace
    def accept_job_offer(
            self,
            worker_id: str,
            offer_id: str,
            **kwargs: Any
    ) -> AcceptJobOfferResult:
        """Accepts an offer to work on a job and returns a 409/Conflict if another agent accepted the job
        already.

        :param worker_id: Id of the worker.
        :type worker_id: str
        :param offer_id: Id of the offer.
        :type offer_id: str

        :return: Instance of AcceptJobOfferResult
        :rtype: ~azure.communication.jobrouter.AcceptJobOfferResult
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START accept_job_offer]
                :end-before: [END accept_job_offer]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to accept a job offer
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        if not offer_id:
            raise ValueError("offer_id cannot be None.")

        return self._client.job_router.accept_job_action(
            worker_id = worker_id,
            offer_id = offer_id,
            # pylint:disable=protected-access,line-too-long
            cls = lambda http_response, deserialized_json_response, arg: _deserialize_from_json("AcceptJobOfferResult", deserialized_json_response),
            **kwargs
        )

    @distributed_trace
    def decline_job_offer(
            self,
            worker_id: str,
            offer_id: str,
            *,
            retry_offer_at: Optional[datetime] = None,
            **kwargs: Any
    ) -> None:
        """Declines an offer to work on a job.

        :param worker_id: Id of the worker.
        :type worker_id: str
        :param offer_id: Id of the offer.
        :type offer_id: str

        :keyword retry_offer_at: If the retry_offer_at is not provided, then this job will not be re-offered to the
          worker who declined this job unless the worker is de-registered and re-registered.  If a retry_offer_at is
          provided, then the job will be re-matched to eligible workers after the reoffer time. The worker that declined
          the job will also be eligible for the job at that time.
        :paramtype retry_offer_at: Optional[~datetime.datetime]

        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError

        .. admonition:: Example:

            .. literalinclude:: ../samples/router_job_crud_ops.py
                :start-after: [START decline_job_offer]
                :end-before: [END decline_job_offer]
                :language: python
                :dedent: 8
                :caption: Use a JobRouterClient to decline a job offer
        """
        if not worker_id:
            raise ValueError("worker_id cannot be None.")

        if not offer_id:
            raise ValueError("offer_id cannot be None.")

        decline_job_offer_request = DeclineJobOfferRequest(
            retry_offer_at = retry_offer_at
        )

        self._client.job_router.decline_job_action(
            worker_id = worker_id,
            offer_id = offer_id,
            # pylint:disable=protected-access
            decline_job_offer_request = _serialize_to_json(decline_job_offer_request, "DeclineJobOfferRequest"),
            **kwargs
        )

    # endregion Offer

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "JobRouterClient":
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args) -> None:
        self._client.__exit__(*args)  # pylint:disable=no-member
