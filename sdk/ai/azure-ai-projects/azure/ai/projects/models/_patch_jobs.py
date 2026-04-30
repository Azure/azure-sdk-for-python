# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customized job models."""

import datetime
import json
import yaml
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Union
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
        data["inputs"] = {key: Input(**val) if isinstance(val, dict) else val for key, val in inputs_data.items()}

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


class Diagnostic:
    """Represents a diagnostic of a job validation error with the location info."""

    def __init__(
        self,
        yaml_path: str,
        message: str,
        *,
        error_code: Optional[str] = None,
        value: Any = None,
    ) -> None:
        """Init Diagnostic.

        :keyword yaml_path: A dot-separated path from the root to the target element of the
            diagnostic, e.g. ``inputs.training_data.path``.
        :paramtype yaml_path: str
        :keyword message: Error message of the diagnostic.
        :paramtype message: str
        :keyword error_code: Error code of the diagnostic.
        :paramtype error_code: str
        :keyword value: The offending value, if relevant.
        :paramtype value: Any
        """
        self.yaml_path = yaml_path
        self.message = message
        self.error_code = error_code
        self.value = value

    def __repr__(self) -> str:
        """The yaml path and error message.

        :return: The formatted diagnostic
        :rtype: str
        """
        return "{}: {}".format(self.yaml_path, self.message)


class ValidationResult:
    """Represents the result of job validation.

    This class is used to organize and parse diagnostics from client-side validation
    before exposing them to the user.
    """

    _STATUS_SUCCEEDED = "Succeeded"
    _STATUS_FAILED = "Failed"

    def __init__(self) -> None:
        self.errors: List[Diagnostic] = []
        self.warnings: List[Diagnostic] = []

    @property
    def passed(self) -> bool:
        """Returns boolean indicating whether any errors were found.

        :return: True if the validation passed, False otherwise.
        :rtype: bool
        """
        return not self.errors

    @property
    def error_messages(self) -> Dict[str, str]:
        """Return all messages of errors in the validation result.

        :return: A dictionary of error messages. The key is the yaml path of the error,
            and the value is the error message. Multiple messages on the same path are
            joined with ``"; "``.
        :rtype: dict
        """
        messages: Dict[str, str] = {}
        for err in self.errors:
            if err.yaml_path in messages:
                messages[err.yaml_path] = messages[err.yaml_path] + "; " + err.message
            else:
                messages[err.yaml_path] = err.message
        return messages

    def append_error(
        self,
        yaml_path: str,
        message: str,
        *,
        error_code: Optional[str] = None,
        value: Any = None,
    ) -> "ValidationResult":
        """Add an error to the result.

        :param yaml_path: The yaml path of the error.
        :type yaml_path: str
        :param message: The error message.
        :type message: str
        :keyword error_code: Error code of the diagnostic.
        :paramtype error_code: str
        :keyword value: The offending value, if relevant.
        :paramtype value: Any
        :return: The current validation result.
        :rtype: ValidationResult
        """
        self.errors.append(Diagnostic(yaml_path, message, error_code=error_code, value=value))
        return self

    def append_warning(
        self,
        yaml_path: str,
        message: str,
        *,
        error_code: Optional[str] = None,
        value: Any = None,
    ) -> "ValidationResult":
        """Add a warning to the result.

        :param yaml_path: The yaml path of the warning.
        :type yaml_path: str
        :param message: The warning message.
        :type message: str
        :keyword error_code: Error code of the diagnostic.
        :paramtype error_code: str
        :keyword value: The offending value, if relevant.
        :paramtype value: Any
        :return: The current validation result.
        :rtype: ValidationResult
        """
        self.warnings.append(Diagnostic(yaml_path, message, error_code=error_code, value=value))
        return self

    def try_raise(self, *, raise_on_failure: bool = True) -> "ValidationResult":
        """Try to raise an error from the validation result.

        If the validation is passed or ``raise_on_failure`` is False, this method
        will return the validation result.

        :keyword raise_on_failure: Whether to raise the error.
        :paramtype raise_on_failure: bool
        :return: The current validation result.
        :rtype: ValidationResult
        :raises ValueError: If validation did not pass and ``raise_on_failure`` is True.
        """
        if raise_on_failure and not self.passed:
            raise ValueError(repr(self))
        return self

    def _to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {"result": self._STATUS_SUCCEEDED if self.passed else self._STATUS_FAILED}
        for diagnostic_type, diagnostics in [("errors", self.errors), ("warnings", self.warnings)]:
            messages = []
            for diagnostic in diagnostics:
                message: Dict[str, Any] = {"message": diagnostic.message, "path": diagnostic.yaml_path}
                if diagnostic.error_code is not None:
                    message["error_code"] = diagnostic.error_code
                if diagnostic.value is not None:
                    message["value"] = diagnostic.value
                messages.append(message)
            if messages:
                result[diagnostic_type] = messages
        return result

    def __repr__(self) -> str:
        """Get the string representation of the validation result.

        :return: The string representation
        :rtype: str
        """
        return json.dumps(self._to_dict(), indent=2)
