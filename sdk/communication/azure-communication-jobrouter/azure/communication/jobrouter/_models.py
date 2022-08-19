# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

from azure.core.serialization import _datetime_as_isostr  # pylint:disable=protected-access

from ._generated.models import (
    JobQueueInternal,
    JobQueueItemInternal,
    RouterWorkerInternal,
    RouterWorkerItemInternal,
    RouterJobInternal,
    RouterJobItemInternal,
)
from ._utils import _convert_str_to_datetime


QueueAssignment = TypedDict("QueueAssignment", {}, total = False)


class JobQueue(object):
    """A queue that can contain jobs to be routed.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar id: The Id of this queue.
    :vartype id: str
    :ivar name: The name of this queue.
    :vartype name: str
    :ivar distribution_policy_id: The ID of the distribution policy that will determine
     how a job is distributed to workers.
    :vartype distribution_policy_id: str
    :ivar labels: A set of key/value pairs that are identifying attributes used by the rules
     engines to make decisions.
    :vartype labels: dict[str, Union[int, float, str, bool]]
    :ivar exception_policy_id: (Optional) The ID of the exception policy that determines various
     job escalation rules.
    :vartype exception_policy_id: str
    """
    def __init__(self, **kwargs):
        """
        :keyword name: The name of this queue.
        :paramtype name: str
        :keyword distribution_policy_id: Required. The ID of the distribution policy that will
         determine how a job is distributed to workers.
        :paramtype distribution_policy_id: str
        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: dict[str, Union[int, float, str, bool]]
        :keyword exception_policy_id: (Optional) The ID of the exception policy that determines various
         job escalation rules.
        :paramtype exception_policy_id: str
        """
        self.id = kwargs.pop('id', None)
        self.name = kwargs.pop('name', None)
        self.distribution_policy_id = kwargs.pop('distribution_policy_id', None)
        self.labels = kwargs.pop('labels', None)
        self.exception_policy_id = kwargs.pop('exception_policy_id', None)

    @classmethod
    def _from_generated(cls, job_queue_generated):
        return cls(
            id = job_queue_generated.id,
            name = job_queue_generated.name,
            distribution_policy_id = job_queue_generated.distribution_policy_id,
            labels = job_queue_generated.labels,
            exception_policy_id = job_queue_generated.exception_policy_id
        )

    def _to_generated(self):
        return JobQueueInternal(
            name = self.name,
            distribution_policy_id = self.distribution_policy_id,
            labels = self.labels,
            exception_policy_id = self.exception_policy_id
        )


class JobQueueItem(object):
    """A queue returned from a pageable list.

    :ivar job_queue: A queue that can contain jobs to be routed.
    :vartype job_queue: ~azure.communication.jobrouter.JobQueue
    :ivar etag: Etag of the resource
    :vartype etag: str
    """
    def __init__(self, **kwargs):
        """
        :keyword job_queue: A queue that can contain jobs to be routed.
        :paramtype job_queue: ~azure.communication.jobrouter.JobQueue
        :keyword etag: Etag of the resource
        :paramtype etag: str
        """
        self.job_queue = kwargs.pop('job_queue', None)
        self.etag = kwargs.pop('etag', None)

    @classmethod
    def _from_generated(
            cls,
            entity_generated,  # type: JobQueueItemInternal
            # pylint:disable=unused-argument
            **kwargs,  # type: Any
    ):
        #  type: (...) -> JobQueueItem
        return cls(
            job_queue = JobQueue._from_generated(entity_generated.job_queue),  # pylint:disable=protected-access
            etag = entity_generated.etag
        )


