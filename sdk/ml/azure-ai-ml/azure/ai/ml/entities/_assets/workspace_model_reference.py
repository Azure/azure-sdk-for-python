# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from pathlib import Path
from typing import Dict, Union

from azure.ai.ml._restclient.v2021_10_01_dataplanepreview.models import (
    ResourceManagementAssetReferenceData,
    ResourceManagementAssetReferenceDetails,
)
from azure.ai.ml._schema import WorkspaceModelReferenceSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.entities._util import load_from_dict


class WorkspaceModelReference(Asset):
    """Workspace Model Reference.

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
        name: str = None,
        version: str = None,
        asset_id: str = None,
        properties: Dict = None,
        **kwargs,
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
        cls,
        data: dict = None,
        yaml_path: Union[os.PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "WorkspaceModelReference":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return load_from_dict(WorkspaceModelReferenceSchema, data, context, **kwargs)

    def _to_rest_object(self) -> ResourceManagementAssetReferenceData:
        resource_management_details = ResourceManagementAssetReferenceDetails(
            destination_name=self.name,
            destination_version=self.version,
            source_asset_id=self.asset_id,
        )
        resource_management = ResourceManagementAssetReferenceData(properties=resource_management_details)
        return resource_management

    @classmethod
    def _from_rest_object(cls, resource_object: ResourceManagementAssetReferenceData) -> "WorkspaceModelReference":

        resource_management = WorkspaceModelReference(
            name=resource_object.properties.destination_name,
            version=resource_object.properties.destination_version,
            asset_id=resource_object.properties.source_asset_id,
        )

        return resource_management

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return WorkspaceModelReferenceSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
