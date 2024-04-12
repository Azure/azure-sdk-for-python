# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2021_10_01_dataplanepreview.models import (
    ResourceManagementAssetReferenceData,
    ResourceManagementAssetReferenceDetails,
)
from azure.ai.ml._schema import WorkspaceAssetReferenceSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.entities._util import load_from_dict


class WorkspaceAssetReference(Asset):
    """Workspace Model Reference.

    This is for SDK internal use only, might be deprecated in the future.
    :param name: Model name
    :type name: str
    :param version: Model version
    :type version: str
    :param asset_id: Model asset id
    :type version: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        asset_id: Optional[str] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
    ):
        super().__init__(
            name=name,
            version=version,
            properties=properties,
            **kwargs,
        )
        self.asset_id = asset_id

    @classmethod
    def _load(
        cls: Any,
        data: Optional[dict] = None,
        yaml_path: Optional[Union[os.PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "WorkspaceAssetReference":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        res: WorkspaceAssetReference = load_from_dict(WorkspaceAssetReferenceSchema, data, context, **kwargs)
        return res

    def _to_rest_object(self) -> ResourceManagementAssetReferenceData:
        resource_management_details = ResourceManagementAssetReferenceDetails(
            destination_name=self.name,
            destination_version=self.version,
            source_asset_id=self.asset_id,
        )
        resource_management = ResourceManagementAssetReferenceData(properties=resource_management_details)
        return resource_management

    @classmethod
    def _from_rest_object(cls, resource_object: ResourceManagementAssetReferenceData) -> "WorkspaceAssetReference":
        resource_management = WorkspaceAssetReference(
            name=resource_object.properties.destination_name,
            version=resource_object.properties.destination_version,
            asset_id=resource_object.properties.source_asset_id,
        )

        return resource_management

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return dict(WorkspaceAssetReferenceSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self))
