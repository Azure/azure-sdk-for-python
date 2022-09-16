# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import traceback
from enum import Enum
from typing import Dict, Tuple, Union

from colorama import Fore, init
from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml.constants._common import (
    DATASTORE_SCHEMA_TYPES,
    SCHEMA_VALIDATION_ERROR_TEMPLATE,
    YAML_CREATION_ERROR_DESCRIPTION,
)
from azure.core.exceptions import AzureError

module_logger = logging.getLogger(__name__)


class ValidationErrorType(Enum):
    """
    Error types to be specified when using ValidationException class.
    Types are then used in raise_error.py to format a detailed error message for users.

    When using ValidationException, specify the type that best describes the nature of the error being captured.
    If no type fits, add a new enum here and update raise_error.py to handle it.

    INVALID_VALUE -> One or more schema fields are invalid (e.g. incorrect type or format)
    UNKNOWN_FIELD -> A least one unrecognized schema parameter is specified
    MISSING_FIELD -> At least one required schema parameter is missing
    FILE_OR_FOLDER_NOT_FOUND -> One or more files or folder paths do not exist
    CANNOT_SERIALIZE -> Same as "Cannot dump". One or more fields cannot be serialized by marshmallow.
    CANNOT_PARSE -> YAML file cannot be parsed
    RESOURCE_NOT_FOUND -> Resource could not be found
    GENERIC -> Undefined placeholder. Avoid using.
    """

    INVALID_VALUE = "INVALID VALUE"
    UNKNOWN_FIELD = "UNKNOWN FIELD"
    MISSING_FIELD = "MISSING FIELD"
    FILE_OR_FOLDER_NOT_FOUND = "FILE OR FOLDER NOT FOUND"
    CANNOT_SERIALIZE = "CANNOT DUMP"
    CANNOT_PARSE = "CANNOT PARSE"
    RESOURCE_NOT_FOUND = "RESOURCE NOT FOUND"
    GENERIC = "GENERIC"


class ErrorCategory:

    USER_ERROR = "UserError"
    SYSTEM_ERROR = "SystemError"
    UNKNOWN = "Unknown"


class ErrorTarget:

    BATCH_ENDPOINT = "BatchEndpoint"
    BATCH_DEPLOYMENT = "BatchDeployment"
    LOCAL_ENDPOINT = "LocalEndpoint"
    CODE = "Code"
    COMPONENT = "Component"
    DATA = "Data"
    ENVIRONMENT = "Environment"
    JOB = "Job"
    COMMAND_JOB = "CommandJob"
    SPARK_JOB = "SparkJob"
    LOCAL_JOB = "LocalJob"
    MODEL = "Model"
    ONLINE_DEPLOYMENT = "OnlineDeployment"
    ONLINE_ENDPOINT = "OnlineEndpoint"
    ASSET = "Asset"
    DATASTORE = "Datastore"
    WORKSPACE = "Workspace"
    COMPUTE = "Compute"
    DEPLOYMENT = "Deployment"
    ENDPOINT = "Endpoint"
    AUTOML = "AutoML"
    PIPELINE = "Pipeline"
    SWEEP_JOB = "SweepJob"
    GENERAL = "General"
    IDENTITY = "Identity"
    ARM_DEPLOYMENT = "ArmDeployment"
    ARM_RESOURCE = "ArmResource"
    ARTIFACT = "Artifact"
    SCHEDULE = "Schedule"
    UNKNOWN = "Unknown"


