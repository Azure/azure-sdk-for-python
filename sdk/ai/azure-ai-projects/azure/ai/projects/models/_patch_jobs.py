# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customized job models."""

import datetime
from typing import Any, Mapping, Optional, Union
from ._models import (
    CommandJob as _RestCommandJob,
    CommandJobLimits as _RestCommandJobLimits,
    Job as _RestJob,
    SystemData,
)


class CommandJob(_RestCommandJob):
    """A training job that runs a custom command.

    :ivar name: The name of the job. Read-only; populated after the job is created.
    :vartype name: str or None
    :ivar id: The resource ID of the job. Read-only; populated after the job is created.
    :vartype id: str or None
    :ivar system_data: Metadata pertaining to creation and last modification of the job.
    :vartype system_data: ~azure.ai.projects.models.SystemData or None
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._name: Optional[str] = None
        self._id: Optional[str] = None
        self._system_data: Optional[SystemData] = None

    @property
    def name(self) -> Optional[str]:
        """The name of the job."""
        return self._name

    @property
    def id(self) -> Optional[str]:
        """The resource ID of the job."""
        return self._id

    @property
    def system_data(self) -> Optional[SystemData]:
        """Metadata pertaining to creation and last modification of the job."""
        return self._system_data

    @classmethod
    def _from_rest_object(cls, rest_obj: Union[_RestJob, Any]) -> "CommandJob":
        """Construct a :class:`CommandJob` from a service response object.

        :param rest_obj: The deserialized response from the service.
        :returns: A :class:`CommandJob` with ``name``, ``id``, and ``system_data`` populated.
        :raises ValueError: If the job properties are missing.
        :raises TypeError: If the job is not a Command job.
        """
        props = rest_obj.properties
        if props is None:
            raise ValueError(
                "Cannot convert REST Job to CommandJob: Job.properties is None. "
                "Expected a CommandJob in the properties field."
            )
        if not isinstance(props, _RestCommandJob):
            raise TypeError(
                f"Cannot convert REST Job to CommandJob: expected properties of type "
                f"CommandJob, but got {type(props).__name__}. "
                f"Only Command jobs are supported by this method."
            )
        obj = cls(props)
        obj._name = rest_obj.name
        obj._id = rest_obj.id
        obj._system_data = rest_obj.system_data
        limits_obj = obj._data.get("limits")
        if isinstance(limits_obj, _RestCommandJobLimits) and limits_obj._data.get("timeout"):
            limits_obj._data["timeout"] = limits_obj.timeout
        return obj


class CommandJobLimits(_RestCommandJobLimits):

    def __init__(  # type: ignore[override]
        self,
        *args: Any,
        timeout: Optional[Union[int, float, datetime.timedelta]] = None,
        **kwargs: Any,
    ) -> None:
        if isinstance(timeout, (int, float)):
            timeout = datetime.timedelta(seconds=timeout)
        super().__init__(*args, timeout=timeout, **kwargs)

    @property  # type: ignore[override]
    def timeout(self) -> Optional[int]:  # type: ignore[override]
        """Maximum wall-clock run time in seconds."""
        val = super().timeout  # type: ignore[misc]
        if val is None:
            return None
        if isinstance(val, datetime.timedelta):
            return int(val.total_seconds())
        return int(val)


