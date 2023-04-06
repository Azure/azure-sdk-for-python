# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import traceback
from typing import Any, Dict, Optional, Tuple, Union

from colorama import Fore, Style, init
from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml.constants._common import (
    DATASTORE_SCHEMA_TYPES,
    SCHEMA_VALIDATION_ERROR_TEMPLATE,
    YAML_CREATION_ERROR_DESCRIPTION,
)
from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)


def _find_deepest_dictionary(data: Dict[Any, Any]) -> Dict[Any, Any]:
    """Find deepest dictionary in nested dictionary.

    Can't be placed in _utils/ due to circular import.

    :param data: Nested dictionary
    :type data: Dict[Any, Any]
    :return: The innermost dictionary
    :rtype: Dict[Any, Any]
    """
    if not any([isinstance(data.get(key), dict) for key in data]):
        return data
    for key in data:
        if isinstance(data.get(key), dict):
            return _find_deepest_dictionary(data.get(key))


def get_entity_type(error: Union[SchemaValidationError, ValidationException]) -> Tuple[str, str]:
    """Get entity name and details based on the schema type referenced in an error.

    :param error: Client-side validation error
    :type error: Union[SchemaValidationError, ValidationException]
    :raises NotImplementedError: If entity-linking logic has not been implemented for the error schema type
    :return: Entity name and details component of error message
    :rtype: Tuple[str, str]
    """
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
    """Build string for the error message template's Details section.

    :param error: Client-side validation error
    :type error: Union[SchemaValidationError, ValidationException]
    :param details: Error message details
    :type details: str
    :param entity_type: The entity name corresponding the schema type in the error message
    :type entity_type: str
    :return: A dictionary of each ValidationErrorType with boolean keys indicating if they were
    found in the error message and the formatted Details section string
    :rtype: Tuple[Dict[str, bool], str]
    """
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
        details += f"\n\n{Fore.RED}(x) {error.message}{Fore.RESET}\n"
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

            details += f"{Fore.RED}\n(x) {field}:\n- {field_error}{Fore.RESET}\n"
    return error_types, details


def format_errors_and_resolutions_sections(
    entity_type: str, error_types: Dict[str, bool], cli: bool
) -> Tuple[str, str]:
    """Build strings for the error message template's Errors and Resolutions sections.

    :param entity_type: The entity name corresponding the schema type in the error message
    :type entity_type: str
    :param error_types: A dictionary of each ValidationErrorType with boolean keys indicating if they were
    found in the error message
    :type error_types: Dict[str, bool]
    :param cli: Whether or not the error was triggered by the CLI or SDK
    :type cli: bool
    :return: Formatted strings for Errors and Resolutions sections
    :rtype: Tuple[str, str]
    """
    resolutions = ""
    errors = ""
    count = 1

    if error_types[ValidationErrorType.INVALID_VALUE]:
        errors += f"\n{count}) One or more fields are invalid"
        resolutions += (
            f"\n{count}) Double-check that all specified parameters are of the correct types and formats "
            f"prescribed by the {entity_type} schema."
        )
        count += 1
    if error_types[ValidationErrorType.UNKNOWN_FIELD]:
        errors += f"\n{count}) A least one unrecognized parameter is specified"
        resolutions += f"\n{count}) Remove any parameters not prescribed by the {entity_type} schema."
        count += 1
    if error_types[ValidationErrorType.MISSING_FIELD]:
        errors += f"\n{count}) At least one required parameter is missing"
        resolutions += f"\n{count}) Ensure all parameters required by the {entity_type} schema are specified."
        count += 1
    if error_types[ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND]:
        errors += f"\n{count}) One or more files or folders do not exist.\n"
        resolutions += f"\n{count}) Double-check the directory path you provided and enter the correct path."
        count += 1
    if error_types[ValidationErrorType.CANNOT_SERIALIZE]:
        errors += f"\n{count}) One or more fields cannot be serialized.\n"
        resolutions += f"\n{count}) Double-check that all specified parameters are of the correct types and formats \
        prescribed by the {entity_type} schema."
        count += 1
    if error_types[ValidationErrorType.CANNOT_PARSE]:
        errors += f"\n{count}) YAML file cannot be parsed.\n"
        resolutions += f"\n{count}) Double-check your YAML file for syntax and formatting errors."
        count += 1
    if error_types[ValidationErrorType.RESOURCE_NOT_FOUND]:
        errors += f"\n{count}) Resource was not found.\n"
        resolutions += (
            f"\n{count}) Double-check that the resource has been specified correctly and " "that you have access to it."
        )
        count += 1

    if cli:
        errors = "Error: " + errors
    else:
        errors = Fore.BLACK + errors + Fore.RESET

    return errors, resolutions