# pylint:disable=too-many-instance-attributes
class RouterWorker(object):
    """An entity for jobs to be routed to.

    :ivar id: Id of the worker
    :vartype id: str
    :ivar state: The current state of the worker. Known values are: "active", "draining",
     "inactive".
    :vartype state: str or ~azure.communication.jobrouter.RouterWorkerState
    :ivar queue_assignments: The queue(s) that this worker can receive work from.
    :vartype queue_assignments: dict[str, ~azure.communication.jobrouter.QueueAssignment]
    :ivar total_capacity: The total capacity score this worker has to manage multiple concurrent
     jobs.
    :vartype total_capacity: int
    :ivar labels: A set of key/value pairs that are identifying attributes used by the rules
     engines to make decisions.
    :vartype labels: dict[str, Union[int, float, str, bool]]
    :ivar tags: A set of tags. A set of non-identifying attributes attached to this worker.
    :vartype tags: dict[str, Union[int, float, str, bool]]
    :ivar channel_configurations: The channel(s) this worker can handle and their impact on the
     workers capacity.
    :vartype channel_configurations: Dict[str, ~azure.communication.jobrouter.ChannelConfiguration]
    :ivar offers: A list of active offers issued to this worker.
    :vartype offers: List[~azure.communication.jobrouter.JobOffer]
    :ivar assigned_jobs: A list of assigned jobs attached to this worker.
    :vartype assigned_jobs: List[~azure.communication.jobrouter.WorkerAssignment]
    :ivar load_ratio: A value indicating the workers capacity. A value of '1' means all capacity is
     consumed. A value of '0' means no capacity is currently consumed.
    :vartype load_ratio: float
    :ivar available_for_offers: A flag indicating this worker is open to receive offers or not.
    :vartype available_for_offers: bool
    """
    def __init__(
            self,
            **kwargs
    ):
        """
        :keyword queue_assignments: The queue(s) that this worker can receive work from.
        :paramtype queue_assignments: dict[str, ~azure.communication.jobrouter.QueueAssignment]
        :keyword total_capacity: The total capacity score this worker has to manage multiple concurrent
         jobs.
        :paramtype total_capacity: int
        :keyword labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :paramtype labels: dict[str, Union[int, float, str, bool]]
        :keyword tags: A set of tags. A set of non-identifying attributes attached to this worker.
        :paramtype tags: dict[str, Union[int, float, str, bool]]
        :keyword channel_configurations: The channel(s) this worker can handle and their impact on the
         workers capacity.
        :paramtype channel_configurations: dict[str, ~azure.communication.jobrouter.ChannelConfiguration]
        :keyword available_for_offers: A flag indicating this worker is open to receive offers or not.
        :paramtype available_for_offers: bool
        """
        self.id = kwargs.pop('id', None)
        self.state = kwargs.pop('state', None)
        self.queue_assignments = kwargs.pop('queue_assignments', None)
        self.total_capacity = kwargs.pop('total_capacity', None)
        self.labels = kwargs.pop('labels', None)
        self.tags = kwargs.pop('tags', None)
        self.channel_configurations = kwargs.pop('channel_configurations', None)
        self.offers = kwargs.pop('offers', None)
        self.assigned_jobs = kwargs.pop('assigned_jobs', None)
        self.load_ratio = kwargs.pop('load_ratio', None)
        self.available_for_offers = kwargs.pop('available_for_offers', None)

    @classmethod
    def _from_generated(cls, router_worker_generated):
        return cls(
            id = router_worker_generated.id,
            state = router_worker_generated.state,
            # pylint:disable=protected-access
            queue_assignments = {k: QueueAssignment() for k, v in
                                 router_worker_generated.queue_assignments.items()},
            total_capacity = router_worker_generated.total_capacity,
            labels = router_worker_generated.labels,
            tags = router_worker_generated.tags,
            channel_configurations = router_worker_generated.channel_configurations,
            offers = router_worker_generated.offers,
            assigned_jobs = router_worker_generated.assigned_jobs,
            load_ratio = router_worker_generated.load_ratio,
            available_for_offers = router_worker_generated.available_for_offers
        )

    def _to_generated(self):
        queue_assignments = self.queue_assignments
        # if queue_assignments is not None:
        #     # pylint:disable=protected-access
        #     queue_assignments = {k: v._to_generated() for k, v in self.queue_assignments.items()}

        return RouterWorkerInternal(
            # pylint:disable=protected-access
            queue_assignments = queue_assignments,
            total_capacity = self.total_capacity,
            labels = self.labels,
            tags = self.tags,
            channel_configurations = self.channel_configurations,
            available_for_offers = self.available_for_offers
        )


