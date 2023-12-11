# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access

from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_06_01_preview.models import WorkspaceHubConfig as RestWorkspaceHubConfig
from azure.ai.ml._schema._workspace_hub.workspace_hub import WorkspaceHubConfigSchema
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY

from azure.ai.ml._utils._experimental import experimental


@experimental
class WorkspaceHubConfig:
    """WorkspaceHubConfig.

    :keyword additional_workspace_storage_accounts: A list of resource IDs of existing storage accounts that will be
        utilized in addition to the default one.
    :paramtype additional_workspace_storage_accounts: List[str]
    :keyword default_workspace_resource_group: A destination resource group for any Project workspaces that join the
        workspaceHub, it will be the workspaceHub's resource group by default.
    :paramtype default_workspace_resource_group: str
    """

    def __init__(
        self,
        *,
        additional_workspace_storage_accounts: Optional[List[str]] = None,
        default_workspace_resource_group: Optional[str] = None,
    ) -> None:
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

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "WorkspaceHubConfig":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        loaded_schema = load_from_dict(WorkspaceHubConfigSchema, data, context, **kwargs)
        return WorkspaceHubConfig(**loaded_schema)
