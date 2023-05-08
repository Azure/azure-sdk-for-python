# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

try:
    from typing import TypedDict  # pylint: disable=no-name-in-module
except ImportError:
    from typing_extensions import TypedDict
from typing import List, Optional, Dict, Union, MutableMapping

from datetime import datetime, timezone
from dateutil.parser import parse
from azure.core.serialization import _datetime_as_isostr  # pylint:disable=protected-access

from ._models import (
    RouterWorker as RouterWorkerGenerated,
    RouterJob as RouterJobGenerated,
    JSON,
)


# cSpell:ignore tzinfos
def _convert_str_to_datetime(datetime_as_str: str) -> datetime:
    dt = parse(datetime_as_str, tzinfos=[timezone.utc])
    return dt


QueueAssignment = TypedDict("QueueAssignment", {}, total=False)

DeclineJobOfferResult = TypedDict("DeclineJobOfferResult", {}, total=False)

ReclassifyJobResult = TypedDict("ReclassifyJobResult", {}, total=False)

CancelJobResult = TypedDict("CancelJobResult", {}, total=False)

CompleteJobResult = TypedDict("CompleteJobResult", {}, total=False)

CloseJobResult = TypedDict("CloseJobResult", {}, total=False)


class RouterJob(RouterJobGenerated):
    def __init__(
        self,
        *,
        channel_reference: Optional[str] = None,
        channel_id: Optional[str] = None,
        classification_policy_id: Optional[str] = None,
        queue_id: Optional[str] = None,
        priority: Optional[int] = None,
        disposition_code: Optional[str] = None,
        requested_worker_selectors: Optional[List["_models.WorkerSelector"]] = None,
        labels: Optional[Dict[str, Union[int, float, str, bool, None]]] = None,
        tags: Optional[Dict[str, Union[int, float, str, bool, None]]] = None,
        notes: Dict[Union[str, datetime], str] = None,
        **kwargs
    ):
        if notes:
            for k in [key for key in notes.keys()]:
                v: str = notes[k]
                if isinstance(k, str):
                    datetime_as_dt: datetime = _convert_str_to_datetime(k)  # pylint:disable=protected-access
                    notes.pop(k)
                    datetime_as_str: str = _datetime_as_isostr(datetime_as_dt)  # pylint:disable=protected-access
                    notes[datetime_as_str] = v
                elif isinstance(k, datetime):
                    datetime_as_str: str = _datetime_as_isostr(k)  # pylint:disable=protected-access
                    notes.pop(k)
                    notes[datetime_as_str] = v
        super().__init__(
            channel_reference = channel_reference,
            channel_id = channel_id,
            classification_policy_id = classification_policy_id,
            queue_id = queue_id,
            priority = priority,
            disposition_code = disposition_code,
            requested_worker_selectors = requested_worker_selectors,
            notes = notes,
            labels = labels,
            tags = tags,
            **kwargs)


class RouterWorker(RouterWorkerGenerated):
    def __init__(
        self,
        *,
        queue_assignments: Optional[Dict[str, Union[QueueAssignment, JSON, None]]] = None,
        total_capacity: Optional[int] = None,
        labels: Optional[Dict[str, Union[int, float, str, bool, None]]] = None,
        tags: Optional[Dict[str, Union[int, float, str, bool, None]]] = None,
        channel_configurations: Optional[Dict[str, "_models.ChannelConfiguration"]] = None,
        available_for_offers: Optional[bool] = None,
        **kwargs
    ):
        if queue_assignments:
            for k, v in queue_assignments.items():
                if not isinstance(v, (MutableMapping, JSON, type(None))):
                    raise ValueError("tags only accept 'QueueAssignment', 'JSON' and 'NoneType' as values.")
        super().__init__(
            queue_assignments = queue_assignments,
            total_capacity = total_capacity,
            labels = labels,
            tags = tags,
            channel_configurations = channel_configurations,
            available_for_offers = available_for_offers,
            **kwargs)


__all__: List[str] = [
    "RouterWorker",
    "QueueAssignment",
    "DeclineJobOfferResult",
    "ReclassifyJobResult",
    "CancelJobResult",
    "CompleteJobResult",
    "CloseJobResult",
    "RouterJob",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
