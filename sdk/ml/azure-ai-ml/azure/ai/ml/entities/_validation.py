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
from azure.ai.ml.entities._job.pipeline._attr_dict import try_get_non_arbitrary_attr_for_potential_attr_dict
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict, decorate_validation_error
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
        return cls(
            yaml_path=yaml_path,
            message=message,
            error_code=error_code,
        )


class ValidationResult(object):
    """Represents the result of job/asset validation.

    This class is used to organize and parse diagnostics from both
    client & server side before expose them to users. In this way, we
    may improve user experience without changing the validation logic &
    API.
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
        self._errors: typing.List[Diagnostic] = diagnostics or []
        self._warnings: typing.List[Diagnostic] = []
        self._target_obj = data
        self._valid_data = valid_data

    @property
    def messages(self):
        messages = {}
        for diagnostic in self._errors:
            messages[diagnostic.yaml_path] = diagnostic.message
        return messages

    @property
    def invalid_fields(self):
        invalid_fields = []
        for diagnostic in self._errors:
            invalid_fields.append(diagnostic.yaml_path)
        return invalid_fields

    @property
    def passed(self):
        return not self._errors

    def merge_with(self, other: "ValidationResult", field_name: str = None, condition_skip: typing.Callable = None):
        """Merge two validation results.

        Will update current validation result.
        """
        for target_attr in ["_errors", "_warnings"]:
            for diagnostic in getattr(other, target_attr):
                if condition_skip and condition_skip(diagnostic):
                    continue
                new_diagnostic = copy.deepcopy(diagnostic)
                if field_name:
                    if new_diagnostic.yaml_path == "*":
                        new_diagnostic.yaml_path = field_name
                    else:
                        new_diagnostic.yaml_path = field_name + "." + new_diagnostic.yaml_path
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
    ) -> "ValidationResult":
        """Try to raise an error from the validation result.

        If the validation is passed or raise_error is False, this method
        will return the validation result.
        """
        # pylint: disable=logging-not-lazy
        if raise_error is False:
            return self

        if self._warnings:
            module_logger.info("Warnings: {}".format(self._warnings)) # pylint: disable=logging-format-interpolation

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
                no_personal_data_message="validation failed on the following fields: " + ", ".join(self.invalid_fields),
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
        self._errors.append(
            Diagnostic.create_instance(
                yaml_path=yaml_path,
                message=message,
                error_code=error_code,
            )
        )
        return self

    def resolve_location_for_diagnostics(self, source_path: str, resolve_value: bool = False):
        """Resolve location for diagnostics."""
        resolver = YamlLocationResolver(source_path)
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
        self._warnings.append(
            Diagnostic.create_instance(
                yaml_path=yaml_path,
                message=message,
                error_code=error_code,
            )
        )
        return self

    def _to_dict(self) -> typing.Dict[str, typing.Any]:
        result = {
            "result": OperationStatus.SUCCEEDED if self.passed else OperationStatus.FAILED,
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
                    "value": pydash.get(self._target_obj, diagnostic.yaml_path, diagnostic.value),
                }
                if diagnostic.local_path:
                    message["location"] = str(diagnostic.local_path)
                messages.append(message)
            if messages:
                result[diagnostic_type] = messages
        return result

    def __repr__(self):
        return json.dumps(self._to_dict(), indent=2)


class SchemaValidatableMixin:
    @classmethod
    def _create_empty_validation_result(cls) -> ValidationResult:
        """Simply create an empty validation result to reduce
        _ValidationResultBuilder importing, which is a private class."""
        return _ValidationResultBuilder.success()

    @classmethod
    def _create_schema_for_validation_with_base_path(cls, base_path=None):
        return cls._create_schema_for_validation(context={BASE_PATH_CONTEXT_KEY: base_path or Path.cwd()})

    @classmethod
    def _create_schema_for_validation(cls, context) -> typing.Union[PathAwareSchema, Schema]:
        """Create a schema of the resource with specific context. Should be
        overridden by subclass.

        return: The schema of the resource.
        return type: PathAwareSchema. PathAwareSchema will add marshmallow.Schema as super class on runtime.
        """
        raise NotImplementedError()

    @property
    def _base_path_for_validation(self) -> typing.Union[str, PathLike]:
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
    def _schema_for_validation(self) -> typing.Union[PathAwareSchema, Schema]:
        """Return the schema of this Resource with self._base_path as base_path
        of Schema. Do not override this method. Override _get_schema instead.

        return: The schema of the resource.
        return type: PathAwareSchema. PathAwareSchema will add marshmallow.Schema as super class on runtime.
        """
        return self._create_schema_for_validation_with_base_path(self._base_path_for_validation)

    def _dump_for_validation(self) -> typing.Dict:
        """Convert the resource to a dictionary."""
        return convert_ordered_dict_to_dict(self._schema_for_validation.dump(self))

    def _validate(self, raise_error=False) -> ValidationResult:
        """Validate the resource. If raise_error is True, raise ValidationError
        if validation fails and log warnings if applicable; Else, return the
        validation result.

        :param raise_error: Whether to raise ValidationError if validation fails.
        :type raise_error: bool
        return type: ValidationResult
        """
        result = self._schema_validate()
        result.merge_with(self._customized_validate())
        return result.try_raise(raise_error=raise_error, error_target=self._get_validation_error_target())

    def _customized_validate(self) -> ValidationResult:
        """Validate the resource with customized logic.

        Override this method to add customized validation logic.
        """
        return self._create_empty_validation_result()

    def _get_skip_fields_in_schema_validation(self) -> typing.List[str]:  # pylint: disable=no-self-use
        """Get the fields that should be skipped in schema validation.

        Override this method to add customized validation logic.
        """
        return []

    def _schema_validate(self) -> ValidationResult:
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
        return ValidationResult()

    @classmethod
    def from_single_message(cls, singular_error_message: str = None, yaml_path: str = "*", data: dict = None):
        """Create a validation result with only 1 diagnostic.

        param singular_error_message: diagnostic.message.
        param yaml_path: diagnostic.yaml_path. param data:
        serialized validation target.
        """
        obj = ValidationResult(data=data)
        if singular_error_message:
            obj.append_error(message=singular_error_message, yaml_path=yaml_path)
        return obj

    @classmethod
    def from_validation_error(cls, error: ValidationError, source_path: str = None):
        """Create a validation result from a ValidationError, which will be
        raised in marshmallow.Schema.load. Please use this function only for
        exception in loading file.

        param error: ValidationError raised by marshmallow.Schema.load.
        """
        obj = cls.from_validation_messages(error.messages, data=error.data)
        obj._valid_data = error.valid_data
        if source_path:
            obj.resolve_location_for_diagnostics(source_path, resolve_value=True)
        return obj

    @classmethod
    def from_validation_messages(cls, errors: typing.Dict, data: typing.Dict):
        """Create a validation result from error messages, which will be
        returned by marshmallow.Schema.validate.

        param errors: error message returned by
        marshmallow.Schema.validate. param data: serialized data to
        validate
        """
        instance = ValidationResult(data=data)
        errors = copy.deepcopy(errors)
        cls._from_validation_messages_recursively(errors, [], instance)
        return instance

    @classmethod
    def _from_validation_messages_recursively(cls, errors, path_stack, instance: ValidationResult):
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
                    cls._from_validation_messages_recursively(msgs, path_stack, instance)
                else:
                    path_stack.append(field)
                    cls._from_validation_messages_recursively(msgs, path_stack, instance)
                    path_stack.pop()
        # detailed error message
        elif isinstance(errors, list) and all(isinstance(msg, str) for msg in errors):
            if cls.UNKNOWN_MESSAGE in errors:
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
                if isinstance(msg, dict) and len(msg) == 1 and "_schema" in msg and len(msg["_schema"]) == 1:
                    return msg["_schema"][0]

                return str(msg)

            instance.append_error(message="; ".join([msg2str(x) for x in errors]), yaml_path=cur_path)
        # unknown error
        else:
            instance.append_error(message=str(errors), yaml_path=cur_path)


class YamlLocationResolver:
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
        return f"{source_path.resolve().absolute()}#line {loaded_yaml.start_line}", None if attrs else loaded_yaml.value
