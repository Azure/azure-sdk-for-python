# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import path
from typing import Any, Iterable, Optional

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data as DataAsset

from azure.ai.generative.entities.data import Data


class DataOperations():
    """DataOperations.

    You should not instantiate this class directly. Instead, you should
    create an AIClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(self, ml_client: MLClient, **kwargs: Any):
        self._ml_client = ml_client

    def list(
        self,
        name: Optional[str] = None
    ) -> Iterable[Data]:
        # TODO migrate mlindex to generic asset
        return [Data._from_data_asset(data) for data in self._ml_client.data.list(name=name)]

    def get(self, name: str, version: Optional[str] = None, label: Optional[str] = None) -> Data:
        data = self._ml_client.data.get(name, version, label)

        return Data(
            name=data.name,
            version=data.version,
            type=data.type,
            path=data.path,
            description=data.description,
            tags=data.tags,
            properties=data.properties
        )

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
            type=data.type,
            path=path,
            properties=data.properties,
            tags=data.tags,
            description=data.description
        )

        created = self._ml_client.data.create_or_update(data_asset)
        return Data(name=created.name, version=created.version, description=created.description, tags=created.tags, path=created.path, properties=created.properties)
