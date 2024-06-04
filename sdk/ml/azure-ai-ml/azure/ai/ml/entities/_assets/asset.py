# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid
from abc import abstractmethod
from os import PathLike
from typing import IO, Any, AnyStr, Dict, Optional, Union

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException


class Asset(Resource):
    """Base class for asset.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :param name: The name of the asset. Defaults to a random GUID.
    :type name: Optional[str]]
    :param version: The version of the asset. Defaults to "1" if no name is provided, otherwise defaults to
        autoincrement from the last registered version of the asset with that name. For a model name that has
        never been registered, a default version will be assigned.
    :type version: Optional[str]
    :param description: The description of the resource. Defaults to None.
    :type description: Optional[str]
    :param tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None.
    :type tags: Optional[dict[str, str]]
    :param properties: The asset property dictionary. Defaults to None.
    :type properties: Optional[dict[str, str]]
    :keyword kwargs: A dictionary of additional configuration parameters.
    :paramtype kwargs: Optional[dict]
    """

    def __init__(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        self._is_anonymous = kwargs.pop("is_anonymous", False)
        self._auto_increment_version = kwargs.pop("auto_increment_version", False)
        self.auto_delete_setting = kwargs.pop("auto_delete_setting", None)

        if not name and version is None:
            name = _get_random_name()
            version = "1"
            self._is_anonymous = True
        elif version is not None and not name:
            msg = "If version is specified, name must be specified also."
            err = ValidationException(
                message=msg,
                target=ErrorTarget.ASSET,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                error_type=ValidationErrorType.MISSING_FIELD,
            )
            log_and_raise_error(err)

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

    @property
    def version(self) -> Optional[str]:
        """The asset version.

        :return: The asset version.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        """Sets the asset version.

        :param value: The asset version.
        :type value: str
        :raises ValidationException: Raised if value is not a string.
        """
        if value:
            if not isinstance(value, str):
                msg = f"Asset version must be a string, not type {type(value)}."
                err = ValidationException(
                    message=msg,
                    target=ErrorTarget.ASSET,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
                log_and_raise_error(err)

        self._version = value
        self._auto_increment_version = self.name and not self._version

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
        """Dump the asset content into a file in YAML format.

        :param dest: The local path or file stream to write the YAML content to.
            If dest is a file path, a new file will be created.
            If dest is an open file, the file will be written to directly.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        :raises FileExistsError: Raised if dest is a file path and the file already exists.
        :raises IOError: Raised if dest is an open file and the file is not writable.
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def __eq__(self, other: Any) -> bool:
        return bool(
            self.name == other.name
            and self.id == other.id
            and self.version == other.version
            and self.description == other.description
            and self.tags == other.tags
            and self.properties == other.properties
            and self.base_path == other.base_path
            and self._is_anonymous == other._is_anonymous
            and self._auto_increment_version == other._auto_increment_version
            and self.auto_delete_setting == other.auto_delete_setting
        )

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


def _get_random_name() -> str:
    return str(uuid.uuid4())
