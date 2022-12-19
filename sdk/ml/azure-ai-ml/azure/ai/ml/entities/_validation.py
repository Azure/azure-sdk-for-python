# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
import json
import logging
import os.path
import typing
from os import PathLike
from pathlib import Path
from typing import List

import pydash
import strictyaml
from marshmallow import Schema, ValidationError

from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, OperationStatus
from azure.ai.ml.entities._job.pipeline._attr_dict import (
    try_get_non_arbitrary_attr_for_potential_attr_dict,
)
from azure.ai.ml.entities._util import (
    convert_ordered_dict_to_dict,
    decorate_validation_error,
)
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException

module_logger = logging.getLogger(__name__)


class Diagnostic(object):
    """Represents a diagnostic of an asset validation error with the location
    info."""

    def __init__(self, yaml_path: str, message: str, error_code: str):
        """Init Diagnostic.

        :param yaml_path: A dash path from root to the target element of the diagnostic. jobs.job_a.inputs.input_str
        :type yaml_path: str
        :param message: Error message of diagnostic.
        :type message: str
        :param error_code: Error code of diagnostic.
        :type error_code: str
        """
        self.yaml_path = yaml_path
        self.message = message
        self.error_code = error_code
        self.local_path, self.value = None, None

    def __repr__(self):
        """Return the asset friendly name and error message."""
        return "{}: {}".format(self.yaml_path, self.message)

    @classmethod
    def create_instance(
        cls,
        yaml_path: str,
        message: str = None,
        error_code: str = None,
    ):
        """Create a diagnostic instance.

        :param yaml_path: A dash path from root to the target element of the diagnostic. jobs.job_a.inputs.input_str
        :type yaml_path: str
        :param message: Error message of diagnostic.
        :type message: str
        :param error_code: Error code of diagnostic.
        :type error_code: str
        """
        return cls(
            yaml_path=yaml_path,
            message=message,
            error_code=error_code,
        )


class ValidationResult(object):
    """Represents the result of job/asset validation.

    This class is used to organize and parse diagnostics from both
    client & server side before expose them.
    The result is immutable.
    """

    def __init__(self):
        self._target_obj = None
        self._errors = []
        self._warnings = []

    @property
    def error_messages(self):
        """Return all messages of errors in the validation result.
        For example, if repr(self) is:
        {
            "errors": [
                {
                    "path": "jobs.job_a.inputs.input_str",
                    "message": "input_str is required",
                    "value": None,
                },
                {
                    "path": "jobs.job_a.inputs.input_str",
                    "message": "input_str must be in the format of xxx",
                    "value": None,
                },
                {
                    "path": "settings.on_init",
                    "message": "On_init job name job_b not exists in jobs.",
                    "value": None,
                },
            ],
            "warnings": [
                {
                    "path": "jobs.job_a.inputs.input_str",
                    "message": "input_str is required",
                    "value": None,
                }
            ]
        }
        then the error_messages will be:
        {
            "jobs.job_a.inputs.input_str": "input_str is required; input_str must be in the format of xxx",
            "settings.on_init": "On_init job name job_b not exists in jobs.",
        }
        """
        messages = {}
        for diagnostic in self._errors:
            if diagnostic.yaml_path not in messages:
                messages[diagnostic.yaml_path] = diagnostic.message
            else:
                messages[diagnostic.yaml_path] += "; " + diagnostic.message
        return messages

    @property
    def passed(self):
        """Return whether the validation passed. If there is no error, then it passed."""
        return not self._errors

    def _to_dict(self) -> typing.Dict[str, typing.Any]:
        result = {
            "result": OperationStatus.SUCCEEDED
            if self.passed
            else OperationStatus.FAILED,
        }
        for diagnostic_type, diagnostics in [
            ("errors", self._errors),
            ("warnings", self._warnings),
        ]:
            messages = []
            for diagnostic in diagnostics:
                message = {
                    "message": diagnostic.message,
                    "path": diagnostic.yaml_path,
                    "value": pydash.get(
                        self._target_obj, diagnostic.yaml_path, diagnostic.value
                    ),
                }
                if diagnostic.local_path:
                    message["location"] = str(diagnostic.local_path)
                messages.append(message)
            if messages:
                result[diagnostic_type] = messages
        return result

    def __repr__(self):
        """Get the string representation of the validation result."""
        return json.dumps(self._to_dict(), indent=2)


