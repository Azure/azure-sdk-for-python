# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._utils._arm_id_utils import is_ARM_id_for_resource
from azure.ai.ml._scope_dependent_operations import OperationScope

OPEN_AI_PROTOCOL_TEMPLATE = "azure_open_ai://deployment/{}/model/{}"


def build_open_ai_protocol(
    model: Optional[str] = None,
    deployment: Optional[str] = None,
):
    if not deployment or not model:
        return None
    return OPEN_AI_PROTOCOL_TEMPLATE.format(deployment, model)


def build_connection_id(id: Optional[str], scope: OperationScope):
    if not id or not scope.subscription_id or not scope.resource_group_name or not scope.workspace_name:
        return id

    if is_ARM_id_for_resource(id, "connections", True):
        return id

    # pylint: disable=line-too-long
    template = "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}/connections/{id}"
    return template.format(
        subscription_id=scope.subscription_id,
        resource_group_name=scope.resource_group_name,
        workspace_name=scope.workspace_name,
        id=id,
    )
