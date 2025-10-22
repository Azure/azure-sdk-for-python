# pylint: disable=too-many-lines, C4763
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio
import datetime
import collections
import logging
from typing import Any, cast, Callable, Deque, Dict, AsyncIterator, List, Iterable, Optional, TypeVar

from azure.batch import models as _models
from azure.core import MatchConditions
from azure.core.exceptions import (
    HttpResponseError,
)
from azure.core.polling import AsyncLROPoller
from azure.core.rest import HttpResponse, HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline import PipelineResponse

from ._polling_async import (
    DeallocateNodePollingMethodAsync,
    DeleteCertificatePollingMethodAsync,
    DeleteJobPollingMethodAsync,
    DeleteJobSchedulePollingMethodAsync,
    DeletePoolPollingMethodAsync,
    DisableJobPollingMethodAsync,
    EnableJobPollingMethodAsync,
    RebootNodePollingMethodAsync,
    ReimageNodePollingMethodAsync,
    RemoveNodePollingMethodAsync,
    ResizePoolPollingMethodAsync,
    StartNodePollingMethodAsync,
    StopPoolResizePollingMethodAsync,
    TerminateJobPollingMethodAsync,
    TerminateJobSchedulePollingMethodAsync,
)
from ._operations import (
    _BatchClientOperationsMixin as BatchClientOperationsMixinGenerated,
)


T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

MAX_TASKS_PER_REQUEST = 100
_LOGGER = logging.getLogger(__name__)

__all__: List[str] = [
    "BatchClientOperationsMixin",
]  # Add all objects you want publicly available to users at this package level