class MlException(AzureError):
    """
    The base class for all exceptions raised in AzureML SDK code base. If there is a need to define a custom exception type,
    that custom exception type should extend from this class.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data. This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    :param error: The original exception if any.
    :type error: Exception
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        self._error_category = error_category
        self._target = target
        self._no_personal_data_message = no_personal_data_message
        super().__init__(message, *args, **kwargs)

    @property
    def target(self):
        """Return the error target.

        :return: The error target.
        :rtype: ErrorTarget
        """
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    @property
    def no_personal_data_message(self):
        """Return the error message with no personal data.

        :return: No personal data error message.
        :rtype: str
        """
        return self._no_personal_data_message

    @no_personal_data_message.setter
    def no_personal_data_message(self, value):
        self._no_personal_data_message = value

    @property
    def error_category(self):
        """Return the error category.

        :return: The error category.
        :rtype: ErrorCategory
        """
        return self._error_category

    @error_category.setter
    def error_category(self, value):
        self._error_category = value


class DeploymentException(MlException):
    """
    Class for all exceptions related to Deployments.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(DeploymentException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ComponentException(MlException):
    """
    Class for all exceptions related to Components.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(ComponentException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class JobException(MlException):
    """
    Class for all exceptions related to Jobs.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(JobException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ModelException(MlException):
    """
    Class for all exceptions related to Models.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(ModelException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class AssetException(MlException):
    """
    Class for all exceptions related to Assets.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(AssetException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ScheduleException(MlException):
    """
    Class for all exceptions related to Job Schedules.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        *args,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        **kwargs,
    ):
        super(ScheduleException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


class ValidationException(MlException):
    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        error_type: ValidationErrorType = ValidationErrorType.GENERIC,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.USER_ERROR,
        *args,
        **kwargs,
    ):
        """
        Class for all exceptions raised as part of client-side schema validation.

        :param message: A message describing the error. This is the error message the user will see.
        :type message: str
        :param no_personal_data_message: The error message without any personal data.
            This will be pushed to telemetry logs.
        :type no_personal_data_message: str
        :param error_type: The error type, chosen from one of the values of ValidationErrorType enum class.
        :type error_type: ValidationErrorType
        :param target: The name of the element that caused the exception to be thrown.
        :type target: ErrorTarget
        :param error_category: The error category, defaults to Unknown.
        :type error_category: ErrorCategory
        :param error: The original exception if any.
        :type error: Exception
        """
        super(ValidationException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )

        if error_type in list(ValidationErrorType):
            self._error_type = error_type
        else:
            raise Exception(f"Error type {error_type} is not a member of the ValidationErrorType enum class.")

    @property
    def error_type(self):
        """Return the error type.

        :return: The error type.
        :rtype: ValidationErrorType
        """
        return self._error_type

    @error_type.setter
    def error_type(self, value):
        self._error_type = value


class AssetPathException(MlException):
    """
    Class for the exception raised when an attempt is made to update the path of an existing asset. Asset paths are immutable.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param no_personal_data_message: The error message without any personal data.
        This will be pushed to telemetry logs.
    :type no_personal_data_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ErrorTarget
    :param error_category: The error category, defaults to Unknown.
    :type error_category: ErrorCategory
    """

    def __init__(
        self,
        message: str,
        no_personal_data_message: str,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        *args,
        **kwargs,
    ):
        super(AssetPathException, self).__init__(
            message=message,
            target=target,
            error_category=error_category,
            no_personal_data_message=no_personal_data_message,
            *args,
            **kwargs,
        )


def _find_deepest_dictionary(data):
    """
    Find deepest dictionary in nested dictionary.
    Used here to get nested error message. Can't be in utils.py due to circular import.
    """
    if not any([isinstance(data.get(key), dict) for key in data]):
        return data
    for key in data:
        if isinstance(data.get(key), dict):
            return _find_deepest_dictionary(data.get(key))


def get_entity_type(error: Union[SchemaValidationError, ValidationException]) -> Tuple[str, str]:
    """Get entity name from schema type referenced in the error."""
    details = ""

    error_name = error.exc_msg if hasattr(error, "exc_msg") else error.split(":")[0]
    if isinstance(error, ValidationException):
        entity_type = error.target
    else:
        details += error_name + "\n"
        if "DataSchema" in error_name:
            entity_type = ErrorTarget.DATA
        elif "ModelSchema" in error_name:
            entity_type = ErrorTarget.MODEL
        elif "EnvironmentSchema" in error_name:
            entity_type = ErrorTarget.ENVIRONMENT
        elif "CodeAssetSchema" in error_name:
            entity_type = ErrorTarget.CODE
        elif any([x in error_name for x in DATASTORE_SCHEMA_TYPES]):
            entity_type = ErrorTarget.DATASTORE
        elif "BaseJobSchema" in error_name:
            entity_type = ErrorTarget.JOB
        elif "CommandSchema" in error_name:
            entity_type = ErrorTarget.COMMAND_JOB
        elif "CommandJobSchema" in error_name:
            entity_type = ErrorTarget.COMMAND_JOB
        elif "SweepSchema" in error_name:
            entity_type = ErrorTarget.SWEEP_JOB
        elif "SweepJobSchema" in error_name:
            entity_type = ErrorTarget.SWEEP_JOB
        elif "AutoMLJobSchema" in error_name:
            entity_type = ErrorTarget.AUTOML
        else:
            raise NotImplementedError()

    return entity_type, details


def format_details_section(
    error: Union[SchemaValidationError, ValidationException], details: str, entity_type: str
) -> Tuple[Dict[str, bool], str]:
    """Builds strings for details of the error message template's Details section."""

    error_types = {
        ValidationErrorType.INVALID_VALUE: False,
        ValidationErrorType.UNKNOWN_FIELD: False,
        ValidationErrorType.MISSING_FIELD: False,
        ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND: False,
        ValidationErrorType.CANNOT_SERIALIZE: False,
        ValidationErrorType.CANNOT_PARSE: False,
        ValidationErrorType.RESOURCE_NOT_FOUND: False,
    }

    if hasattr(error, "message"):
        error_types[error.error_type] = True
        details += f"\n\n{error.message}\n"
    else:
        if (
            entity_type == ErrorTarget.COMMAND_JOB
        ):  # Command Job errors require different parsing because they're using ValidationResult.
            # This separate treatment will be unnecessary once
            # task https://msdata.visualstudio.com/Vienna/_workitems/edit/1925982/ is resolved.
            parsed_error_msg = error[error.find("{") : (error.rfind("}") + 1)]
            error_msg = json.loads(parsed_error_msg).get("errors")[0].get("message")
            error_msg = error_msg[error_msg.find("{") : (error_msg.rfind("}") + 1)]
            error_msg = error_msg[: (error_msg.rfind("}") + 1)]
            error_msg = json.loads(error_msg)
        else:
            parsed_error_msg = error[error.find("{") : (error.rfind("}") + 1)]
            error_msg = json.loads(parsed_error_msg)

        for field, field_error in zip(error_msg.keys(), error_msg.values()):
            try:
                field_error = field_error[0]
            except KeyError:
                error_msg = _find_deepest_dictionary(field_error)
                if entity_type not in [ErrorTarget.PIPELINE, ErrorTarget.COMMAND_JOB]:
                    field = list(error_msg.keys())[0]
                field_error = list(error_msg.values())[0][0]
            field_error_string = str(field_error)

            if not error_types[ValidationErrorType.INVALID_VALUE] and any(
                s in field_error_string for s in ["Not a valid", "is not in set"]
            ):
                error_types[ValidationErrorType.INVALID_VALUE] = True
            if not error_types[ValidationErrorType.UNKNOWN_FIELD] and "Unknown field" in field_error_string:
                error_types[ValidationErrorType.UNKNOWN_FIELD] = True
            if (
                not error_types[ValidationErrorType.MISSING_FIELD]
                and "Missing data for required field" in field_error_string
            ):
                error_types[ValidationErrorType.MISSING_FIELD] = True
            if (
                not error_types[ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND]
                and "No such file or directory" in field_error_string
            ):
                error_types[ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND] = True
            if not error_types[ValidationErrorType.CANNOT_SERIALIZE] and "Cannot dump" in field_error_string:
                error_types[ValidationErrorType.CANNOT_SERIALIZE] = True
            if (
                not error_types[ValidationErrorType.CANNOT_PARSE]
                and "Error while parsing yaml file" in field_error_string
            ):
                error_types[ValidationErrorType.CANNOT_PARSE] = True

            if isinstance(field_error, dict):
                field_error = f"{list(field_error.keys())[0]}:\n    - {list(field_error.values())[0][0]}"

            details += f"\n{field}:\n- {field_error}\n"

    return error_types, details


def format_errors_and_resolutions_sections(entity_type: str, error_types: Dict[str, bool]) -> Tuple[str, str]:
    """Builds strings for details of the error message template's Errors and Resolutions sections."""

    resolutions = ""
    errors = ""
    count = 1

    if error_types[ValidationErrorType.INVALID_VALUE]:
        errors += f"\n{count}) One or more fields are invalid"
        resolutions += f"Double-check that all specified parameters are of the correct types and formats \
        prescribed by the {entity_type} schema.\n"
        count += 1
    if error_types[ValidationErrorType.UNKNOWN_FIELD]:
        errors += f"\n{count}) A least one unrecognized parameter is specified"
        resolutions += f"Remove any parameters not prescribed by the {entity_type} schema.\n"
        count += 1
    if error_types[ValidationErrorType.MISSING_FIELD]:
        errors += f"\n{count}) At least one required parameter is missing"
        resolutions += f"Ensure all parameters required by the {entity_type} schema are specified.\n"
        count += 1
    if error_types[ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND]:
        errors += f"\n{count}) One or more files or folders do not exist.\n"
        resolutions += "Double-check the directory paths you provided and enter the correct paths.\n"
        count += 1
    if error_types[ValidationErrorType.CANNOT_SERIALIZE]:
        errors += f"\n{count}) One or more fields cannot be serialized.\n"
        resolutions += f"Double-check that all specified parameters are of the correct types and formats \
        prescribed by the {entity_type} schema.\n"
        count += 1
    if error_types[ValidationErrorType.CANNOT_PARSE]:
        errors += f"\n{count}) YAML file cannot be parsed.\n"
        resolutions += "Double-check your YAML file for syntax and formatting errors.\n"
        count += 1
    if error_types[ValidationErrorType.RESOURCE_NOT_FOUND]:
        errors += f"\n{count}) Resource was not found.\n"
        resolutions += "Double-check that the resource has been specified correctly and that you have access to it.\n"
        count += 1

    return errors, resolutions


def format_create_validation_error(
    error: Union[SchemaValidationError, ValidationException], yaml_operation: bool
) -> str:
    """
    Formats a detailed error message for validation errors.
    """
    entity_type, details = get_entity_type(error)
    error_types, details = format_details_section(error, details, entity_type)
    errors, resolutions = format_errors_and_resolutions_sections(entity_type, error_types)
    description = YAML_CREATION_ERROR_DESCRIPTION.format(entity_type=entity_type) if yaml_operation else ""
    formatted_error = SCHEMA_VALIDATION_ERROR_TEMPLATE.format(
        description=description,
        error_msg=errors,
        parsed_error_details=details,
        resolutions=resolutions,
    )

    formatted_error = Fore.RED + formatted_error + Fore.RESET
    return formatted_error


def log_and_raise_error(error, debug=False, yaml_operation=False):
    init()

    # use an f-string to automatically call str() on error
    if debug:
        module_logger.error(traceback.print_exc())

    if isinstance(error, SchemaValidationError):
        module_logger.debug(traceback.format_exc())

        try:
            formatted_error = format_create_validation_error(error.messages[0], yaml_operation=yaml_operation)
        except NotImplementedError:
            formatted_error = error
    elif isinstance(error, ValidationException):
        module_logger.debug(traceback.format_exc())
        try:
            if error.error_type == ValidationErrorType.GENERIC:
                formatted_error = error
            else:
                formatted_error = format_create_validation_error(error, yaml_operation=yaml_operation)
        except NotImplementedError:
            formatted_error = error
    else:
        raise error

    raise Exception(formatted_error)
