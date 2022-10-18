# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import traceback
from typing import Dict, Tuple, Union

from colorama import Fore, init
from marshmallow.exceptions import ValidationError as SchemaValidationError

from azure.ai.ml.constants._common import (
    DATASTORE_SCHEMA_TYPES,
    SCHEMA_VALIDATION_ERROR_TEMPLATE,
    YAML_CREATION_ERROR_DESCRIPTION,
)
from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)


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
        prescribed by the {entity_type} schema."
        count += 1
    if error_types[ValidationErrorType.UNKNOWN_FIELD]:
        errors += f"\n{count}) A least one unrecognized parameter is specified"
        resolutions += f"Remove any parameters not prescribed by the {entity_type} schema."
        count += 1
    if error_types[ValidationErrorType.MISSING_FIELD]:
        errors += f"\n{count}) At least one required parameter is missing"
        resolutions += f"Ensure all parameters required by the {entity_type} schema are specified."
        count += 1
    if error_types[ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND]:
        errors += f"\n{count}) One or more files or folders do not exist.\n"
        resolutions += "Double-check the directory paths you provided and enter the correct paths."
        count += 1
    if error_types[ValidationErrorType.CANNOT_SERIALIZE]:
        errors += f"\n{count}) One or more fields cannot be serialized.\n"
        resolutions += f"Double-check that all specified parameters are of the correct types and formats \
        prescribed by the {entity_type} schema."
        count += 1
    if error_types[ValidationErrorType.CANNOT_PARSE]:
        errors += f"\n{count}) YAML file cannot be parsed.\n"
        resolutions += "Double-check your YAML file for syntax and formatting errors."
        count += 1
    if error_types[ValidationErrorType.RESOURCE_NOT_FOUND]:
        errors += f"\n{count}) Resource was not found.\n"
        resolutions += "Double-check that the resource has been specified correctly and that you have access to it."
        count += 1

    return errors, resolutions


def format_create_validation_error(
    error: Union[SchemaValidationError, ValidationException], yaml_operation: bool
) -> str:
    """
    Formats a detailed error message for validation errors.
    """
    from azure.ai.ml.entities._util import REF_DOC_ERROR_MESSAGE_MAP
    from azure.ai.ml._schema.assets.data import DataSchema
    from azure.ai.ml._schema._datastore import (
        AzureBlobSchema,
        AzureDataLakeGen1Schema,
        AzureDataLakeGen2Schema,
        AzureFileSchema,
    )
    from azure.ai.ml._schema.job import CommandJobSchema
    from azure.ai.ml._schema._sweep import SweepJobSchema
    from azure.ai.ml._schema.assets.environment import EnvironmentSchema
    from azure.ai.ml._schema.assets.model import ModelSchema

    entity_type, details = get_entity_type(error)
    error_types, details = format_details_section(error, details, entity_type)
    errors, resolutions = format_errors_and_resolutions_sections(entity_type, error_types)

    if yaml_operation:
        description = YAML_CREATION_ERROR_DESCRIPTION.format(entity_type=entity_type)

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