def format_create_validation_error(
    error: Union[SchemaValidationError, ValidationException],
    yaml_operation: bool,
    cli: Optional[bool] = False,
    raw_error: Optional[str] = None,
) -> str:
    """Build a UI-friendly error message string for validation errors.

    :param error: Raised error
    :type error: Union[SchemaValidationError, ValidationException]
    :param yaml_operation: Whether or not the error arose from a YAML file issue. If so, a section asking the user to check their YAML file will be added.
    :type yaml_operation: bool
    :param cli: Whether or not the error was triggered by the CLI or SDK, defaults to False
    :type cli: Optional[bool]
    :param raw_error: Raw error message, defaults to None
    :type raw_error: Optional[str]
    :return: Formatted error message
    :rtype: str
    """
    from azure.ai.ml._schema._datastore import (
        AzureBlobSchema,
        AzureDataLakeGen1Schema,
        AzureDataLakeGen2Schema,
        AzureFileSchema,
    )
    from azure.ai.ml._schema._sweep import SweepJobSchema
    from azure.ai.ml._schema.assets.data import DataSchema
    from azure.ai.ml._schema.assets.environment import EnvironmentSchema
    from azure.ai.ml._schema.assets.model import ModelSchema
    from azure.ai.ml._schema.job import CommandJobSchema
    from azure.ai.ml.entities._util import REF_DOC_ERROR_MESSAGE_MAP

    if raw_error:
        error = raw_error
    entity_type, details = get_entity_type(error)
    error_types, details = format_details_section(error, details, entity_type)
    errors, resolutions = format_errors_and_resolutions_sections(entity_type, error_types, cli)

    if yaml_operation:
        description = YAML_CREATION_ERROR_DESCRIPTION.format(entity_type=entity_type)
        description = Style.BRIGHT + description + Style.RESET_ALL

        if entity_type == ErrorTarget.MODEL:
            schema_type = ModelSchema
        elif entity_type == ErrorTarget.DATA:
            schema_type = DataSchema
        elif entity_type == ErrorTarget.COMMAND_JOB:
            schema_type = CommandJobSchema
        elif entity_type == ErrorTarget.SWEEP_JOB:
            schema_type = SweepJobSchema
        elif entity_type in [ErrorTarget.BLOB_DATASTORE, ErrorTarget.DATASTORE]:
            schema_type = AzureBlobSchema
        elif entity_type == ErrorTarget.GEN1_DATASTORE:
            schema_type = AzureDataLakeGen1Schema
        elif entity_type == ErrorTarget.GEN2_DATASTORE:
            schema_type = AzureDataLakeGen2Schema
        elif entity_type == ErrorTarget.FILE_DATASTORE:
            schema_type = AzureFileSchema
        elif entity_type == ErrorTarget.ENVIRONMENT:
            schema_type = EnvironmentSchema
        else:
            schema_type = ""

        resolutions += " " + REF_DOC_ERROR_MESSAGE_MAP.get(schema_type, "")
    else:
        description = ""

    resolutions += "\n"
    formatted_error = SCHEMA_VALIDATION_ERROR_TEMPLATE.format(
        description=description,
        error_msg=errors,
        parsed_error_details=details,
        resolutions=resolutions,
        text_color=Fore.WHITE,
        link_color=Fore.CYAN,
        reset=Fore.RESET,
    )

    return formatted_error


def log_and_raise_error(
    error: Exception, debug: Optional[bool] = False, yaml_operation: Optional[bool] = False
) -> None:
    """Log, filter, format, and raise triggered errors.

    :param error: Raised error
    :type error: Exception
    :param debug: Whether or not the --debug flag should be included to provide verbose log output, defaults to False
    :type debug: Optional[bool]
    :param yaml_operation: Whether or not the error arose from a YAML file issue, defaults to False
    :type yaml_operation: Optional[bool]
    :raises error: Unformatted error message
    :raises Exception: Formatted error message, for client-side validation errors only
    """
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
            error_type = error.error_type
            if error_type == ValidationErrorType.GENERIC:
                formatted_error = error
            else:
                formatted_error = format_create_validation_error(error, yaml_operation=yaml_operation)
        except NotImplementedError:
            formatted_error = error
    else:
        raise error

    raise Exception(formatted_error)
