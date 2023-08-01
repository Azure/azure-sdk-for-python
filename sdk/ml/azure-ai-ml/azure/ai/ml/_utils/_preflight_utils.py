# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Optional

from azure.ai.ml._azure_environments import _get_base_url_from_metadata
from azure.ai.ml._vendor.azure_resources._resource_management_client import ResourceManagementClient
from azure.ai.ml._vendor.azure_resources.operations import DeploymentsOperations
from azure.ai.ml.constants._common import ArmConstants
from azure.core.credentials import TokenCredential

module_logger = logging.getLogger(__name__)


def get_deployments_operation(credentials: TokenCredential, subscription_id: str) -> Optional[DeploymentsOperations]:
    if subscription_id is None:
        return None
    client = ResourceManagementClient(
        credential=credentials,
        subscription_id=subscription_id,
        base_url=_get_base_url_from_metadata(),
        api_version=ArmConstants.AZURE_MGMT_RESOURCE_API_VERSION,
    )
    return client.deployments
