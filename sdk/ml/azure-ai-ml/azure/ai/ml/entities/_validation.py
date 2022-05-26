# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import typing

from marshmallow import ValidationError
from azure.ai.ml._ml_exceptions import ValidationException
from typing import List

from azure.ai.ml.constants import OperationStatus


class DiagnosticDescriptor(object):
    """Detailed description of a Diagnostic, including error code & error message."""

    def __init__(self, message: str, error_code: str):
        """
        Create description about a Diagnostic.

        :param message: Error message of diagnostic.
        :type message: str
        :param error_code: Error code of diagnostic.
        :type error_code: str
        """
        self.message = message
        self.error_code = error_code


class DiagnosticLocation(object):
    """The location of diagnostic in Job or Asset.
    include 3 fields:
    - yaml_path: A dash path from root to the target element of the diagnostic. jobs.job_a.inputs.input_str, e.g.
    - asset_ids: A list of arm-ids of related remote assets.
    - local_path: The local path of the exact yaml file where the error is.
    """

    def __init__(
        self,
        yaml_path: str = None,
        asset_ids: List[str] = None,
        local_path: str = None,
    ):
        """
        Create diagnostic location of a validation result.

        :param yaml_path: A dash path from root to the target element of the diagnostic. jobs.job_a.inputs.input_str, e.g.
        :type yaml_path: str
        :param asset_ids: A list of arm-ids of related remote assets.
        :type asset_ids: List[str]
        :param local_path: The local path of the exact yaml file where the error is.
        :type local_path: str
        """
        self.yaml_path = yaml_path
        self.asset_ids = asset_ids
        self.local_path = local_path


class Diagnostic(object):
    """Represents a diagnostic of an asset validation error with the location info."""

    def __init__(self, location: DiagnosticLocation, descriptor: DiagnosticDescriptor):
        """
        Init Diagnostic.

        :param location: The location of diagnostic in Job or Asset.
        :type location: DiagnosticLocation
        :param descriptor: Description about a Diagnostic.
        :type descriptor: DiagnosticDescriptor
        """
        self.location = location
        self.descriptor = descriptor

    def __repr__(self):
        """Return the asset friendly name and error message."""
        return "{}: {}".format(self.location.yaml_path, self.descriptor.message)

    @classmethod
    def create_instance(
        cls,
        yaml_path: str,
        asset_ids: List[str] = None,
        local_path: str = None,
        message: str = None,
        error_code: str = None,
    ):
        return cls(
            DiagnosticLocation(yaml_path, asset_ids, local_path),
            DiagnosticDescriptor(message, error_code),
        )


class ValidationResult(object):
    """
    Represents the result of job/asset validation.
    This class is used to organize and parse diagnostics from both client & server side before expose them to users.
    In this way, we may improve user experience without changing the validation logic & API.
    """

    def __init__(
        self,
        diagnostics: typing.List[Diagnostic] = None,
        data: typing.Optional[
            typing.Union[
                typing.Mapping[str, typing.Any],
                typing.Iterable[typing.Mapping[str, typing.Any]],
            ]
        ] = None,
        valid_data: typing.Optional[
            typing.Union[
                typing.List[typing.Dict[str, typing.Any]],
                typing.Dict[str, typing.Any],
            ]
        ] = None,
    ):
        self.diagnostics: typing.List[Diagnostic] = diagnostics or []
        self.data = data
        self.valid_data = valid_data

    @property
    def messages(self):
        messages = {}
        for diagnostic in self.diagnostics:
            messages[diagnostic.location.yaml_path] = diagnostic.descriptor.message
        return messages

    @property
    def _single_message(self) -> str:
        if not self.messages:
            return ""
        if len(self.messages) == 1:
            for field, message in self.messages.items():
                if field == "*":
                    return message
                else:
                    return field + ": " + message
        else:
            return str(self.messages)

    @property
    def passed(self):
        return not self.diagnostics

    @classmethod
    def _create_instance(cls, singular_error_message: str = None, yaml_path: str = "*"):
        obj = cls()
        if singular_error_message:
            obj._append_diagnostic(message=singular_error_message, yaml_path=yaml_path)
        return obj

    @classmethod
    def _from_validation_error(cls, error: ValidationError):
        obj = cls._from_validation_messages(error.messages)
        obj.data = error.data
        obj.valid_data = error.valid_data
        return obj

    @classmethod
    def _from_validation_messages(cls, errors: typing.Dict):
        instance = cls()
        diagnostics = []
        unknown_msg = "Unknown field."
        errors = copy.deepcopy(errors)
        for field, msgs in errors.items():
            if unknown_msg in msgs:
                # TODO: should we log them instead of just ignore?
                msgs.remove(unknown_msg)
            if len(msgs) != 0:
                diagnostics.append(Diagnostic.create_instance(yaml_path=field, message=" ".join(msgs)))
        instance._extend_diagnostics(diagnostics)
        return instance

    def _extend_diagnostics(self, diagnostics: typing.List[Diagnostic]):
        self.diagnostics.extend(diagnostics)
        return self

    def _append_validation_exception(self, validation_exception: ValidationException, yaml_path: str = "*"):
        self._append_diagnostic(yaml_path=yaml_path, message=validation_exception.message)
        return self

    def _merge_with(self, other: "ValidationResult", field_name: str = None):
        for diagnostic in other.diagnostics:
            new_diagnostic = copy.deepcopy(diagnostic)
            if field_name:
                if new_diagnostic.location.yaml_path == "*":
                    new_diagnostic.location.yaml_path = field_name
                else:
                    new_diagnostic.location.yaml_path = field_name + "." + new_diagnostic.location.yaml_path
            self.diagnostics.append(new_diagnostic)
        return self

    def _append_diagnostic(
        self,
        yaml_path: str = "*",
        asset_ids: typing.List[str] = None,
        local_path: str = None,
        message: str = None,
        error_code: str = None,
    ):
        self.diagnostics.append(
            Diagnostic.create_instance(
                yaml_path=yaml_path, asset_ids=asset_ids, local_path=local_path, message=message, error_code=error_code
            )
        )
        return self

    def _to_dict(self):
        messages = []
        for field, message in self.messages.items():
            messages.append({"location": field, "message": message})
        return {
            "result": OperationStatus.SUCCEEDED if self.passed else OperationStatus.FAILED,
            "messages": self.messages,
        }
