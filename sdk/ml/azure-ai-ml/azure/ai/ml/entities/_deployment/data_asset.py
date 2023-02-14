# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional

from azure.ai.ml._schema._deployment.online.data_asset_schema import DataAssetSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


@experimental
class DataAsset:
    """Data Asset entity

    :param data_id: Arm id of registered data asset
    :param data_id: str
    :param name: Name of data asset
    :type name: str
    :param path: Path where the data asset is stored.
    :type path: str
    :param version: Version of data asset.
    :type version" int

    """

    def __init__(
        self,
        data_id: Optional[str] = None,
        name: Optional[str] = None,
        path: Optional[str] = None,
        version: Optional[int] = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.data_id = data_id
        self.name = name
        self.path = path
        self.version = version

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DataAssetSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
