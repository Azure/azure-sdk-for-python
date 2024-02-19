# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=no-member

from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_06_01_preview.models import DatabaseSource as RestDatabaseSource
from azure.ai.ml._restclient.v2023_06_01_preview.models import DataImport as RestDataImport
from azure.ai.ml._restclient.v2023_06_01_preview.models import FileSystemSource as RestFileSystemSource
from azure.ai.ml._schema import DataImportSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, AssetTypes
from azure.ai.ml.data_transfer import Database, FileSystem
from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._util import load_from_dict


@experimental
class DataImport(Data):
    """Data asset with a creating data import job.

    :param name: Name of the asset.
    :type name: str
    :param path: The path to the asset being created by data import job.
    :type path: str
    :param source: The source of the asset data being copied from.
    :type source: Union[Database, FileSystem]
    :param version: Version of the resource.
    :type version: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str,
        path: str,
        source: Union[Database, FileSystem],
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
    ):
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            path=path,
            **kwargs,
        )
        self.source = source

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "DataImport":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        res: DataImport = load_from_dict(DataImportSchema, data, context, **kwargs)
        return res

    def _to_rest_object(self) -> RestDataImport:
        if isinstance(self.source, Database):
            source = RestDatabaseSource(
                connection=self.source.connection,
                query=self.source.query,
            )
        else:
            source = RestFileSystemSource(
                connection=self.source.connection,
                path=self.source.path,
            )

        return RestDataImport(
            description=self.description,
            properties=self.properties,
            tags=self.tags,
            data_type=self.type,
            data_uri=self.path,
            asset_name=self.name,
            source=source,
        )

    @classmethod
    def _from_rest_object(cls, data_rest_object: RestDataImport) -> "DataImport":
        source: Any = None
        if isinstance(data_rest_object.source, RestDatabaseSource):
            source = Database(
                connection=data_rest_object.source.connection,
                query=data_rest_object.source.query,
            )
            data_type = AssetTypes.MLTABLE
        else:
            source = FileSystem(
                connection=data_rest_object.source.connection,
                path=data_rest_object.source.path,
            )
            data_type = AssetTypes.URI_FOLDER

        data_import = cls(
            name=data_rest_object.asset_name,
            path=data_rest_object.data_uri,
            source=source,
            description=data_rest_object.description,
            tags=data_rest_object.tags,
            properties=data_rest_object.properties,
            type=data_type,
            is_anonymous=data_rest_object.is_anonymous,
        )
        return data_import
