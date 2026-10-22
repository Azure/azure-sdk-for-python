# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


# ---------------------------------------------------------------------------------------------
# This package has been vendored from azure-identity package from the following commit
# https://github.com/Azure/azure-sdk-for-python/commit/0f302dc6c299df2ee637457c8f165c7bdb4ec2af
# ---------------------------------------------------------------------------------------------
from typing import Any

from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


# pylint: disable-next=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
def _scopes_to_resource(*scopes: Any) -> Any:
    """Convert an AADv2 scope to an AADv1 resource."""

    if len(scopes) != 1:
        msg = "This credential requires exactly one scope per token request."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.IDENTITY,
            error_category=ErrorCategory.USER_ERROR,
        )

    resource = scopes[0]
    if resource.endswith("/.default"):
        resource = resource[: -len("/.default")]

    return resource
