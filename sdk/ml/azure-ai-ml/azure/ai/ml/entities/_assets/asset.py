# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid
from abc import abstractmethod
from os import PathLike
from typing import Dict, Optional, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.entities._resource import Resource


class Asset(Resource):
    """Base class for asset, can't be instantiated directly.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the asset.
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
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs,
    ):

        self._is_anonymous = kwargs.pop("is_anonymous", False)
        self._auto_increment_version = kwargs.pop("auto_increment_version", False)

        if not name and version is None:
            name = str(uuid.uuid4())
            version = "1"
            self._is_anonymous = True
        elif version is not None and not name:
            msg = "If version is specified, name must be specified also."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.ASSET,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )

        super().__init__(
            name=name,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )

        self.version = version
        self.latest_version = None

    @abstractmethod
    def _to_dict(self) -> Dict:
        """Dump the artifact content into a pure dict object."""
        pass

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        if value:
            if not isinstance(value, str):
                msg = f"Asset version must be a string, not type {type(value)}."
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.ASSET,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                )
        self._version = value
        self._auto_increment_version = self.name and not self._version

    def dump(self, path: Union[PathLike, str]) -> None:
        """Dump the artifact content into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(path, yaml_serialized, default_flow_style=False)

    def __eq__(self, other) -> bool:
        return (
            self.name == other.name
            and self.id == other.id
            and self.version == other.version
            and self.description == other.description
            and self.tags == other.tags
            and self.properties == other.properties
            and self.base_path == other.base_path
            and self._is_anonymous == other._is_anonymous
            and self._auto_increment_version == other._auto_increment_version
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
