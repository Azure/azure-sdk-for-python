# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import typing

import pydash
from marshmallow import ValidationError
from azure.ai.ml._ml_exceptions import ValidationException, ErrorTarget, ErrorCategory
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
        data: typing.Dict[str, typing.Any] = None,
        valid_data: typing.Optional[
            typing.Union[
                typing.List[typing.Dict[str, typing.Any]],
                typing.Dict[str, typing.Any],
            ]
        ] = None,
    ):
        self._diagnostics: typing.List[Diagnostic] = diagnostics or []
        self._warnings: typing.List[Diagnostic] = []
        self._target_obj = data
        self._valid_data = valid_data

    @property
    def messages(self):
        messages = {}
        for diagnostic in self._diagnostics:
            messages[diagnostic.location.yaml_path] = diagnostic.descriptor.message
        return messages

    @property
    def invalid_fields(self):
        invalid_fields = []
        for diagnostic in self._diagnostics:
            invalid_fields.append(diagnostic.location.yaml_path)
        return invalid_fields

    @property
    def invalid_data(self):
        if not self._target_obj:
            return {}
        return pydash.objects.pick(self._target_obj, *self.invalid_fields)

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
        return not self._diagnostics

    def merge_with(self, other: "ValidationResult", field_name: str = None):
        """
        Merge two validation results. Will update current validation result.
        """
        for diagnostic in other._diagnostics:
            new_diagnostic = copy.deepcopy(diagnostic)
            if field_name:
                if new_diagnostic.location.yaml_path == "*":
                    new_diagnostic.location.yaml_path = field_name
                else:
                    new_diagnostic.location.yaml_path = field_name + "." + new_diagnostic.location.yaml_path
            self._diagnostics.append(new_diagnostic)
        return self

    def try_raise(
        self,
        error_target: ErrorTarget,
        error_category: ErrorCategory = ErrorCategory.USER_ERROR,
        raise_error: bool = True,
    ) -> "ValidationResult":
        """
        Try to raise an error from the validation result.
        If the validation is passed or raise_error is False, this method will return the validation result.
        """
        if self.passed or raise_error is False:
            return self

        raise ValidationException(
            message=self._single_message,
            no_personal_data_message="validation failed on the following fields: " + ", ".join(self.invalid_fields),
            target=error_target,
            error_category=error_category,
        )

    def append_diagnostic(
        self,
        yaml_path: str = "*",
        asset_ids: typing.List[str] = None,
        local_path: str = None,
        message: str = None,
        error_code: str = None,
    ):
        self._diagnostics.append(
            Diagnostic.create_instance(
                yaml_path=yaml_path, asset_ids=asset_ids, local_path=local_path, message=message, error_code=error_code
            )
        )
        return self

    def _to_dict(self) -> typing.Dict[str, typing.Any]:
        messages = []
        for field, message in self.messages.items():
            messages.append(
                {
                    "location": field,
                    "value": pydash.get(self._target_obj, field, "NOT_FOUND"),
                    "message": message,
                }
            )
        result = {
            "result": OperationStatus.SUCCEEDED if self.passed else OperationStatus.FAILED,
            "messages": messages,
        }
        if self._warnings:
            result["warnings"] = self._warnings
        return result


class _ValidationResultBuilder:
    def __init__(self):
        pass

    @classmethod
    def success(cls):
        """
        Create a validation result with success status.
        """
        return cls.from_single_message()

    @classmethod
    def from_single_message(cls, singular_error_message: str = None, yaml_path: str = "*", data: dict = None):
        """
        Create a validation result with only 1 diagnostic.

        param singular_error_message: diagnostic.descriptor.message.
        param yaml_path: diagnostic.location.yaml_path.
        param data: serialized validation target.
        """
        obj = ValidationResult(data=data)
        if singular_error_message:
            obj.append_diagnostic(message=singular_error_message, yaml_path=yaml_path)
        return obj

    @classmethod
    def from_validation_error(cls, error: ValidationError):
        """
        Create a validation result from a ValidationError, which will be raised in marshmallow.Schema.load.
        """
        obj = cls.from_validation_messages(error.messages, data=error.data)
        obj._valid_data = error.valid_data
        return obj

    @classmethod
    def from_validation_messages(cls, errors: typing.Dict, data: typing.Dict = None):
        """
        Create a validation result from error messages, which will be returned by marshmallow.Schema.validate.
        """
        instance = ValidationResult(data=data)
        unknown_msg = "Unknown field."
        errors = copy.deepcopy(errors)
        for field, msgs in errors.items():
            if unknown_msg in msgs:
                # TODO: should we log them instead of just ignore?
                msgs.remove(unknown_msg)
            if len(msgs) != 0:

                def msg2str(msg):
                    if isinstance(msg, str):
                        return msg
                    elif isinstance(msg, dict) and len(msg) == 1 and "_schema" in msg and len(msg["_schema"]) == 1:
                        return msg["_schema"][0]
                    else:
                        return str(msg)

                instance.append_diagnostic(message="; ".join(map(lambda x: msg2str(x), msgs)), yaml_path=field)
        return instance
