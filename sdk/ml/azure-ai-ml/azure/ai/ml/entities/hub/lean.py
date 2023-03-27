# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access


from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import Workspace as RestWorkspace

from azure.ai.ml._schema._hub.lean import LeanSchema
from azure.ai.ml.entities import Workspace
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY

from ._constants import LEAN_KIND



@experimental
class _LeanWorkspace(Workspace):
    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        display_name: Optional[str] = None,
        location: Optional[str] = None,
        resource_group: Optional[str] = None,
        application_insights: Optional[str] = None,
        hub_resourceid: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        primary_user_assigned_identity: Optional[str] = None,
        **kwargs,
    ):

        """Hub.

        :param name: Name of the feature store.
        :type name: str
        :param description: Description of the feature store.
        :type description: str
        :param tags: Tags of the feature store.
        :type tags: dict
        :param display_name: Display name for the feature store. This is non-unique within the resource group.
        :type display_name: str
        :param location: The location to create the feature store in.
            If not specified, the same location as the resource group will be used.
        :type location: str
        :param resource_group: Name of resource group to create the feature store in.
        :type resource_group: str
        :param application_insights: The resource ID of an existing application insights
            to use instead of creating a new one.
        :type application_insights: str
        :param hub_resourceid: The resource id for hub workspace
        :type hub_resourceid: str
        :param identity: workspace's Managed Identity (user assigned, or system assigned)
        :type identity: IdentityConfiguration
        :param primary_user_assigned_identity: The workspace's primary user assigned identity
        :type primary_user_assigned_identity: str
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """

        self._workspace_id = kwargs.pop("workspace_id", "")
        super().__init__(
            name=name,
            description=description,
            tags=tags,
            kind=LEAN_KIND,
            display_name=display_name,
            location=location,
            resource_group=resource_group,
            application_insights = application_insights,
            identity=identity,
            primary_user_assigned_identity=primary_user_assigned_identity,
            hub_resourceid=hub_resourceid,
            **kwargs,
        )
        self.identity = identity

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspace) -> "_LeanWorkspace":
        if not rest_obj:
            return None

        workspace_object = Workspace._from_rest_object(rest_obj)

        return _LeanWorkspace(
            name=workspace_object.name,
            description=workspace_object.description,
            tags=workspace_object.tags,
            display_name=workspace_object.display_name,
            location=workspace_object.location,
            resource_group=workspace_object.resource_group,
            identity=workspace_object.identity,
            hub_resourceid=workspace_object.hub_resourceid,
            application_insights = workspace_object.application_insights,
            workspace_id=rest_obj.workspace_id,
        )

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "_LeanWorkspace":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        loaded_schema = load_from_dict(LeanSchema, data, context, **kwargs)
        return _LeanWorkspace(**loaded_schema)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return _LeanWorkspace(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
