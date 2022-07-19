# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import re
from typing import Any, Optional, Tuple, Union
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.constants import (
    ARM_ID_PREFIX,
    DATA_ARM_TYPE,
    DATASET_ARM_TYPE,
    DATASTORE_RESOURCE_ID,
    DATASTORE_SHORT_URI,
    REGISTRY_URI_REGEX_FORMAT,
    ASSET_ID_URI_REGEX_FORMAT,
    NAMED_RESOURCE_ID_FORMAT,
    AZUREML_RESOURCE_PROVIDER,
    PROVIDER_RESOURCE_ID_WITH_VERSION,
    LEVEL_ONE_NAMED_RESOURCE_ID_FORMAT,
    REGISTRY_VERSION_PATTERN,
)
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget

module_logger = logging.getLogger(__name__)


class AMLVersionedArmId(object):
    """Parser for versioned arm id: e.g. /subscription/.../code/my-code/versions/1

    :param arm_id: the versioned arm id
    :type arm_id: str
    :raises ValidationException: the arm id is incorrectly formatted
    """

    REGEX_PATTERN = (
        "^/?subscriptions/([^/]+)/resourceGroups/(["
        "^/]+)/providers/Microsoft.MachineLearningServices/workspaces/([^/]+)/([^/]+)/([^/]+)/versions/(["
        "^/]+)"
    )

    def __init__(self, arm_id=None):
        self.is_registry_id = None
        if arm_id:
            match = re.match(AMLVersionedArmId.REGEX_PATTERN, arm_id)
            if match:
                self.subscription_id = match.group(1)
                self.resource_group_name = match.group(2)
                self.workspace_name = match.group(3)
                self.asset_type = match.group(4)
                self.asset_name = match.group(5)
                self.asset_version = match.group(6)
            else:
                match = re.match(REGISTRY_VERSION_PATTERN, arm_id)
                if match:
                    self.asset_name = match.group(3)
                    self.asset_version = match.group(4)
                    self.is_registry_id = True
                else:
                    msg = "Invalid AzureML ARM versioned Id {}"
                    raise ValidationException(
                        message=msg.format(arm_id),
                        no_personal_data_message=msg.format("[arm_id]"),
                        error_category=ErrorCategory.USER_ERROR,
                        target=ErrorTarget.ARM_RESOURCE,
                    )


def get_datastore_arm_id(datastore_name: str = None, operation_scope: OperationScope = None) -> Optional[str]:
    return (
        DATASTORE_RESOURCE_ID.format(
            operation_scope.subscription_id,
            operation_scope.resource_group_name,
            operation_scope.workspace_name,
            datastore_name,
        )
        if datastore_name
        else None
    )


class AMLNamedArmId:
    """Parser for named arm id (no version): e.g. /subscription/.../compute/cpu-cluster

    :param arm_id: the named arm id
    :type arm_id: str
    :raises ValidationException: the arm id is incorrectly formatted
    """

    REGEX_PATTERN = (
        "^/?subscriptions/([^/]+)/resourceGroups/(["
        "^/]+)/providers/Microsoft.MachineLearningServices/workspaces/([^/]+)/([^/]+)/([^/]+)"
    )

    REGEX_PATTERN_WITH_PARENT = (
        "^/?subscriptions/([^/]+)/resourceGroups/(["
        "^/]+)/providers/Microsoft.MachineLearningServices/workspaces/([^/]+)/([^/]+)/([^/]+)/([^/]+)/([^/]+)"
    )

    def __init__(self, arm_id=None):
        if arm_id:
            match = re.match(AMLNamedArmId.REGEX_PATTERN_WITH_PARENT, arm_id)
            if match:
                self.asset_name = match.group(7)
                self.asset_type = match.group(6)
                self.parent_asset_name = match.group(5)
                self.parent_azureml_type = match.group(4)
            if match is None:
                match = re.match(AMLNamedArmId.REGEX_PATTERN, arm_id)
                if match:
                    self.asset_type = match.group(4)
                    self.asset_name = match.group(5)
                    self.parent_asset_name = None
                    self.parent_azureml_type = None
                else:
                    msg = "Invalid AzureML ARM named Id {}"
                    raise ValidationException(
                        message=msg.format(arm_id),
                        no_personal_data_message=msg.format("[arm_id]"),
                        error_category=ErrorCategory.USER_ERROR,
                        target=ErrorTarget.ARM_RESOURCE,
                    )

            self.subscription_id = match.group(1)
            self.resource_group_name = match.group(2)
            self.workspace_name = match.group(3)