class RouterWorkerItem(object):
    """A worker returned from a pageable list.

    :ivar router_worker: An entity for jobs to be routed to.
    :vartype router_worker: ~azure.communication.jobrouter.RouterWorker
    :ivar etag: Etag of the resource
    :vartype etag: str
    """
    def __init__(self, **kwargs):
        """
        :keyword router_worker: An entity for jobs to be routed to.
        :paramtype router_worker: ~azure.communication.jobrouter.RouterWorker
        :keyword etag: Etag of the resource
        :paramtype etag: str
        """
        self.router_worker = kwargs.pop('router_worker', None)
        self.etag = kwargs.pop('etag', None)

    @classmethod
    def _from_generated(
            cls,
            entity_generated,  # type: RouterWorkerItemInternal
            # pylint:disable=unused-argument
            **kwargs,  # type: Any
    ):
        return cls(
            # pylint:disable=protected-access
            router_worker = RouterWorker._from_generated(entity_generated.router_worker),
            etag = entity_generated.etag
        )


class RouterJob(object):
    """A unit of work to be routed.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: The id of the job.
    :vartype id: str
    :ivar channel_reference: Reference to an external parent context, eg. call ID.
    :vartype channel_reference: str
    :ivar job_status: The state of the Job. Known values are: "pendingClassification", "queued",
     "assigned", "completed", "closed", "cancelled", "classificationFailed", "created".
    :vartype job_status: Union[str, ~azure.communication.jobrouter.RouterJobStatus]
    :ivar enqueue_time_utc: The time a job was queued.
    :vartype enqueue_time_utc: ~datetime.datetime
    :ivar channel_id: The channel identifier. eg. voice, chat, etc.
    :vartype channel_id: str
    :ivar classification_policy_id: The Id of the Classification policy used for classifying a job.
    :vartype classification_policy_id: str
    :ivar queue_id: The Id of the Queue that this job is queued to.
    :vartype queue_id: str
    :ivar priority: The priority of this job.
    :vartype priority: int
    :ivar disposition_code: Reason code for cancelled or closed jobs.
    :vartype disposition_code: str
    :ivar requested_worker_selectors: A collection of manually specified label selectors, which a
     worker must satisfy in order to process this job.
    :vartype requested_worker_selectors: List[~azure.communication.jobrouter.WorkerSelector]
    :ivar attached_worker_selectors: A collection of label selectors attached by a classification
     policy, which a worker must satisfy in order to process this job.
    :vartype attached_worker_selectors: List[~azure.communication.jobrouter.WorkerSelector]
    :ivar labels: A set of key/value pairs that are identifying attributes used by the rules
     engines to make decisions.
    :vartype labels: dict[str, Union[int, float, str, bool]]
    :ivar assignments: A collection of the assignments of the job.
     Key is AssignmentId.
    :vartype assignments: Dict[str, ~azure.communication.jobrouter.JobAssignment]
    :ivar tags: A set of tags. A set of non-identifying attributes attached to this job.
    :vartype tags: dict[str, Union[int, float, str, bool]]
    :ivar notes: Notes attached to a job, sorted by timestamp.
    :vartype notes: Dict[~datetime.datetime, str]
    """
    def __init__(
            self,
            **kwargs,  # type: Any
    ):
        """
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
        :paramtype labels: dict[str, Union[int, float, str, bool]]
        :keyword tags: A set of tags. A set of non-identifying attributes attached to this job.
        :paramtype tags: dict[str, Union[int, float, str, bool]]
        :keyword notes: Notes attached to a job, sorted by timestamp.
        :paramtype notes: Dict[~datetime.datetime, str]
        """
        self.id = kwargs.pop('id', None)
        self.channel_reference = kwargs.pop('channel_reference', None)
        self.job_status = kwargs.pop('job_status', None)
        self.enqueue_time_utc = kwargs.pop('enqueue_time_utc', None)
        self.channel_id = kwargs.pop('channel_id', None)
        self.classification_policy_id = kwargs.pop('classification_policy_id', None)
        self.queue_id = kwargs.pop('queue_id', None)
        self.priority = kwargs.pop('priority', None)
        self.disposition_code = kwargs.pop('disposition_code', None)
        self.requested_worker_selectors = kwargs.pop('requested_worker_selectors', None)
        self.attached_worker_selectors = kwargs.pop('attached_worker_selectors', None)
        self.labels = kwargs.pop('labels', None)
        self.assignments = kwargs.pop('assignments', None)
        self.tags = kwargs.pop('tags', None)
        self.notes = kwargs.pop('notes', None)

    @classmethod
    def _from_generated(
            cls,
            router_job_internal,  # type: RouterJobInternal
            **kwargs  # pylint:disable=unused-argument
    ):
        #  type: (...) -> RouterJob
        job_notes = {}
        if router_job_internal.notes is not None:
            # pylint:disable=protected-access
            job_notes = {_convert_str_to_datetime(k): v for k, v in router_job_internal.notes.items()}

        return cls(
            id = router_job_internal.id,
            channel_reference = router_job_internal.channel_reference,
            job_status = router_job_internal.job_status,
            enqueue_time_utc = router_job_internal.enqueue_time_utc,
            channel_id = router_job_internal.channel_id,
            classification_policy_id = router_job_internal.classification_policy_id,
            queue_id = router_job_internal.queue_id,
            priority = router_job_internal.priority,
            disposition_code = router_job_internal.disposition_code,
            requested_worker_selectors = router_job_internal.requested_worker_selectors,
            attached_worker_selectors = router_job_internal.attached_worker_selectors,
            labels = router_job_internal.labels,
            assignments = router_job_internal.assignments,
            tags = router_job_internal.tags,
            notes = job_notes
        )

    def _to_generated(
            self
    ):
        #  type: (...) -> RouterJobInternal
        return RouterJobInternal(
            channel_reference = self.channel_reference,
            channel_id = self.channel_id,
            classification_policy_id = self.classification_policy_id,
            queue_id = self.queue_id,
            priority = self.priority,
            disposition_code = self.disposition_code,
            requested_worker_selectors = self.requested_worker_selectors,
            labels = self.labels,
            tags = self.tags,
            # pylint:disable=protected-access
            notes = {_datetime_as_isostr(k): v for k, v in self.notes.items()} if self.notes is not None else None
        )


