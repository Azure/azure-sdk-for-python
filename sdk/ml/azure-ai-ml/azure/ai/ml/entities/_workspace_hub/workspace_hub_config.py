# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access

from typing import Dict, List, Optional

from azure.ai.ml._restclient.v2023_06_01_preview.models import WorkspaceHubConfig as RestWorkspaceHubConfig
from azure.ai.ml._schema._workspace_hub.workspace_hub import WorkspaceHubConfigSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY

from azure.ai.ml._utils._experimental import experimental


@experimental
class WorkspaceHubConfig:
    def __init__(
        self,
        additional_workspace_storage_accounts: Optional[List[str]] = None,
        default_workspace_resource_group: Optional[str] = None,
    ) -> None:
         
        """WorkspaceHubConfig.

        :param additional_workspace_storage_accounts: A list of resource IDs of existing storage accounts that will be utilized in addition to the default one.
        :type additional_workspace_storage_accounts: List[str]
        :param default_workspace_resource_group: A destination resource group for any Project workspaces that join the workspaceHub, it will be the workspaceHub's resource group by default.
        :type default_workspace_resource_group: str
        """
        self.additional_workspace_storage_accounts = additional_workspace_storage_accounts
        self.default_workspace_resource_group = default_workspace_resource_group

    def _to_rest_object(self) -> RestWorkspaceHubConfig:
        return RestWorkspaceHubConfig(
            additional_workspace_storage_accounts=self.additional_workspace_storage_accounts,
            default_workspace_resource_group=self.default_workspace_resource_group,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestWorkspaceHubConfig) -> "WorkspaceHubConfig":
        return WorkspaceHubConfig(
            additional_workspace_storage_accounts=obj.additional_workspace_storage_accounts,
            default_workspace_resource_group=obj.default_workspace_resource_group,
        )

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return WorkspaceHubConfigSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