class BatchClientOperationsMixin(BatchClientOperationsMixinGenerated):
    """Customize generated code"""

    @distributed_trace
    async def begin_delete_job(
        self,
        job_id: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        force: Optional[bool] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Deletes a Job with Long Running Operation support.

        Deleting a Job also deletes all Tasks that are part of that Job, and all Job
        statistics. This also overrides the retention period for Task data; that is, if
        the Job contains Tasks which are still retained on Compute Nodes, the Batch
        services deletes those Tasks' working directories and all their contents.  When
        a Delete Job request is received, the Batch service sets the Job to the
        deleting state. All update operations on a Job that is in deleting state will
        fail with status code 409 (Conflict), with additional information indicating
        that the Job is being deleted.

        :param job_id: The ID of the Job to delete. Required.
        :type job_id: str
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword force: If true, the server will delete the Job even if the corresponding nodes have
         not fully processed the deletion. The default value is false. Default value is None.
        :paramtype force: bool
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: An LROPoller that can be used to wait for the job deletion to complete
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        # cast otherwise mypy complains about incompatible return type
        pipeline_response = cast(
            PipelineResponse,
            await self._delete_job_internal(
                job_id,
                timeout=timeout,
                ocpdate=ocpdate,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                force=force,
                etag=etag,
                match_condition=match_condition,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = DeleteJobPollingMethodAsync(self, pipeline_response, None, job_id, polling_interval)
        # redundant but needed to fix pylint errors in the polling method code
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_disable_job(
        self,
        job_id: str,
        disable_options: _models.BatchJobDisableOptions,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Disables a Job with Long Running Operation support.

        The Batch Service immediately moves the Job to the disabling state. Batch then
        uses the disableTasks parameter to determine what to do with the currently
        running Tasks of the Job. The Job remains in the disabling state until the
        disable operation is completed and all Tasks have been dealt with according to
        the disableTasks option; the Job then moves to the disabled state. No new Tasks
        are started under the Job until it moves back to active state. If you try to
        disable a Job that is in any state other than active, disabling, or disabled,
        the request fails with status code 409.

        :param job_id: The ID of the Job to disable. Required.
        :type job_id: str
        :param disable_options: The options to use for disabling the Job. Required.
        :type disable_options: ~azure.batch.models.BatchJobDisableOptions
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._disable_job_internal(
                job_id,
                disable_options=disable_options,
                timeout=timeout,
                ocpdate=ocpdate,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                etag=etag,
                match_condition=match_condition,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = DisableJobPollingMethodAsync(self, pipeline_response, None, job_id, polling_interval)
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_enable_job(
        self,
        job_id: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Enables a Job with Long Running Operation support.
        When you call this API, the Batch service sets a disabled Job to the enabling
        state. After the this operation is completed, the Job moves to the active
        state, and scheduling of new Tasks under the Job resumes. The Batch service
        does not allow a Task to remain in the active state for more than 180 days.
        Therefore, if you enable a Job containing active Tasks which were added more
        than 180 days ago, those Tasks will not run.

        :param job_id: The ID of the Job to enable. Required.
        :type job_id: str
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._enable_job_internal(
                job_id,
                timeout=timeout,
                ocpdate=ocpdate,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                etag=etag,
                match_condition=match_condition,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = EnableJobPollingMethodAsync(self, pipeline_response, None, job_id, polling_interval)
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_delete_job_schedule(
        self,
        job_schedule_id: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Deletes a Job Schedule with Long Running Operation support.

        When you delete a Job Schedule, this also deletes all Jobs and Tasks under
        that schedule. When Tasks are deleted, all the files in their working
        directories on the Compute Nodes are also deleted (the retention period is
        ignored). The Job Schedule statistics are no longer accessible once the Job
        Schedule is deleted, though they are still counted towards Account lifetime
        statistics.

        :param job_schedule_id: The ID of the Job Schedule to delete. Required.
        :type job_schedule_id: str
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: An LROPoller that can be used to wait for the job schedule deletion to complete
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._delete_job_schedule_internal(
                job_schedule_id,
                timeout=timeout,
                ocpdate=ocpdate,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                etag=etag,
                match_condition=match_condition,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = DeleteJobSchedulePollingMethodAsync(
            self, pipeline_response, None, job_schedule_id, polling_interval
        )
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_delete_pool(
        self,
        pool_id: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Deletes a Pool from specified Account with Long Running Operation support.

        When you request that a Pool be deleted, the following actions occur: the Pool
        state is set to deleting; any ongoing resize operation on the Pool are stopped;
        the Batch service starts resizing the Pool to zero Compute Nodes; any Tasks
        running on existing Compute Nodes are terminated and requeued (as if a resize
        Pool operation had been requested with the default requeue option); finally,
        the Pool is removed from the system. Because running Tasks are requeued, the
        user can rerun these Tasks by updating their Job to target a different Pool.
        The Tasks can then run on the new Pool. If you want to override the requeue
        behavior, then you should call resize Pool explicitly to shrink the Pool to
        zero size before deleting the Pool. If you call an Update, Patch or Delete API
        on a Pool in the deleting state, it will fail with HTTP status code 409 with
        error code PoolBeingDeleted.

        :param pool_id: The ID of the Pool to get. Required.
        :type pool_id: str
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._delete_pool_internal(
                pool_id,
                timeout=timeout,
                ocpdate=ocpdate,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                etag=etag,
                match_condition=match_condition,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = DeletePoolPollingMethodAsync(self, pipeline_response, None, pool_id, polling_interval)
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_delete_certificate(
        self,
        thumbprint_algorithm: str,
        thumbprint: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Deletes a Certificate from the specified Account with Long Running Operation support.

        You cannot delete a Certificate if a resource (Pool or Compute Node) is using
        it. Before you can delete a Certificate, you must therefore make sure that the
        Certificate is not associated with any existing Pools, the Certificate is not
        installed on any Nodes (even if you remove a Certificate from a Pool, it is not
        removed from existing Compute Nodes in that Pool until they restart), and no
        running Tasks depend on the Certificate. If you try to delete a Certificate
        that is in use, the deletion fails. The Certificate status changes to
        deleteFailed. You can use Cancel Delete Certificate to set the status back to
        active if you decide that you want to continue using the Certificate.

        :param thumbprint_algorithm: The algorithm used to derive the thumbprint parameter. This must
         be sha1. Required.
        :type thumbprint_algorithm: str
        :param thumbprint: The thumbprint of the Certificate to be deleted. Required.
        :type thumbprint: str
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._delete_certificate_internal(
                thumbprint_algorithm,
                thumbprint,
                timeout=timeout,
                ocpdate=ocpdate,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = DeleteCertificatePollingMethodAsync(
            self, pipeline_response, None, thumbprint_algorithm, thumbprint, polling_interval
        )
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_deallocate_node(
        self,
        pool_id: str,
        node_id: str,
        options: Optional[_models.BatchNodeDeallocateOptions] = None,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Deallocates a Compute Node with Long Running Operation support.

        You can deallocate a Compute Node only if it is in an idle or running state.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node that you want to restart. Required.
        :type node_id: str
        :param options: The options to use for deallocating the Compute Node. Default value is None.
        :type options: ~azure.batch.models.BatchNodeDeallocateOptions
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :paramtype ocpdate: ~datetime.datetime
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._deallocate_node_internal(
                pool_id,
                node_id,
                options=options,
                timeout=timeout,
                ocpdate=ocpdate,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = DeallocateNodePollingMethodAsync(
            self, pipeline_response, None, pool_id, node_id, polling_interval
        )
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_reboot_node(
        self,
        pool_id: str,
        node_id: str,
        options: Optional[_models.BatchNodeRebootOptions] = None,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Reboots a Compute Node with Long Running Operation support.

        You can restart a Compute Node only if it is in an idle or running state.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node that you want to restart. Required.
        :type node_id: str
        :param options: The options to use for rebooting the Compute Node. Default value is None.
        :type options: ~azure.batch.models.BatchNodeRebootOptions
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._reboot_node_internal(
                pool_id,
                node_id,
                options=options,
                timeout=timeout,
                ocpdate=ocpdate,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = RebootNodePollingMethodAsync(self, pipeline_response, None, pool_id, node_id, polling_interval)
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_reimage_node(
        self,
        pool_id: str,
        node_id: str,
        options: Optional[_models.BatchNodeReimageOptions] = None,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Reimages a Compute Node with Long Running Operation support.

        Reinstalls the operating system on the specified Compute Node

        You can reinstall the operating system on a Compute Node only if it is in an
        idle or running state. This API can be invoked only on Pools created with the
        cloud service configuration property.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node that you want to restart. Required.
        :type node_id: str
        :param options: The options to use for reimaging the Compute Node. Default value is None.
        :type options: ~azure.batch.models.BatchNodeReimageOptions
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._reimage_node_internal(
                pool_id,
                node_id,
                options=options,
                timeout=timeout,
                ocpdate=ocpdate,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = ReimageNodePollingMethodAsync(
            self, pipeline_response, None, pool_id, node_id, polling_interval
        )
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_remove_nodes(
        self,
        pool_id: str,
        remove_options: _models.BatchNodeRemoveOptions,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Removes Compute Nodes from a Pool with Long Running Operation support.

        This operation can only run when the allocation state of the Pool is steady.
        When this operation runs, the allocation state changes from steady to resizing.
        Each request may remove up to 100 nodes.

        :param pool_id: The ID of the Pool to get. Required.
        :type pool_id: str
        :param remove_options: The options to use for removing the node. Required.
        :type remove_options: ~azure.batch.models.BatchNodeRemoveOptions
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._remove_nodes_internal(
                pool_id,
                remove_options=remove_options,
                timeout=timeout,
                ocpdate=ocpdate,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                etag=etag,
                match_condition=match_condition,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = RemoveNodePollingMethodAsync(self, pipeline_response, None, pool_id, polling_interval)
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_resize_pool(
        self,
        pool_id: str,
        resize_options: _models.BatchPoolResizeOptions,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Resizes a Pool with Long Running Operation support.

        You can only resize a Pool when its allocation state is steady. If the Pool is
        already resizing, the request fails with status code 409. When you resize a
        Pool, the Pool's allocation state changes from steady to resizing. You cannot
        resize Pools which are configured for automatic scaling. If you try to do this,
        the Batch service returns an error 409. If you resize a Pool downwards, the
        Batch service chooses which Compute Nodes to remove. To remove specific Compute
        Nodes, use the Pool remove Compute Nodes API instead.

        :param pool_id: The ID of the Pool to get. Required.
        :type pool_id: str
        :param resize_options: The options to use for resizing the pool. Required.
        :type resize_options: ~azure.batch.models.BatchPoolResizeOptions
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._resize_pool_internal(
                pool_id,
                resize_options=resize_options,
                timeout=timeout,
                ocpdate=ocpdate,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                etag=etag,
                match_condition=match_condition,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = ResizePoolPollingMethodAsync(self, pipeline_response, None, pool_id, polling_interval)
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_start_node(
        self,
        pool_id: str,
        node_id: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Starts a Compute Node with Long Running Operation support.

        You can start a Compute Node only if it has been deallocated.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node that you want to restart. Required.
        :type node_id: str
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._start_node_internal(
                pool_id,
                node_id,
                timeout=timeout,
                ocpdate=ocpdate,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = StartNodePollingMethodAsync(self, pipeline_response, None, pool_id, node_id, polling_interval)
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_stop_pool_resize(
        self,
        pool_id: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Stops an ongoing Pool resize operation with Long Running Operation support.

        This does not restore the Pool to its previous state before the resize
        operation: it only stops any further changes being made, and the Pool maintains
        its current state. After stopping, the Pool stabilizes at the number of Compute
        Nodes it was at when the stop operation was done. During the stop operation,
        the Pool allocation state changes first to stopping and then to steady. A
        resize operation need not be an explicit resize Pool request; this API can also
        be used to halt the initial sizing of the Pool when it is created.

        :param pool_id: The ID of the Pool to get. Required.
        :type pool_id: str
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._stop_pool_resize_internal(
                pool_id,
                timeout=timeout,
                ocpdate=ocpdate,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                etag=etag,
                match_condition=match_condition,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = StopPoolResizePollingMethodAsync(self, pipeline_response, None, pool_id, polling_interval)
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_terminate_job(
        self,
        job_id: str,
        options: Optional[_models.BatchJobTerminateOptions] = None,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        force: Optional[bool] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Terminates a Job with Long Running Operation support, marking it as completed.

        When a Terminate Job request is received, the Batch service sets the Job to the
        terminating state. The Batch service then terminates any running Tasks
        associated with the Job and runs any required Job release Tasks. Then the Job
        moves into the completed state. If there are any Tasks in the Job in the active
        state, they will remain in the active state. Once a Job is terminated, new
        Tasks cannot be added and any remaining active Tasks will not be scheduled.

        :param job_id: The ID of the Job to terminate. Required.
        :type job_id: str
        :param options: The options to use for terminating the Job. Default value is None.
        :type options: ~azure.batch.models.BatchJobTerminateOptions
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword force: If true, the server will terminate the Job even if the corresponding nodes have
         not fully processed the termination. The default value is false. Default value is None.
        :paramtype force: bool
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._terminate_job_internal(
                job_id,
                options=options,
                timeout=timeout,
                ocpdate=ocpdate,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                force=force,
                etag=etag,
                match_condition=match_condition,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = TerminateJobPollingMethodAsync(self, pipeline_response, None, job_id, polling_interval)
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    @distributed_trace
    async def begin_terminate_job_schedule(
        self,
        job_schedule_id: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        force: Optional[bool] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        polling_interval: int = 5,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Terminates a Job Schedule with Long Running Operation support.

        :param job_schedule_id: The ID of the Job Schedule to terminates. Required.
        :type job_schedule_id: str
        :keyword timeout: The maximum time that the server can spend processing the request, in
         seconds. The default is 30 seconds. If the value is larger than 30, the default will be used
         instead.". Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword force: If true, the server will terminate the JobSchedule even if the corresponding
         nodes have not fully processed the termination. The default value is false. Default value is
         None.
        :paramtype force: bool
        :keyword etag: check if resource is changed. Set None to skip checking etag. Default value is
         None.
        :paramtype etag: str
        :keyword match_condition: The match condition to use upon the etag. Default value is None.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword polling_interval: The interval in seconds between polling attempts. Default value is 5.
        :paramtype polling_interval: int
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def capture_pipeline_response(pipeline_response, _deserialized, _response_headers):
            return pipeline_response

        pipeline_response = cast(
            PipelineResponse,
            await self._terminate_job_schedule_internal(
                job_schedule_id,
                timeout=timeout,
                ocpdate=ocpdate,
                if_modified_since=if_modified_since,
                if_unmodified_since=if_unmodified_since,
                force=force,
                etag=etag,
                match_condition=match_condition,
                cls=capture_pipeline_response,
                **kwargs,
            ),
        )

        polling_method = TerminateJobSchedulePollingMethodAsync(
            self, pipeline_response, None, job_schedule_id, polling_interval
        )
        return AsyncLROPoller(self, pipeline_response, lambda _: None, polling_method, **kwargs)

    # create_task_collection renamed
    @distributed_trace
    async def create_tasks(
        self,
        job_id: str,
        task_collection: List[_models.BatchTaskCreateOptions],
        concurrencies: int = 0,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> _models.BatchCreateTaskCollectionResult:
        """Adds a collection of Tasks to the specified Job.

        Note that each Task must have a unique ID. The Batch service may not return the
        results for each Task in the same order the Tasks were submitted in this
        request. If the server times out or the connection is closed during the
        request, the request may have been partially or fully processed, or not at all.
        In such cases, the user should re-issue the request. Note that it is up to the
        user to correctly handle failures when re-issuing a request. For example, you
        should use the same Task IDs during a retry so that if the prior operation
        succeeded, the retry will not create extra Tasks unexpectedly. If the response
        contains any Tasks which failed to add, a client can retry the request. In a
        retry, it is most efficient to resubmit only Tasks that failed to add, and to
        omit Tasks that were successfully added on the first attempt. The maximum
        lifetime of a Task from addition to completion is 180 days. If a Task has not
        completed within 180 days of being added it will be terminated by the Batch
        service and left in whatever state it was in at that time.

        :param job_id: The ID of the Job to which the Task collection is to be added. Required.
        :type job_id: str
        :param task_collection: The Tasks to be added. Required.
        :type task_collection: ~azure.batch.models.BatchTaskAddCollectionResult
        :param concurrencies: number of coroutines to use in parallel when adding tasks. If specified
         and greater than 0, will start additional coroutines to submit requests and wait for them to finish.
         Otherwise will submit create_task_collection requests sequentially on main thread
        :type concurrencies: int
        :keyword timeout: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :return: BatchTaskAddCollectionResult. The BatchTaskAddCollectionResult is compatible with MutableMapping
        :rtype: ~azure.batch.models.BatchTaskAddCollectionResult
        :raises ~azure.batch.custom.CreateTasksError:
        """

        kwargs.update({"timeout": timeout, "ocpdate": ocpdate})

        results_queue: Deque[_models.BatchTaskCreateResult] = collections.deque()
        task_workflow_manager = _TaskWorkflowManager(self, job_id=job_id, task_collection=task_collection, **kwargs)

        if concurrencies:
            if concurrencies < 0:
                raise ValueError("Concurrencies must be positive or 0")

            coroutines = []
            for _ in range(concurrencies):
                coroutines.append(task_workflow_manager.task_collection_handler(results_queue))
            await asyncio.gather(*coroutines)
        else:
            await task_workflow_manager.task_collection_handler(results_queue)

        # Only define error if all coroutines have finished and there were failures
        if task_workflow_manager.failure_tasks or task_workflow_manager.errors:
            raise _models.CreateTasksError(
                task_workflow_manager.tasks_to_add,
                task_workflow_manager.failure_tasks,
                task_workflow_manager.errors,
            )
        submitted_tasks = _handle_output(results_queue)
        return _models.BatchCreateTaskCollectionResult(values_property=submitted_tasks)

    @distributed_trace
    async def get_node_file(
        self,
        pool_id: str,
        node_id: str,
        file_path: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        ocp_range: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterator[bytes]:
        """Returns the content of the specified Compute Node file.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node from which you want to delete the file. Required.
        :type node_id: str
        :param file_path: The path to the file or directory that you want to delete. Required.
        :type file_path: str
        :keyword timeout: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword ocp_range: The byte range to be retrieved. The default is to retrieve the entire file.
         The
         format is bytes=startRange-endRange. Default value is None.
        :paramtype ocp_range: str
        :return: bytes
        :rtype: bytes
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        args = [pool_id, node_id, file_path]
        kwargs.update(
            {
                "timeout": timeout,
                "ocpdate": ocpdate,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
                "ocp_range": ocp_range,
            }
        )
        kwargs["stream"] = True
        return await super().get_node_file(*args, **kwargs)

    @distributed_trace
    async def get_node_file_properties(
        self,
        pool_id: str,
        node_id: str,
        file_path: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> _models.BatchFileProperties:
        """Gets the properties of the specified Compute Node file.

        :param pool_id: The ID of the Pool that contains the Compute Node. Required.
        :type pool_id: str
        :param node_id: The ID of the Compute Node from which you want to delete the file. Required.
        :type node_id: str
        :param file_path: The path to the file or directory that you want to delete. Required.
        :type file_path: str
        :keyword timeout: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :return: BatchFileProperties
        :rtype: ~azure.batch.models.BatchFileProperties
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def cls(_pipeline_response, _json_response, headers):
            return _models.BatchFileProperties(
                url=headers["ocp-batch-file-url"],
                is_directory=headers["ocp-batch-file-isdirectory"],
                last_modified=headers["Last-Modified"],
                content_length=headers["Content-Length"],
                creation_time=headers["ocp-creation-time"],
                # content_type=headers["Content-Type"], # need to add to typespec
                file_mode=headers["ocp-batch-file-mode"],
            )

        # cls = lambda pipeline_response, json_response, headers: _models.BatchFileProperties(
        #     url=headers["ocp-batch-file-url"],
        #     is_directory=headers["ocp-batch-file-isdirectory"],
        #     last_modified=headers["Last-Modified"],
        #     content_length=headers["Content-Length"],
        #     creation_time=headers["ocp-creation-time"],
        #     # content_type=headers["Content-Type"], # need to add to typespec
        #     file_mode=headers["ocp-batch-file-mode"],
        # )

        get_response: _models.BatchFileProperties = await super()._get_node_file_properties_internal(  # type: ignore
            pool_id,
            node_id,
            file_path,
            timeout=timeout,
            ocpdate=ocpdate,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            cls=cls,
            **kwargs,
        )

        return get_response

    @distributed_trace
    async def get_task_file_properties(
        self,
        job_id: str,
        task_id: str,
        file_path: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        **kwargs: Any
    ) -> _models.BatchFileProperties:
        """Gets the properties of the specified Task file.

        :param job_id: The ID of the Job that contains the Task. Required.
        :type job_id: str
        :param task_id: The ID of the Task whose file you want to retrieve. Required.
        :type task_id: str
        :param file_path: The path to the Task file that you want to get the content of. Required.
        :type file_path: str
        :keyword timeout: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :return: BatchFileProperties
        :rtype: ~azure.batch.models.BatchFileProperties
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        def cls(_pipeline_response, _json_response, headers):
            return _models.BatchFileProperties(
                url=headers["ocp-batch-file-url"],
                is_directory=headers["ocp-batch-file-isdirectory"],
                last_modified=headers["Last-Modified"],
                content_length=headers["Content-Length"],
                creation_time=headers["ocp-creation-time"],
                # content_type=headers["Content-Type"], # need to add to typespec
                file_mode=headers["ocp-batch-file-mode"],
            )

        # cls = lambda pipeline_response, json_response, headers: _models.BatchFileProperties(
        #     url=headers["ocp-batch-file-url"],
        #     is_directory=headers["ocp-batch-file-isdirectory"],
        #     last_modified=headers["Last-Modified"],
        #     content_length=headers["Content-Length"],
        #     creation_time=headers["ocp-creation-time"],
        #     # content_type=headers["Content-Type"], # need to add to typespec
        #     file_mode=headers["ocp-batch-file-mode"],
        # )

        get_response: _models.BatchFileProperties = await super()._get_task_file_properties_internal(  # type: ignore
            job_id,
            task_id,
            file_path,
            timeout=timeout,
            ocpdate=ocpdate,
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            cls=cls,
            **kwargs,
        )

        return get_response

    @distributed_trace
    async def get_task_file(
        self,
        job_id: str,
        task_id: str,
        file_path: str,
        *,
        timeout: Optional[int] = None,
        ocpdate: Optional[datetime.datetime] = None,
        if_modified_since: Optional[datetime.datetime] = None,
        if_unmodified_since: Optional[datetime.datetime] = None,
        ocp_range: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncIterator[bytes]:
        """Returns the content of the specified Task file.

        :param job_id: The ID of the Job that contains the Task. Required.
        :type job_id: str
        :param task_id: The ID of the Task whose file you want to retrieve. Required.
        :type task_id: str
        :param file_path: The path to the Task file that you want to get the content of. Required.
        :type file_path: str
        :keyword timeout: The maximum number of items to return in the response. A maximum of 1000
         applications can be returned. Default value is None.
        :paramtype timeout: int
        :keyword ocpdate: The time the request was issued. Client libraries typically set this to the
         current system clock time; set it explicitly if you are calling the REST API
         directly. Default value is None.
        :paramtype ocpdate: ~datetime.datetime
        :keyword if_modified_since: A timestamp indicating the last modified time of the resource known
         to the
         client. The operation will be performed only if the resource on the service has
         been modified since the specified time. Default value is None.
        :paramtype if_modified_since: ~datetime.datetime
        :keyword if_unmodified_since: A timestamp indicating the last modified time of the resource
         known to the
         client. The operation will be performed only if the resource on the service has
         not been modified since the specified time. Default value is None.
        :paramtype if_unmodified_since: ~datetime.datetime
        :keyword ocp_range: The byte range to be retrieved. The default is to retrieve the entire file.
         The
         format is bytes=startRange-endRange. Default value is None.
        :paramtype ocp_range: str
        :return: bytes
        :rtype: bytes
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        args = [job_id, task_id, file_path]
        kwargs.update(
            {
                "timeout": timeout,
                "ocpdate": ocpdate,
                "if_modified_since": if_modified_since,
                "if_unmodified_since": if_unmodified_since,
                "ocp_range": ocp_range,
            }
        )
        kwargs["stream"] = True
        return await super().get_task_file(*args, **kwargs)


class _TaskWorkflowManager:
    """Worker class for one create_task_collection request

    :param str job_id: The ID of the job to which the task collection is to be
        added.
    :ivar tasks_to_add: The collection of tasks to add.
    :vartype tasks_to_add: Iterable[~azure.batch.models.BatchTaskCreateContent]
    :param task_create_task_collection_options: Additional parameters for the
        operation
    :type task_create_task_collection_options: :class:`TaskAddCollectionOptions
        <azure.batch.models.TaskAddCollectionOptions>`
    """

    def __init__(
        self,
        batch_client: BatchClientOperationsMixin,
        job_id: str,
        task_collection: Iterable[_models.BatchTaskCreateOptions],
        **kwargs
    ):
        # List of tasks which failed to add due to a returned client error
        self.failure_tasks: Deque[_models.BatchTaskCreateResult] = collections.deque()
        # List of unknown exceptions which occurred during requests.
        self.errors: Deque[Any] = collections.deque()

        # synchronized through lock variables
        self._max_tasks_per_request = MAX_TASKS_PER_REQUEST
        self.tasks_to_add = collections.deque(task_collection)

        # Variables to be used for task create_task_collection requests
        self._batch_client = batch_client
        self._job_id = job_id

        self._kwargs = kwargs

    async def _bulk_add_tasks(
        self,
        results_queue: collections.deque,
        chunk_tasks_to_add: List[_models.BatchTaskCreateOptions],
    ):
        """Adds a chunk of tasks to the job

        Retry chunk if body exceeds the maximum request size and retry tasks
        if failed due to server errors.

        :param results_queue: Queue to place the return value of the request
        :type results_queue: collections.deque
        :param chunk_tasks_to_add: Chunk of at most 100 tasks with retry details
        :type chunk_tasks_to_add: list[~azure.batch.models.BatchTaskCreateOptions]
        """

        try:
            create_task_collection_response: _models.BatchCreateTaskCollectionResult = (
                await self._batch_client.create_task_collection(
                    job_id=self._job_id,
                    task_collection=_models.BatchTaskGroup(values_property=chunk_tasks_to_add),
                    **self._kwargs,
                )
            )
        except HttpResponseError as e:
            # In case of a chunk exceeding the MaxMessageSize split chunk in half
            # and resubmit smaller chunk requests
            # TODO: Replace string with constant variable once available in SDK
            if e.error and e.error.code == "RequestBodyTooLarge":  # pylint: disable=no-member
                # In this case the task is misbehaved and will not be able to be added due to:
                #   1) The task exceeding the max message size
                #   2) A single cell of the task exceeds the per-cell limit, or
                #   3) Sum of all cells exceeds max row limit
                if len(chunk_tasks_to_add) == 1:
                    failed_task = chunk_tasks_to_add.pop()
                    self.errors.appendleft(e)
                    _LOGGER.error(
                        "Failed to add task with ID %s due to the body exceeding the maximum request size",
                        failed_task.id,
                    )
                else:
                    # Assumption: Tasks are relatively close in size therefore if one batch exceeds size limit
                    # we should decrease the initial task collection size to avoid repeating the error
                    # Midpoint is lower bounded by 1 due to above base case
                    midpoint = int(len(chunk_tasks_to_add) / 2)
                    if midpoint < self._max_tasks_per_request:
                        _LOGGER.info(
                            "Amount of tasks per request reduced from %s to %s due to the"
                            " request body being too large",
                            str(self._max_tasks_per_request),
                            str(midpoint),
                        )
                        self._max_tasks_per_request = midpoint

                    # Not the most efficient solution for all cases, but the goal of this is to handle this
                    # exception and have it work in all cases where tasks are well behaved
                    # Behavior retries as a smaller chunk and
                    # appends extra tasks to queue to be picked up by another coroutines .
                    self.tasks_to_add.extendleft(chunk_tasks_to_add[midpoint:])
                    await self._bulk_add_tasks(results_queue, chunk_tasks_to_add[:midpoint])
            # Retry server side errors
            elif 500 <= e.response.status_code <= 599:  # type: ignore
                self.tasks_to_add.extendleft(chunk_tasks_to_add)
            else:
                # Re-add to pending queue as unknown status / don't have result
                self.tasks_to_add.extendleft(chunk_tasks_to_add)
                # Unknown State - don't know if tasks failed to add or were successful
                self.errors.appendleft(e)
        except Exception as e:  # pylint: disable=broad-except
            # Re-add to pending queue as unknown status / don't have result
            self.tasks_to_add.extendleft(chunk_tasks_to_add)
            # Unknown State - don't know if tasks failed to add or were successful
            self.errors.appendleft(e)
        else:
            if create_task_collection_response.values_property:
                for task_result in create_task_collection_response.values_property:
                    if task_result.status == _models.BatchTaskAddStatus.SERVER_ERROR:
                        # Server error will be retried
                        for task in chunk_tasks_to_add:
                            if task.id == task_result.task_id:
                                self.tasks_to_add.appendleft(task)
                    elif task_result.status == _models.BatchTaskAddStatus.CLIENT_ERROR and not (
                        task_result.error and task_result.error.code == "TaskExists"
                    ):
                        # Client error will be recorded unless Task already exists
                        self.failure_tasks.appendleft(task_result)
                    else:
                        results_queue.appendleft(task_result)

    async def task_collection_handler(self, results_queue):
        """Main method for worker to run

        Pops a chunk of tasks off the collection of pending tasks to be added and submits them to be added.

        :param collections.deque results_queue: Queue for worker to output results to
        """
        # Add tasks until either we run out or we run into an unexpected error
        while self.tasks_to_add and not self.errors:
            max_tasks = self._max_tasks_per_request  # local copy
            chunk_tasks_to_add = []
            while len(chunk_tasks_to_add) < max_tasks and self.tasks_to_add:
                chunk_tasks_to_add.append(self.tasks_to_add.pop())

            if chunk_tasks_to_add:
                await self._bulk_add_tasks(results_queue, chunk_tasks_to_add)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


def _handle_output(results_queue):
    """Scan output for exceptions

    If there is an output from an add task collection call add it to the results.

    :param results_queue: Queue containing results of attempted create_task_collection's
    :type results_queue: collections.deque
    :return: list of TaskAddResults
    :rtype: list[~TaskAddResult]
    """
    results = []
    while results_queue:
        queue_item = results_queue.pop()
        results.append(queue_item)
    return results
