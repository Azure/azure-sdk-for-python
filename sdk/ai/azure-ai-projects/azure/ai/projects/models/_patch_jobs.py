# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customized job models."""

import datetime
import yaml
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Optional, Union
from ._models import (
    CommandJob as _RestCommandJob,
    CommandJobLimits as _RestCommandJobLimits,
    Input,
    Job as _RestJob,
    JobResourceConfiguration,
    MpiDistribution,
    PyTorchDistribution,
    QueueSettings,
    SystemData,
    TensorFlowDistribution,
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
        self._base_path: Optional[Union[str, PathLike[str]]] = None

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


def _load_command_job(data: dict, base_dir: Optional[Path] = None) -> CommandJob:
    limits_data = data.pop("limits", None)
    if isinstance(limits_data, dict):
        data["limits"] = CommandJobLimits(**limits_data)

    resources_data = data.pop("resources", None)
    if isinstance(resources_data, dict):
        data["resources"] = JobResourceConfiguration(**resources_data)

    queue_data = data.pop("queue_settings", None)
    if isinstance(queue_data, dict):
        data["queue_settings"] = QueueSettings(**queue_data)

    dist_data = data.pop("distribution", None)
    if isinstance(dist_data, dict):
        dist_type = dist_data.pop("type", "").lower()
        if dist_type == "pytorch":
            data["distribution"] = PyTorchDistribution(**dist_data)
        elif dist_type == "mpi":
            data["distribution"] = MpiDistribution(**dist_data)
        elif dist_type == "tensorflow":
            data["distribution"] = TensorFlowDistribution(**dist_data)

    inputs_data = data.pop("inputs", None)
    if isinstance(inputs_data, dict):
        data["inputs"] = {
            key: Input(**val) if isinstance(val, dict) else val for key, val in inputs_data.items()
        }

    job = CommandJob(**data)
    job._base_path = base_dir
    return job


def load_job(source: Union[str, "PathLike[str]", IO[AnyStr]]) -> CommandJob:
    """Load a job object from a YAML file.

    The YAML ``type`` field determines which job class is returned.
    Currently supported types: ``command`` (default).

    :param source: Path to a YAML file or an already-open file object.
    :type source: str or os.PathLike or IO
    :returns: A job object populated from the YAML content.
    :rtype: ~azure.ai.projects.models.CommandJob
    :raises ValueError: If the ``type`` field specifies an unsupported job type.
    """
    if hasattr(source, "read"):
        data: dict = yaml.safe_load(source)  # type: ignore[arg-type]
        source_name = getattr(source, "name", None)
        base_dir: Optional[Path] = Path(source_name).resolve().parent if source_name else None
    else:
        source_path = Path(source)  # type: ignore[arg-type]
        base_dir = source_path.resolve().parent
        with open(source_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

    data.pop("$schema", None)

    job_type_str = data.pop("type", "command")
    if isinstance(job_type_str, str):
        job_type_str = job_type_str.lower()

    if job_type_str == "command":
        return _load_command_job(data, base_dir=base_dir)
    raise ValueError(f"Unsupported job type: '{job_type_str}'. Supported types: ['command']")
