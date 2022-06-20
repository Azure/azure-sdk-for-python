# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from azure.ai.ml._schema._data.mltable_metadata_schema import MLTableMetadataSchema
from azure.ai.ml._restclient.v2021_10_01.models import UriReference

from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._util import load_from_dict
from marshmallow import INCLUDE


class MLTableMetadata:
    """MLTableMetadata for data assets.

    :param paths: List of uris which the MLTableMetadata refers to.
    :type paths: List[UriReference]
    :param transformations: Any transformations to be applied to the data referenced in paths.
    :type transformations: List[Any]
    :param base_path: Base path to resolve relative paths from.
    :type base_path: str
    """

    def __init__(
        self, *, paths: List[UriReference], transformations: Optional[List[Any]] = None, base_path: str, **kwargs
    ):
        self.base_path = base_path
        self.paths = paths
        self.transformations = transformations

    @classmethod
    def load(
        cls,
        yaml_path: Union[PathLike, str],
        **kwargs,
    ) -> "MLTableMetadata":
        """Construct an MLTable object from yaml file.

        :param yaml_path: Path to a local file as the source.
        :type PathLike | str

        :return: Constructed MLTable object.
        :rtype: MLTable
        """
        yaml_dict = load_yaml(yaml_path)
        return cls._load(yaml_data=yaml_dict, yaml_path=yaml_path, **kwargs)

    @classmethod
    def _load(
        cls,
        yaml_data: Optional[Dict],
        yaml_path: Optional[Union[PathLike, str]],
        **kwargs,
    ) -> "MLTableMetadata":
        yaml_data = yaml_data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
        }
        return load_from_dict(MLTableMetadataSchema, yaml_data, context, "", unknown=INCLUDE, **kwargs)

    def _to_dict(self) -> Dict:
        return MLTableMetadataSchema(context={BASE_PATH_CONTEXT_KEY: "./"}, unknown=INCLUDE).dump(self)

    def referenced_uris(self) -> List[str]:
        return [path.file or path.folder for path in self.paths if path.file or path.folder]