class AMLAssetId:
    REGEX_PATTERN = ASSET_ID_URI_REGEX_FORMAT

    def __init__(self, asset_id: str):
        match = re.match(AMLAssetId.REGEX_PATTERN, asset_id)
        if match is None:
            msg = "Invalid AzureML Asset Id {}"
            raise ValidationException(
                message=msg.format(asset_id),
                no_personal_data_message=msg.format("[asset_id]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.ASSET,
            )

        self.location = match.group(1)
        self.workspace_id = match.group(2)
        self.asset_type = match.group(3)
        self.asset_name = match.group(4)
        self.asset_version = match.group(5)


class AzureResourceId:
    """Parser for a non-AzureML ARM Id

    :param arm_id: the named arm id
    :type arm_id: str
    :raises ValidationException: the arm id is incorrectly formatted
    """

    REGEX_PATTERN = "^/?subscriptions/([^/]+)/resourceGroups/([" "^/]+)/providers/Microsoft.([^/]+)/([^/]+)/([^/]+)"

    def __init__(self, arm_id=None):
        if arm_id:
            match = re.match(AzureResourceId.REGEX_PATTERN, arm_id)
            if match:
                self.asset_name = match.group(5)
                self.asset_type = match.group(4)
            else:
                msg = "Invalid ARM Id {}"
                raise ValidationException(
                    message=msg.format(arm_id),
                    no_personal_data_message=msg.format("[arm_id]"),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.ARM_RESOURCE,
                )

            self.subscription_id = match.group(1)
            self.resource_group_name = match.group(2)


def _parse_endpoint_name_from_deployment_id(id: str) -> str:
    REGEX_PATTERN = (
        "^/?subscriptions/([^/]+)/resourceGroups/(["
        "^/]+)/providers/Microsoft.MachineLearningServices/workspaces/([^/]+)/([^/]+)/([^/]+)/deployments/([^/]+)"
    )
    match = re.match(REGEX_PATTERN, id)
    if match is None:
        msg = "Invalid Deployment Id {}"
        raise ValidationException(
            message=msg.format(id),
            no_personal_data_message=msg.format("[id]"),
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.DEPLOYMENT,
        )
    return match.group(5)


def parse_AzureML_id(name: str) -> Tuple[str, str, str]:
    if name.startswith(ARM_ID_PREFIX):
        name = name[len(ARM_ID_PREFIX) :]

    at_splits = name.rsplit("@", 1)
    if len(at_splits) > 1:
        return at_splits[0], None, name[1]
    else:
        colon_splits = name.rsplit(":", 1)
        return colon_splits[0], None if len(colon_splits) == 1 else colon_splits[1], None


def parse_prefixed_name_version(name: str) -> Tuple[str, Optional[str]]:
    if name.startswith(ARM_ID_PREFIX):
        return parse_name_version(name[len(ARM_ID_PREFIX) :])
    return parse_name_version(name)


def parse_name_version(name: str) -> Tuple[str, Optional[str]]:
    if name.find("/") != -1 and name[0] != "/":
        raise ValidationException(
            f"Could not parse {name}. If providing an ARM id, it should start with a '/'.",
            no_personal_data_message=f"Could not parse {name}.",
        )
    token_list = name.split(":")
    if len(token_list) == 1:
        return name, None
    else:
        name, *version = token_list  # type: ignore
        return name, ":".join(version)


def parse_name_label(name: str) -> Tuple[str, Optional[str]]:
    if name.find("/") != -1 and name[0] != "/":
        raise ValidationException(
            f"Could not parse {name}. If providing an ARM id, it should start with a '/'.",
            no_personal_data_message=f"Could not parse {name}.",
        )
    token_list = name.rpartition("@")
    if not token_list[1]:  # separator not found
        *_, name = token_list
        return name, None
    else:
        name, _, label = token_list
        return name, label


def is_ARM_id_for_resource(name: Any, resource_type: str = ".*", sub_workspace_resource: bool = True) -> bool:
    if sub_workspace_resource:
        resource_regex = NAMED_RESOURCE_ID_FORMAT.format(
            ".*", ".*", AZUREML_RESOURCE_PROVIDER, ".*", resource_type, ".*"
        )
    else:
        resource_regex = LEVEL_ONE_NAMED_RESOURCE_ID_FORMAT.format(
            ".*", ".*", AZUREML_RESOURCE_PROVIDER, resource_type, ".*"
        )
    if isinstance(name, str) and re.match(resource_regex, name, re.IGNORECASE):
        return True
    return False


def is_registry_id_for_resource(name: Any) -> bool:
    if isinstance(name, str) and re.match(REGISTRY_URI_REGEX_FORMAT, name, re.IGNORECASE):
        return True
    return False


def get_arm_id_with_version(
    operation_scope: OperationScope, provider_name: str, provider_value: str, provider_version: str
):
    return PROVIDER_RESOURCE_ID_WITH_VERSION.format(
        operation_scope.subscription_id,
        operation_scope.resource_group_name,
        operation_scope.workspace_name,
        provider_name,
        provider_value,
        provider_version,
    )


def generate_data_arm_id(operation_scope: OperationScope, name: str, version: int):
    return get_arm_id_with_version(operation_scope, DATA_ARM_TYPE, name, str(version))


def generate_dataset_arm_id(operation_scope: OperationScope, name: str, version: int):
    return get_arm_id_with_version(operation_scope, DATASET_ARM_TYPE, name, str(version))


def remove_aml_prefix(id: Optional[str]) -> Optional[str]:
    if not id:
        return None

    if id.startswith(ARM_ID_PREFIX):
        return id[len(ARM_ID_PREFIX) :]
    else:
        return id


def get_resource_name_from_arm_id(resource_id: str) -> str:
    # parse arm id to datastore name
    return AMLNamedArmId(resource_id).asset_name


def get_resource_name_from_arm_id_safe(resource_id: str) -> Optional[str]:
    """
    Get the resource name from an ARM id. return input string if it is not an ARM id.
    """
    try:
        return get_resource_name_from_arm_id(resource_id)
    except ValidationException:
        # already a name
        return resource_id
    except AttributeError:
        # None or empty string
        return resource_id
    except Exception:
        # unexpected error
        module_logger.warning("Failed to parse resource id: %s", resource_id)
        return resource_id


def get_arm_id_object_from_id(resource_id: str) -> Union[AMLVersionedArmId, AMLNamedArmId, AzureResourceId]:
    """Attempts to create and return one of: AMLVersionedId, AMLNamedId, AzureResoureId.
    In the case than an AzureML ARM Id is passed in, either AMLVersionedId or AMLNamedId will be created depending on resource type
    In the case that a non-AzureML ARM id is passed in, an AzureResourceId will be returned

    :param resource_id: the ARM Id to parse
    :type arm_id: str
    :return: The parser for the given ARM Id
    :rtype: Union[AMLVersionedArmId, AMLNamedArmId, AzureResourceId]
    :raises ValidationException: the arm id is incorrectly formatted
    """

    # Try each type of parser for the ARM id. If none succeed, raise a ValueError
    try:
        return AMLVersionedArmId(resource_id)
    except ValidationException:
        pass

    try:
        return AMLNamedArmId(resource_id)
    except ValidationException:
        pass

    try:
        return AzureResourceId(resource_id)
    except ValidationException:
        pass

    msg = "Invalid ARM Id {}"
    raise ValidationException(
        message=msg.format(resource_id),
        no_personal_data_message=msg.format("[resource_id]"),
        target=ErrorTarget.DEPLOYMENT,
    )


def remove_datastore_prefix(id: Optional[str]) -> Optional[str]:
    if not id:
        return None

    if id.startswith(DATASTORE_SHORT_URI):
        return id[len(DATASTORE_SHORT_URI) :]
    else:
        return id
