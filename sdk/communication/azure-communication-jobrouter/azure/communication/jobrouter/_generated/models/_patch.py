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
    JobQueue as JobQueueGenerated,
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
        notes: Dict[Union[str, datetime], str] = None,
        labels: Optional[Dict[str, Union[int, float, str, bool, None]]] = None,
        tags: Optional[Dict[str, Union[int, float, str, bool, None]]] = None,
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
        super().__init__(notes=notes, labels=labels, tags=tags, **kwargs)


class RouterWorker(RouterWorkerGenerated):
    def __init__(
        self,
        *,
        queue_assignments: Optional[Dict[str, Union[QueueAssignment, JSON, None]]] = None,
        labels: Optional[Dict[str, Union[int, float, str, bool, None]]] = None,
        tags: Optional[Dict[str, Union[int, float, str, bool, None]]] = None,
        **kwargs
    ):
        if queue_assignments:
            for k, v in queue_assignments.items():
                if not isinstance(v, (MutableMapping, JSON, type(None))):
                    raise ValueError("tags only accept 'QueueAssignment', 'JSON' and 'NoneType' as values.")
        super().__init__(queue_assignments=queue_assignments, labels=labels, tags=tags, **kwargs)


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
