# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml.constants import OnlineEndpointConfigurations


def validate_endpoint_or_deployment_name(name: str, is_deployment: bool = False) -> None:
    """Validates that the name of an endpoint or deployment is:
    1. Between 3 and 32 characters long (inclusive of both ends of the range)
    2. Follows the following regex pattern: ^[a-zA-Z]([-a-zA-Z0-9]*[a-zA-Z0-9])?$
    """
    type_str = "a deployment" if is_deployment else "an endpoint"
    target = ErrorTarget.DEPLOYMENT if is_deployment else ErrorTarget.ENDPOINT
    if (
        len(name) < OnlineEndpointConfigurations.MIN_NAME_LENGTH
        or len(name) > OnlineEndpointConfigurations.MAX_NAME_LENGTH
    ):
        msg = f"The name for {type_str} must be at least 3 and at most 32 characters long (inclusive of both limits)."
        raise ValidationException(
            message=msg,
            target=target,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
        )
    if not re.match(OnlineEndpointConfigurations.NAME_REGEX_PATTERN, name):
        msg = f"The name for {type_str} must start with an upper- or lowercase letter and only consist of '-'s and alphanumeric characters."
        raise ValidationException(
            message=msg,
            target=target,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
        )


def validate_identity_type_defined(identity: object) -> None:
    if identity and not identity.type:
        msg = "Identity type not found in provided yaml file."
        raise ValidationException(
            message=msg,
            target=ErrorTarget.ENDPOINT,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
        )
