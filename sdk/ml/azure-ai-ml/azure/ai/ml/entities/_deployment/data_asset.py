# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional

from azure.ai.ml._schema._deployment.online.data_asset_schema import DataAssetSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


@experimental
class DataAsset:
    """Data Asset entity

    :keyword Optional[str] data_id: Arm id of registered data asset
    :keyword Optional[str] name: Name of data asset
    :keyword Optional[str] path: Path where the data asset is stored.
    :keyword Optional[int] version: Version of data asset.
    """

    def __init__(
        self,
        *,
        data_id: Optional[str] = None,
        name: Optional[str] = None,
        path: Optional[str] = None,
        version: Optional[int] = None,
    ):
        self.data_id = data_id
        self.name = name
        self.path = path
        self.version = version

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = DataAssetSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
