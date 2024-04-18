# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional
from dataclasses import dataclass

from azure.ai.ml.entities import Data as DataAsset
from azure.ai.ml.constants import AssetTypes


@dataclass
class Data:
    """Data asset
    
    :param name: The name of the data asset.
    :type name: str
    :param path: The path to the data asset.
    :type path: str
    :param version: The version of the data asset.
    :type version: Optional[str]
    :param type: The type of the data asset. Defaults to ~azure.ai.ml.constants.AssetTypes.URI_FOLDER.
        Accepted values include: ~azure.ai.ml.constants.AssetTypes.URI_FILE,
        ~azure.ai.ml.constants.AssetTypes.URI_FOLDER, and ~azure.ai.ml.constants.AssetTypes.MLTABLE.
    :type type: str
    :param description: The description of the data asset.
    :type description: Optional[str]
    :param tags: The tags of the data asset.
    :type tags: Optional[Dict[str, str]]
    :param properties: The properties of the data asset.
    :type properties: Optional[Dict[str, str]]
    """
    name: str
    path: str
    version: Optional[str] = None
    type: str = AssetTypes.URI_FOLDER
    description: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    properties: Optional[Dict[str, str]] = None

    @classmethod
    def _from_data_asset(cls, data: DataAsset) -> "Data":
        return cls(
            name=data.name,
            version=data.version,
            type = data.type,
            path=data.path,
            description=data.description,
            tags=data.tags,
            properties=data.properties
        )