class MutableValidationResult(ValidationResult):
    """Used by the client side to construct a validation result.
    The result is mutable and should not be exposed to the user.
    """

    def __init__(self, target_obj: typing.Dict[str, typing.Any] = None):
        super().__init__()
        self._target_obj = target_obj

    def merge_with(
        self,
        target: "MutableValidationResult",
        field_name: str = None,
        condition_skip: typing.Callable = None,
    ):
        """Merge errors & warnings in another validation results into current one.

        Will update current validation result.
        If field_name is not None, then yaml_path in the other validation result will be updated accordingly.
        * => field_name, jobs.job_a => field_name.jobs.job_a e.g.. If None, then no update.

        :param target: Validation result to merge.
        :type target: MutableValidationResult
        :param field_name: The base field name for the target to merge.
        :type field_name: str
        :param condition_skip: A function to determine whether to skip the merge of a diagnostic in the target.
        :type condition_skip: typing.Callable
        :return: The current validation result.
        :rtype: MutableValidationResult
        """
        for target_attr in ["_errors", "_warnings"]:
            for diagnostic in getattr(target, target_attr):
                if condition_skip and condition_skip(diagnostic):
                    continue
                new_diagnostic = copy.deepcopy(diagnostic)
                if field_name:
                    if new_diagnostic.yaml_path == "*":
                        new_diagnostic.yaml_path = field_name
                    else:
                        new_diagnostic.yaml_path = (
                            field_name + "." + new_diagnostic.yaml_path
                        )
                getattr(self, target_attr).append(new_diagnostic)
        return self

    def try_raise(
        self,
        error_target: ErrorTarget,
        error_category: ErrorCategory = ErrorCategory.USER_ERROR,
        raise_error: bool = True,
        schema: Schema = None,
        additional_message: str = "",
        raise_mashmallow_error: bool = False,
    ) -> "MutableValidationResult":
        """Try to raise an error from the validation result.

        If the validation is passed or raise_error is False, this method
        will return the validation result.

        :param error_target: The target of the error.
        :type error_target: ErrorTarget
        :param error_category: The category of the error.
        :type error_category: ErrorCategory
        :param raise_error: Whether to raise the error.
        :type raise_error: bool
        :param schema: The schema to do the validation, will be used in the error message.
        :type schema: Schema
        :param additional_message: Additional message to add to the error message.
        :type additional_message: str
        :param raise_mashmallow_error: Whether to raise a marshmallow.ValidationError instead of ValidationException.
        :type raise_mashmallow_error: bool
        :return: The current validation result.
        :rtype: MutableValidationResult
        """
        # pylint: disable=logging-not-lazy
        if raise_error is False:
            return self

        if self._warnings:
            module_logger.info("Warnings: %s" % str(self._warnings))

        if not self.passed:
            message = (
                decorate_validation_error(
                    schema=schema.__class__,
                    pretty_error=self.__repr__(),
                    additional_message=additional_message,
                )
                if schema
                else self.__repr__()
            )
            if raise_mashmallow_error:
                raise ValidationError(message)

            raise ValidationException(
                message=message,
                no_personal_data_message="validation failed on the following fields: "
                + ", ".join(self.error_messages),
                target=error_target,
                error_category=error_category,
            )
        return self

    def append_error(
        self,
        yaml_path: str = "*",
        message: str = None,
        error_code: str = None,
    ):
        """Append an error to the validation result.

        :param yaml_path: The yaml path of the error.
        :type yaml_path: str
        :param message: The message of the error.
        :type message: str
        :param error_code: The error code of the error.
        :type error_code: str
        :return: The current validation result.
        :rtype: MutableValidationResult
        """
        self._errors.append(
            Diagnostic.create_instance(
                yaml_path=yaml_path,
                message=message,
                error_code=error_code,
            )
        )
        return self

    def resolve_location_for_diagnostics(
        self, source_path: str, resolve_value: bool = False
    ):
        """Resolve location/value for diagnostics based on the source path where the validatable object is loaded.
        Location includes local path of the exact file (can be different from the source path) & line number of the
        invalid field.
        Value of a diagnostic is resolved from the validatable object in transfering to a dict by default;
        however, when the validatable object is not available for the validation result, validation result is created
        from marshmallow.ValidationError.messages e.g., it can be resolved from the source path.

        param source_path: The path of the source file.
        type source_path: str
        param resolve_value: Whether to resolve the value of the invalid field from source file.
        type resolve_value: bool
        """
        resolver = _YamlLocationResolver(source_path)
        for diagnostic in self._errors + self._warnings:
            diagnostic.local_path, value = resolver.resolve(diagnostic.yaml_path)
            if value is not None and resolve_value:
                diagnostic.value = value

    def append_warning(
        self,
        yaml_path: str = "*",
        message: str = None,
        error_code: str = None,
    ):
        """Append a warning to the validation result.

        :param yaml_path: The yaml path of the warning.
        :type yaml_path: str
        :param message: The message of the warning.
        :type message: str
        :param error_code: The error code of the warning.
        :type error_code: str
        :return: The current validation result.
        :rtype: MutableValidationResult
        """
        self._warnings.append(
            Diagnostic.create_instance(
                yaml_path=yaml_path,
                message=message,
                error_code=error_code,
            )
        )
        return self


