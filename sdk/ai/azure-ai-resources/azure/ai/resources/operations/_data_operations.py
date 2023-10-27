# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import path
from typing import Any, Dict, Iterable, Optional

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data as DataAsset
from azure.ai.ml.constants import AssetTypes as DataAssetTypes

from azure.ai.resources.constants import AssetTypes
from azure.ai.resources.entities.data import Data
from azure.ai.resources._telemetry import ActivityType, monitor_with_activity, OpsLogger
from azure.core.tracing.decorator import distributed_trace

ops_logger = OpsLogger(__name__)
logger, module_logger = ops_logger.package_logger, ops_logger.module_logger

DataTypesMapping: Dict[AssetTypes, DataAssetTypes] = {
    AssetTypes.FILE: DataAssetTypes.URI_FILE,
    AssetTypes.FOLDER: DataAssetTypes.URI_FOLDER,
    AssetTypes.TABLE: DataAssetTypes.MLTABLE,
}

class DataOperations():
    """DataOperations.

    You should not instantiate this class directly. Instead, you should
    create an AIClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(self, ml_client: MLClient, **kwargs: Any):
        self._ml_client = ml_client

    @distributed_trace
    @monitor_with_activity(logger, "Data.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: Optional[str] = None
    ) -> Iterable[Data]:
        # TODO migrate mlindex to generic asset
        return [Data._from_data_asset(data) for data in self._ml_client.data.list(name=name)]

    @distributed_trace
    @monitor_with_activity(logger, "Data.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: Optional[str] = None, label: Optional[str] = None) -> Data:
        data = self._ml_client.data.get(name, version, label)
        if "azureml.mlIndexAsset" in data.properties:
            raise Exception(f"No Data with name {name} and version {version} found.")

        return Data._from_data_asset(data)

    @distributed_trace
    @monitor_with_activity(logger, "Data.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, data: Data) -> Data:
        try:
            path = data.path
        except:
            try:
                path = data["path"]
            except Exception as e:
                raise e

        data_asset = DataAsset(
            name=data.name,
            version=data.version,
            type=DataTypesMapping[data.type],
            path=path,
            properties=data.properties,
            tags=data.tags,
            description=data.description
        )

        created = self._ml_client.data.create_or_update(data_asset)
        return Data._from_data_asset(created)

    @distributed_trace
    @monitor_with_activity(logger, "Data.restore", ActivityType.PUBLICAPI)
    def restore(
            self,
            name: str,
            version: Optional[str] = None,
            label: Optional[str] = None
        ) -> None:
         """Restore an archived data asset.

        :param name: Name of data asset.
        :type name: str
        :param version: Version of data asset.
        :type version: str
        :param label: Label of the data asset. (mutually exclusive with version)
        :type label: str
        :return: None

        """
         
         self._ml_client.data.restore(name, version, label)
    
    @distributed_trace
    @monitor_with_activity(logger, "Data.archive", ActivityType.PUBLICAPI)
    def archive(
            self,
            name: str,
            version: Optional[str] = None,
            label: Optional[str] = None
        ) -> None:
            """Archive a data asset.

            :param name: Name of data asset.
            :type name: str
            :param version: Version of data asset.
            :type version: str
            :param label: Label of the data asset. (mutually exclusive with version)
            :type label: str
            :return: None

            """

            self._ml_client.data.archive(name, version, label)
