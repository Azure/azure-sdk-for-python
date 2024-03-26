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

    :param data_id: Arm id of registered data asset. If not set, data_id defaults to None.
    :type data_id: typing.Optional[str]
    :param name: Name of data asset. If not set, name defaults to None.
    :type name: typing.Optional[str]
    :param path: Path where the data asset is stored. If not set, path defaults to None.
    :type path: typing.Optional[str]
    :param version: Version of data asset. If not set, version defaults to None.
    :type version" typing.Optional[int]

    .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_endpoint_deployment_configs.py
                :start-after: [START data_asset_entity_create]
                :end-before: [END data_asset_entity_create]
                :language: python
                :dedent: 8
                :caption: Creating a DataAsset entity.

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
