# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import MutableMapping
from collections import Counter
from ._generated.models import JobQueueInternal, RouterWorkerInternal


def _validate_value(value):
    primitive = (int,
                 float,
                 str,
                 bool)
    return isinstance(value, primitive)


class LabelCollection(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.__store = {}
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if _validate_value(value):
                self.__store[key] = value
            else:
                raise ValueError("Unsupported value type " + str(type(value)))
        else:
            raise ValueError("Unsupported key type " + str(type(key)))

    def __delitem__(self, key):
        del self.__store[key]

    def __getitem__(self, item):
        return self.__store[item]

    def __iter__(self):
        return iter(self.__store)

    def __len__(self):
        return len(self.__store)

    def __repr__(self):
        return repr(self.__store)

    def __eq__(self, other):
        return Counter(self.__store) == Counter(other)


class JobQueue(object):
    def __init__(self, **kwargs):
        self.id = kwargs.pop('identifier', None)
        self.name = kwargs.pop('name', None)
        self.distribution_policy_id = kwargs.pop('distribution_policy_id', None)
        self.labels = kwargs.pop('labels', None)
        self.exception_policy_id = kwargs.pop('exception_policy_id', None)

    @classmethod
    def _from_generated(cls, job_queue_generated):
        return cls(
            identifier = job_queue_generated.id,
            name = job_queue_generated.name,
            distribution_policy_id = job_queue_generated.distribution_policy_id,
            labels = LabelCollection(job_queue_generated.labels),
            exception_policy_id = job_queue_generated.exception_policy_id
        )

    def _to_generated(self):
        return JobQueueInternal(
            name = self.name,
            distribution_policy_id = self.distribution_policy_id,
            labels = self.labels,
            exception_policy_id = self.exception_policy_id
        )


class QueueAssignment(object):
    def __init__(self, **kwargs):
        # Empty object
        pass

    @classmethod
    def _from_generated(
            cls,
            queue_assignment_generated,  # pylint:disable=unused-argument
    ):
        return cls()

    @staticmethod
    def _to_generated(
            **kwargs  # pylint:disable=unused-argument
    ):
        return {}


# pylint:disable=too-many-instance-attributes
class RouterWorker(object):
    """An entity for jobs to be routed to.

    :ivar id:
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
    :vartype labels: ~azure.communication.jobrouter.LabelCollection
    :ivar tags: A set of tags. A set of non-identifying attributes attached to this worker.
    :vartype tags: ~azure.communication.jobrouter.LabelCollection
    :ivar channel_configurations: The channel(s) this worker can handle and their impact on the
     workers capacity.
    :vartype channel_configurations: dict[str, ~azure.communication.jobrouter.ChannelConfiguration]
    :ivar offers: A list of active offers issued to this worker.
    :vartype offers: list[~azure.communication.jobrouter.JobOffer]
    :ivar assigned_jobs: A list of assigned jobs attached to this worker.
    :vartype assigned_jobs: list[~azure.communication.jobrouter.WorkerAssignment]
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
        :paramtype labels: ~azure.communication.jobrouter.LabelCollection
        :keyword tags: A set of tags. A set of non-identifying attributes attached to this worker.
        :paramtype tags: ~azure.communication.jobrouter.LabelCollection
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
            queue_assignments = {k: QueueAssignment._from_generated(v) for k, v in
                                 router_worker_generated.queue_assignments.items()},
            total_capacity = router_worker_generated.total_capacity,
            labels = LabelCollection(router_worker_generated.labels),
            tags = LabelCollection(router_worker_generated.tags),
            channel_configurations = router_worker_generated.channel_configurations,
            offers = router_worker_generated.offers,
            assigned_jobs = router_worker_generated.assigned_jobs,
            load_ratio = router_worker_generated.load_ratio,
            available_for_offers = router_worker_generated.available_for_offers
        )

    def _to_generated(self):
        queue_assignments = self.queue_assignments
        if queue_assignments is not None:
            # pylint:disable=protected-access
            queue_assignments = {k: v._to_generated() for k, v in self.queue_assignments.items()}

        return RouterWorkerInternal(
            # pylint:disable=protected-access
            queue_assignments = queue_assignments,
            total_capacity = self.total_capacity,
            labels = self.labels,
            tags = self.tags,
            channel_configurations = self.channel_configurations,
            available_for_offers = self.available_for_offers
        )
