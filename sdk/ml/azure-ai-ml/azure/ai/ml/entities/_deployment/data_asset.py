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

    :param name: Name of data asset
    :type name: str
    :param path: Path where the data asset is stored. 
    :type path: str

    """

    def __init__(
        self,
        name: Optional[str] = None,
        path: Optional[str] = None,
        version: Optional[int] = None,
        **kwargs,
    ):  # pylint: disable=unused-argument
        self.name = name
        self.path = path
        self.version = version

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DataAssetSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
