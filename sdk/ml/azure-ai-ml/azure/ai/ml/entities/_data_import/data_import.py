# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._schema import DataImportSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, AssetTypes
from azure.ai.ml.data_transfer import Database, FileSystem
from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._util import load_from_dict


@experimental
class DataImport(Data):
    """Data asset with a creating data import job.

    :keyword name: Name of the asset.
    :paramtype name: str
    :keyword path: The path to the asset being created by data import job.
    :paramtype path: str
    :keyword source: The source of the asset data being copied from.
    :paramtype source: Union[Database, FileSystem]
    :keyword version: Version of the resource.
    :paramtype version: str
    :keyword description: Description of the resource.
    :paramtype description: str
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated.
    :paramtype tags: dict[str, str]
    :keyword properties: The asset property dictionary.
    :paramtype properties: dict[str, str]
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

    def _to_rest_object(self) -> Dict[str, Any]:
        # ``DataImport`` / ``DatabaseSource`` / ``FileSystemSource`` are not modeled on the shared
        # arm_ml_service client, so emit the wire body as a plain dict (JSON-direct). This is byte-identical
        # to the legacy ``RestDataImport(...).serialize()`` output, including the server-pinned
        # ``dataType='uri_folder'`` constant and the ``isAnonymous``/``isArchived`` defaults.
        source: Dict[str, Any]
        if isinstance(self.source, Database):
            source = {"sourceType": "database"}
            if self.source.connection is not None:
                source["connection"] = self.source.connection
            if self.source.query is not None:
                source["query"] = self.source.query
        else:
            source = {"sourceType": "file_system"}
            if self.source.connection is not None:
                source["connection"] = self.source.connection
            if self.source.path is not None:
                source["path"] = self.source.path

        rest_object: Dict[str, Any] = {
            "isAnonymous": False,
            "isArchived": False,
            "dataType": "uri_folder",
            "dataUri": self.path,
            "source": source,
        }
        if self.description is not None:
            rest_object["description"] = self.description
        if self.properties is not None:
            rest_object["properties"] = self.properties
        if self.tags is not None:
            rest_object["tags"] = self.tags
        if self.name is not None:
            rest_object["assetName"] = self.name
        return rest_object

    @classmethod
    def _from_rest_object(cls, data_rest_object: Dict[str, Any]) -> "DataImport":
        source: Any = None
        source_dict = data_rest_object["source"]
        if source_dict.get("sourceType") == "database":
            source = Database(
                connection=source_dict.get("connection"),
                query=source_dict.get("query"),
            )
            data_type = AssetTypes.MLTABLE
        else:
            source = FileSystem(
                connection=source_dict.get("connection"),
                path=source_dict.get("path"),
            )
            data_type = AssetTypes.URI_FOLDER

        data_import = cls(
            name=data_rest_object.get("assetName"),  # type: ignore[arg-type]
            path=data_rest_object.get("dataUri"),  # type: ignore[arg-type]
            source=source,
            description=data_rest_object.get("description"),
            tags=data_rest_object.get("tags"),
            properties=data_rest_object.get("properties"),
            type=data_type,
            is_anonymous=data_rest_object.get("isAnonymous"),
        )
        return data_import
