# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import abstractmethod
from os import PathLike
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

from azure.ai.ml._utils.utils import is_mlflow_uri, is_url
from azure.ai.ml.entities._assets.asset import Asset


class ArtifactStorageInfo:
    def __init__(
        self,
        name: str,
        version: str,
        relative_path: str,
        datastore_arm_id: str,
        container_name: str,
        storage_account_url: Optional[str] = None,
        is_file: Optional[bool] = None,
        indicator_file: Optional[str] = None,
    ):
        self.name = name
        self.version = version
        self.relative_path = relative_path
        self.datastore_arm_id = datastore_arm_id
        self.container_name = container_name
        self.storage_account_url = storage_account_url
        self.is_file = is_file
        self.indicator_file = indicator_file

    @property
    def full_storage_path(self) -> Optional[str]:
        if self.storage_account_url is None:
            return f"{self.container_name}/{self.relative_path}"
        return urljoin(self.storage_account_url, f"{self.container_name}/{self.relative_path}")

    @property
    def subdir_path(self) -> Optional[str]:
        if self.is_file:
            path = PurePosixPath(self.relative_path).parent
            if self.storage_account_url is None:
                return f"{self.container_name}/{path}"
            return urljoin(self.storage_account_url, f"{self.container_name}/{path}")
        return self.full_storage_path


class Artifact(Asset):
    """Base class for artifact, can't be instantiated directly.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param path: The local or remote path to the asset.
    :type path: Union[str, os.PathLike]
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param datastore: The datastore to upload the local artifact to.
    :type datastore: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        path: Optional[Union[str, PathLike]] = None,
        datastore: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )
        self.path = path
        self.datastore = datastore

    @property
    def path(self) -> Optional[Union[str, PathLike]]:
        return self._path

    @path.setter
    def path(self, value: Optional[Union[str, PathLike]]) -> None:
        if not value or is_url(value) or Path(value).is_absolute() or is_mlflow_uri(value):
            self._path = value
        else:
            self._path = Path(self.base_path, value).resolve()

    @abstractmethod
    def _to_dict(self) -> Dict:
        pass

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) == type(other)  # pylint: disable = unidiomatic-typecheck
            and self.name == other.name
            and self.id == other.id
            and self.version == other.version
            and self.description == other.description
            and self.tags == other.tags
            and self.properties == other.properties
            and self.base_path == other.base_path
            and self._is_anonymous == other._is_anonymous
        )

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    @abstractmethod
    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        """Updates an an artifact with the remote path of a local upload.

        :param asset_artifact: The asset storage info of the artifact
        :type asset_artifact: ArtifactStorageInfo
        """