class SchemaValidatableMixin:
    @classmethod
    def _create_empty_validation_result(cls) -> MutableValidationResult:
        """Simply create an empty validation result to reduce
        _ValidationResultBuilder importing, which is a private class."""
        return _ValidationResultBuilder.success()

    @classmethod
    def _create_schema_for_validation_with_base_path(cls, base_path=None):
        return cls._create_schema_for_validation(
            context={BASE_PATH_CONTEXT_KEY: base_path or Path.cwd()}
        )

    @classmethod
    def _create_schema_for_validation(
        cls, context
    ) -> PathAwareSchema:
        """Create a schema of the resource with specific context. Should be
        overridden by subclass.

        return: The schema of the resource.
        return type: PathAwareSchema. PathAwareSchema will add marshmallow.Schema as super class on runtime.
        """
        raise NotImplementedError()

    @property
    def __base_path_for_validation(self) -> typing.Union[str, PathLike]:
        """Get the base path of the resource. It will try to return
        self.base_path, then self._base_path, then Path.cwd() if above attrs
        are non-existent or None.

        return type: str
        """
        return (
            try_get_non_arbitrary_attr_for_potential_attr_dict(self, "base_path")
            or try_get_non_arbitrary_attr_for_potential_attr_dict(self, "_base_path")
            or Path.cwd()
        )

    @classmethod
    def _get_validation_error_target(cls) -> ErrorTarget:
        """Return the error target of this resource.

        Should be overridden by subclass. Value should be in ErrorTarget
        enum.
        """
        raise NotImplementedError()

    @property
    def _schema_for_validation(self) -> PathAwareSchema:
        """Return the schema of this Resource with self._base_path as base_path
        of Schema. Do not override this method. Override _get_schema instead.

        return: The schema of the resource.
        return type: PathAwareSchema. PathAwareSchema will add marshmallow.Schema as super class on runtime.
        """
        return self._create_schema_for_validation_with_base_path(
            self.__base_path_for_validation
        )

    def _dump_for_validation(self) -> typing.Dict:
        """Convert the resource to a dictionary."""
        return convert_ordered_dict_to_dict(self._schema_for_validation.dump(self))

    def _validate(self, raise_error=False) -> MutableValidationResult:
        """Validate the resource. If raise_error is True, raise ValidationError
        if validation fails and log warnings if applicable; Else, return the
        validation result.

        :param raise_error: Whether to raise ValidationError if validation fails.
        :type raise_error: bool
        return type: ValidationResult
        """
        result = self.__schema_validate()
        result.merge_with(self._customized_validate())
        return result.try_raise(
            raise_error=raise_error, error_target=self._get_validation_error_target()
        )

    def _customized_validate(self) -> MutableValidationResult:
        """Validate the resource with customized logic.

        Override this method to add customized validation logic.
        """
        return self._create_empty_validation_result()

    @classmethod
    def _get_skip_fields_in_schema_validation(
        cls,
    ) -> typing.List[str]:  # pylint: disable=no-self-use
        """Get the fields that should be skipped in schema validation.

        Override this method to add customized validation logic.
        """
        return []

    def __schema_validate(self) -> MutableValidationResult:
        """Validate the resource with the schema.

        return type: ValidationResult
        """
        data = self._dump_for_validation()
        messages = self._schema_for_validation.validate(data)
        for skip_field in self._get_skip_fields_in_schema_validation():
            if skip_field in messages:
                del messages[skip_field]
        return _ValidationResultBuilder.from_validation_messages(messages, data=data)