class RouterJobItem(object):
    """A job returned from a pageable list.

    :ivar router_job: A unit of work to be routed.
    :vartype router_job: ~azure.communication.jobrouter.RouterJob
    :ivar etag: Etag of the resource
    :vartype etag: str
    """
    def __init__(self, **kwargs):
        """
        :keyword router_job: A unit of work to be routed.
        :paramtype router_job: ~azure.communication.jobrouter.RouterJob
        :keyword etag: Etag of the resource
        :paramtype etag: str
        """
        self.router_job = kwargs.pop('router_job', None)
        self.etag = kwargs.pop('etag', None)

    @classmethod
    def _from_generated(
            cls,
            entity_generated,  # type: RouterJobItemInternal
            # pylint:disable=unused-argument
            **kwargs,  # type: Any
    ):
        return cls(
            # pylint:disable=protected-access
            router_job = RouterJob._from_generated(entity_generated.router_job),
            etag = entity_generated.etag
        )


DeclineJobOfferResult = TypedDict("DeclineJobOfferResult", {}, total = False)


ReclassifyJobResult = TypedDict("ReclassifyJobResult", {}, total = False)


CancelJobResult = TypedDict("CancelJobResult", {}, total = False)


CompleteJobResult = TypedDict("CompleteJobResult", {}, total = False)


CloseJobResult = TypedDict("CloseJobResult", {}, total = False)
