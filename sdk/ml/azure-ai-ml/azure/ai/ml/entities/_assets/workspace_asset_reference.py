# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._schema import WorkspaceAssetReferenceSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.entities._util import load_from_dict


class WorkspaceAssetReference(Asset):
    """Workspace Model Reference.

    This is for SDK internal use only, might be deprecated in the future.
    :keyword name: Model name
    :paramtype name: str
    :keyword version: Model version
    :paramtype version: str
    :keyword asset_id: Model asset id
    :paramtype asset_id: str
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

    def _to_rest_object(self) -> dict:
        # JSON-direct wire dict, byte-identical to the legacy v2021_10 ``ResourceManagementAssetReferenceData``
        # (referenceType is a server-pinned constant; None fields are omitted, matching msrest serialization).
        properties: Dict[str, Any] = {"referenceType": "Id"}
        if self.name is not None:
            properties["destinationName"] = self.name
        if self.version is not None:
            properties["destinationVersion"] = self.version
        properties["sourceAssetId"] = self.asset_id
        return {"properties": properties}

    @classmethod
    def _from_rest_object(cls, resource_object: dict) -> "WorkspaceAssetReference":
        properties = resource_object["properties"]
        resource_management = WorkspaceAssetReference(
            name=properties.get("destinationName"),
            version=properties.get("destinationVersion"),
            asset_id=properties.get("sourceAssetId"),
        )

        return resource_management

    def _to_dict(self) -> Dict:
        return dict(WorkspaceAssetReferenceSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self))
