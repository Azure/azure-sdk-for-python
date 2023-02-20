# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-member

from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Union
from azure.ai.ml._schema._data_import.data_import import DataImportSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, AssetTypes
from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._inputs_outputs.external_data import Database, FileSystem
from azure.ai.ml.entities._util import load_from_dict


class DataImport(Data):
    """Data import job to create the data asset.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param path: The path to the asset being created by data import job.
    :type path: str
    :param type: The type of the asset. Valid values are uri_file, uri_folder, mltable. Defaults to uri_folder.
    :type type: Literal[AssetTypes.URI_FILE, AssetTypes.URI_FOLDER, AssetTypes.MLTABLE]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        path: Optional[str] = None,  # if type is mltable, the path has to be a folder.
        type: str = AssetTypes.URI_FOLDER,  # pylint: disable=redefined-builtin
        source: Optional[Union[Dict, Database, FileSystem]] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            path=path,
            type=type,
            **kwargs,
        )
        self.source = source

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "DataImport":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        data_import = DataImport._load_from_dict(yaml_data=data, context=context, **kwargs)

        return data_import

    @classmethod
    def _load_from_dict(cls, yaml_data: Dict, context: Dict, **kwargs) -> "DataImport":
        return DataImport(**load_from_dict(DataImportSchema, yaml_data, context, **kwargs))
