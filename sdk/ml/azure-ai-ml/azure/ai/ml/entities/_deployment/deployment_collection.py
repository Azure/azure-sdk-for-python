# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.online.deployment_collection_schema import DeploymentCollectionSchema
from azure.ai.ml.entities._deployment.data_asset import DataAsset
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY


class DeploymentCollection:
    """Collection entity

    :param enabled: Is logging for this collection enabled.
    :type enabled: str, optional
    :param data: Data asset associated with collection logging.
    :type data: DataAsset, optional

    """

    # pylint: disable=unused-argument,no-self-use
    def __init__(self, enabled: str = None, data: DataAsset = None, **kwargs):
        self.enabled = enabled
        self.data = data

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DeploymentCollectionSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
