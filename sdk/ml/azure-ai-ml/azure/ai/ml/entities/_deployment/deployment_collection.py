# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import Collection as RestCollection
from azure.ai.ml._schema._deployment.online.deployment_collection_schema import DeploymentCollectionSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from .data_asset import DataAsset


@experimental
class DeploymentCollection:
    """Collection entity

    :param enabled: Is logging for this collection enabled. Possible values include: 'true', 'false'.
    :type enabled: str
    :param data: Data asset id associated with collection logging.
    :type data: str
    :param client_id: Client ID associated with collection logging.
    :type client_id: str

    """

    def __init__(
        self,
        *,
        enabled: Optional[str] = None,
        data: Optional[Union[str, DataAsset]] = None,
        client_id: Optional[str] = None,
        **kwargs: Any
    ):
        self.enabled = enabled  # maps to data_collection_mode
        self.data = data  # maps to data_id
        self.sampling_rate = kwargs.get(
            "sampling_rate", None
        )  # maps to sampling_rate, but it has to be passed from the data_collector root
        self.client_id = client_id

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = DeploymentCollectionSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    @classmethod
    def _from_rest_object(cls, rest_obj: RestCollection) -> "DeploymentCollection":
        return DeploymentCollection(
            enabled="true" if rest_obj.data_collection_mode == "Enabled" else "false",
            sampling_rate=rest_obj.sampling_rate,
            data=rest_obj.data_id,
            client_id=rest_obj.client_id,
        )

    def _to_rest_object(self) -> RestCollection:
        return RestCollection(
            data_collection_mode="enabled" if str(self.enabled).lower() == "true" else "disabled",
            sampling_rate=self.sampling_rate,
            data_id=self.data,
            client_id=self.client_id,
        )