class _ValidationResultBuilder:
    UNKNOWN_MESSAGE = "Unknown field."

    def __init__(self):
        pass

    @classmethod
    def success(cls):
        """Create a validation result with success status."""
        return MutableValidationResult()

    @classmethod
    def from_single_message(
        cls, singular_error_message: str = None, yaml_path: str = "*", data: dict = None
    ):
        """Create a validation result with only 1 diagnostic.

        param singular_error_message: diagnostic.message.
        param yaml_path: diagnostic.yaml_path. param data:
        serialized validation target.
        """
        obj = MutableValidationResult(target_obj=data)
        if singular_error_message:
            obj.append_error(message=singular_error_message, yaml_path=yaml_path)
        return obj

    @classmethod
    def from_validation_error(
        cls,
        error: ValidationError,
        *,
        source_path: str = None,
        error_on_unknown_field=False
    ):
        """Create a validation result from a ValidationError, which will be
        raised in marshmallow.Schema.load. Please use this function only for
        exception in loading file.

        param error: ValidationError raised by marshmallow.Schema.load.
        type error: ValidationError
        param error_on_unknown_field: whether to raise error if there
        are unknown field diagnostics.
        type error_on_unknown_field: bool
        """
        obj = cls.from_validation_messages(
            error.messages, data=error.data,
            error_on_unknown_field=error_on_unknown_field
        )
        if source_path:
            obj.resolve_location_for_diagnostics(source_path, resolve_value=True)
        return obj

    @classmethod
    def from_validation_messages(
        cls,
        errors: typing.Dict,
        data: typing.Dict,
        *,
        error_on_unknown_field: bool = False
    ):
        """Create a validation result from error messages, which will be
        returned by marshmallow.Schema.validate.

        param errors: error message returned by
        marshmallow.Schema.validate.
        type errors: dict
        param data: serialized data to validate
        type data: dict
        param error_on_unknown_field: whether to raise error if there
        are unknown field diagnostics.
        type error_on_unknown_field: bool
        """
        instance = MutableValidationResult(target_obj=data)
        errors = copy.deepcopy(errors)
        cls._from_validation_messages_recursively(
            errors, [], instance, error_on_unknown_field=error_on_unknown_field
        )
        return instance

    @classmethod
    def _from_validation_messages_recursively(
        cls,
        errors: typing.Union[typing.Dict, typing.List, str],
        path_stack: typing.List[str],
        instance: MutableValidationResult,
        error_on_unknown_field: bool,
    ):
        cur_path = ".".join(path_stack) if path_stack else "*"
        # single error message
        if isinstance(errors, dict) and "_schema" in errors:
            instance.append_error(
                message=";".join(errors["_schema"]),
                yaml_path=cur_path,
            )
        # errors on attributes
        elif isinstance(errors, dict):
            for field, msgs in errors.items():
                # fields.Dict
                if field in ["key", "value"]:
                    cls._from_validation_messages_recursively(
                        msgs, path_stack, instance, error_on_unknown_field
                    )
                else:
                    path_stack.append(field)
                    cls._from_validation_messages_recursively(
                        msgs, path_stack, instance, error_on_unknown_field
                    )
                    path_stack.pop()
        # detailed error message
        elif isinstance(errors, list) and all(isinstance(msg, str) for msg in errors):
            if cls.UNKNOWN_MESSAGE in errors and not error_on_unknown_field:
                # Unknown field is not a real error, so we should remove it and append a warning.
                errors.remove(cls.UNKNOWN_MESSAGE)
                instance.append_warning(message=cls.UNKNOWN_MESSAGE, yaml_path=cur_path)
            if errors:
                instance.append_error(message=";".join(errors), yaml_path=cur_path)
        # union field
        elif isinstance(errors, list):

            def msg2str(msg):
                if isinstance(msg, str):
                    return msg
                if (
                    isinstance(msg, dict)
                    and len(msg) == 1
                    and "_schema" in msg
                    and len(msg["_schema"]) == 1
                ):
                    return msg["_schema"][0]

                return str(msg)

            instance.append_error(
                message="; ".join([msg2str(x) for x in errors]), yaml_path=cur_path
            )
        # unknown error
        else:
            instance.append_error(message=str(errors), yaml_path=cur_path)


class _YamlLocationResolver:
    def __init__(self, source_path):
        self._source_path = source_path

    def resolve(self, yaml_path, source_path=None):
        """Resolve the location & value of a yaml path starting from source_path.

        :param yaml_path: yaml path.
        :type yaml_path: str
        :param source_path: source path.
        :type source_path: str
        :return: the location & value of the yaml path based on source_path.
        :rtype: Tuple[str, str]
        """
        source_path = source_path or self._source_path
        if source_path is None or not os.path.isfile(source_path):
            return None, None
        if yaml_path is None or yaml_path == "*":
            return source_path, None

        attrs = yaml_path.split(".")
        attrs.reverse()

        return self._resolve_recursively(attrs, Path(source_path))

    def _resolve_recursively(self, attrs: List[str], source_path: Path):
        with open(source_path, encoding="utf-8") as f:
            try:
                loaded_yaml = strictyaml.load(f.read())
            except strictyaml.exceptions.StrictYAMLError as e:
                return "can't resolve location:\n{}".format(e).split("\n"), None

        while attrs:
            attr = attrs[-1]
            if loaded_yaml.is_mapping() and attr in loaded_yaml:
                loaded_yaml = loaded_yaml.get(attr)
                attrs.pop()
            else:
                try:
                    # if current object is a path of a valid yaml file, try to resolve location in new source file
                    next_path = Path(loaded_yaml.value)
                    if not next_path.is_absolute():
                        next_path = source_path.parent / next_path
                    if next_path.is_file():
                        return self._resolve_recursively(attrs, source_path=next_path)
                except OSError:
                    pass
                except TypeError:
                    pass
                # if not, return current section
                break
        return (
            f"{source_path.resolve().absolute()}#line {loaded_yaml.start_line}",
            None if attrs else loaded_yaml.value,
        )
