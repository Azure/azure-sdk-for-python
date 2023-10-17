# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
from enum import Enum
from typing import (
    List,
    Dict,
    Union,
    Optional,
    overload,
    Any
)
from ._models import (
    RouterJob as RouterJobGenerated,
    JobMatchingMode,
    RouterWorkerSelector
)
from .._datetimeutils import _convert_str_to_datetime
from azure.core.serialization import _datetime_as_isostr  # pylint:disable=protected-access
from azure.core import CaseInsensitiveEnumMeta


class RouterJob(RouterJobGenerated):
    """A unit of work to be routed.

        Readonly variables are only populated by the server, and will be ignored when sending a request.

        All required parameters must be populated in order to send to Azure.

        :ivar id: The id of the job. Required.
        :vartype id: str
        :ivar channel_reference: Reference to an external parent context, eg. call ID.
        :vartype channel_reference: str
        :ivar status: The status of the Job. Known values are: "pendingClassification", "queued",
         "assigned", "completed", "closed", "cancelled", "classificationFailed", "created",
         "pendingSchedule", "scheduled", "scheduleFailed", and "waitingForActivation".
        :vartype status: str or ~azure.communication.jobrouter.models.RouterJobStatus
        :ivar enqueued_at: The time a job was queued in UTC.
        :vartype enqueued_at: ~datetime.datetime
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
         worker must satisfy
         in order to process this job.
        :vartype requested_worker_selectors:
         list[~azure.communication.jobrouter.models.RouterWorkerSelector]
        :ivar attached_worker_selectors: A collection of label selectors attached by a classification
         policy, which a
         worker must satisfy in order to process this job.
        :vartype attached_worker_selectors:
         list[~azure.communication.jobrouter.models.RouterWorkerSelector]
        :ivar labels: A set of key/value pairs that are identifying attributes used by the rules
         engines to make decisions.
        :vartype labels: dict[str, any]
        :ivar assignments: A collection of the assignments of the job.
         Key is AssignmentId.
        :vartype assignments: dict[str, ~azure.communication.jobrouter.models.RouterJobAssignment]
        :ivar tags: A set of non-identifying attributes attached to this job.
        :vartype tags: dict[str, any]
        :ivar notes: Notes attached to a job, sorted by timestamp.
        :vartype notes: dict[str, str]
        :ivar scheduled_at: If set, job will be scheduled to be enqueued at a given time.
        :vartype scheduled_at: ~datetime.datetime
        :ivar matching_mode: The matching mode to be applied to this job.

         Supported types:

         QueueAndMatchMode: Used when matching worker to a job is required to be
         done right after job is queued.
         ScheduleAndSuspendMode: Used for scheduling
         jobs to be queued at a future time. At specified time, matching of a worker to
         the job will not start automatically.
         SuspendMode: Used when matching workers
         to a job needs to be suspended.
        :vartype matching_mode: ~azure.communication.jobrouter.models.JobMatchingMode
        """
    @overload
    def __init__(
            self,
            *,
            channel_reference: Optional[str] = None,
            channel_id: Optional[str] = None,
            classification_policy_id: Optional[str] = None,
            queue_id: Optional[str] = None,
            priority: Optional[int] = None,
            disposition_code: Optional[str] = None,
            requested_worker_selectors: Optional[List[RouterWorkerSelector]] = None,
            labels: Optional[Dict[str, Union[int, float, str, bool, None]]] = None,
            tags: Optional[Dict[str, Union[int, float, str, bool, None]]] = None,
            notes: Dict[Union[str, datetime.datetime], str] = None,
            matching_mode: Optional[JobMatchingMode] = None,
            **kwargs):
        """
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
        """

    def __init__(self, *args: Any, **kwargs: Any):
        notes = kwargs.pop('notes', None)
        if notes is not None:
            for k in [key for key in notes.keys()]:
                v: str = notes[k]
                if isinstance(k, str):
                    datetime_as_dt: datetime = _convert_str_to_datetime(k)    # pylint:disable=protected-access
                    notes.pop(k)
                    datetime_as_str: str = _datetime_as_isostr(datetime_as_dt)    # pylint:disable=protected-access
                    notes[datetime_as_str] = v
                elif isinstance(k, datetime.datetime):
                    datetime_as_str: str = _datetime_as_isostr(k)    # pylint:disable=protected-access
                    notes.pop(k)
                    notes[datetime_as_str] = v

            kwargs['notes'] = notes

        super().__init__(*args, **kwargs)


__all__: List[str] = [
    "RouterJob",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
