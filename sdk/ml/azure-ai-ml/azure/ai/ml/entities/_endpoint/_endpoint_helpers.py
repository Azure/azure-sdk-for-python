# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
from typing import Any, Optional

from azure.ai.ml.constants._endpoint import EndpointConfigurations
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


def validate_endpoint_or_deployment_name(name: Optional[str], is_deployment: bool = False) -> None:
    """Validates the name of an endpoint or a deployment

    A valid name of an endpoint or deployment:

    1. Is between 3 and 32 characters long (inclusive of both ends of the range)
    2. Starts with a letter
    3. Is followed by 0 or more alphanumeric characters (`a-zA-Z0-9`) or hyphens (`-`)
    3. Ends with an alphanumeric character (`a-zA-Z0-9`)

    :param name: Either an endpoint or deployment name
    :type name: str
    :param is_deployment: Whether the name is a deployment name. Defaults to False
    :type is_deployment: bool
    """
    if name is None:
        return

    type_str = "a deployment" if is_deployment else "an endpoint"
    target = ErrorTarget.DEPLOYMENT if is_deployment else ErrorTarget.ENDPOINT
    if len(name) < EndpointConfigurations.MIN_NAME_LENGTH or len(name) > EndpointConfigurations.MAX_NAME_LENGTH:
        msg = f"The name for {type_str} must be at least 3 and at most 32 characters long (inclusive of both limits)."
        raise ValidationException(
            message=msg,
            target=target,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.INVALID_VALUE,
        )
    if not re.match(EndpointConfigurations.NAME_REGEX_PATTERN, name):
        msg = f"""The name for {type_str} must start with an upper- or lowercase letter
 and only consist of '-'s and alphanumeric characters."""
        raise ValidationException(
            message=msg,
            target=target,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.INVALID_VALUE,
        )


def validate_identity_type_defined(identity: Any) -> None:
    if identity and not identity.type:
        msg = "Identity type not found in provided yaml file."
        raise ValidationException(
            message=msg,
            target=ErrorTarget.ENDPOINT,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.MISSING_FIELD,
        )
