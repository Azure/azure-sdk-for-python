# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml._schema._deployment.online.deployment_collection_schema import DeploymentCollectionSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml._restclient.v2023_04_01_preview.models import Collection as RestCollection
from azure.ai.ml._utils._experimental import experimental


@experimental
class DeploymentCollection:
    """Collection entity

    :param enabled: Is logging for this collection enabled. If not set, enabled defaults to false.
    :type enabled: typing.Optional[str]
    :param data: Data asset id associated with collection logging. If not set, data defaults to None.
    :type data: typing.Optional[str]
    :param client_id: Client ID associated with collection logging. If not set, client_id defaults to None.
    :type client_id: typing.Optional[str]
    :param sampling_rate: Sampling rate for this collection. If not set, sampling_rate defaults to 1.
    :type sampling_rate: typing.Optional[float]

    .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_endpoint_deployment_configs.py
                :start-after: [START data_collector_entity_create]
                :end-before: [END data_collector_entity_create]
                :language: python
                :dedent: 8
                :caption: Creating a DataCollector entity.

    """

    def __init__(self, *, enabled: str = None, data: str = None, client_id: str = None, **kwargs):
        self.enabled = enabled  # maps to data_collection_mode
        self.data = data  # maps to data_id
        self.sampling_rate = kwargs.get(
            "sampling_rate", None
        )  # maps to sampling_rate, but it has to be passed from the data_collector root
        self.client_id = client_id

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DeploymentCollectionSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

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
            data_collection_mode="enabled" if self.enabled == "true" else "disabled",
            sampling_rate=self.sampling_rate,
            data_id=self.data,
            client_id=self.client_id,
        )
