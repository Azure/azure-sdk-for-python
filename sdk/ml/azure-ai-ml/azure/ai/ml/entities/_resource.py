# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import os
from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, Optional, Union

from msrest import Serializer

from azure.ai.ml._restclient.v2021_10_01 import models

from ._system_data import SystemData


class Resource(ABC):
    """Base class for entity classes, can't be instantiated directly.

    :param ABC: Helper class that provides a standard way to create an ABC using inheritance.
    :type ABC: class
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs,
    ):
        """Class Resource constructor.

        :param name: Name of the resource.
        :type name: str
        :param description: Description of the resource., defaults to None
        :type description: str, optional
        :param tags: Tag dictionary. Tags can be added, removed, and updated., defaults to None
        :type tags: Dict, optional
        :param properties: The asset property dictionary., defaults to None
        :type properties: Dict, optional
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """
        self.name = name
        self.description = description
        self.tags = dict(tags) if tags else {}
        self.properties = dict(properties) if properties else {}

        # Hide read only properties in kwargs
        self._id = kwargs.pop("id", None)
        self.__source_path: Optional[str] = kwargs.pop("source_path", None)
        self._base_path = kwargs.pop("base_path", os.getcwd())
        self._creation_context = kwargs.pop("creation_context", None)
        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._serialize.client_side_validation = False
        super().__init__(**kwargs)

    @property
    def _source_path(self) -> Optional[str]:
        # source path is added to display file location for validation error messages
        # usually, base_path = Path(source_path).parent if source_path else os.getcwd()
        return self.__source_path

    @_source_path.setter
    def _source_path(self, value: Union[str, PathLike]):
        self.__source_path = Path(value).as_posix()

    @property
    def id(self) -> Optional[str]:
        """Resource ID.

        :return: Global id of the resource, Azure Resource Manager ID
        :rtype: Optional[str]
        """
        return self._id

    @property
    def creation_context(self) -> Optional[SystemData]:
        """Creation context.

        :return: Creation metadata of the resource.
        :rtype: Optional[~azure.ai.ml.entities.SystemData]
        """
        return self._creation_context

    @property
    def base_path(self) -> str:
        """Base path of the resource.

        :return: Base path of the resource
        :rtype: str
        """
        return self._base_path

    @abstractmethod
    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the object content into a file.

        :param dest: The destination to receive this object's data.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """

    @classmethod
    # pylint: disable=unused-argument
    def _resolve_cls_and_type(cls, data, params_override):
        """Resolve the class to use for deserializing the data. Return current class if no override is provided.

        :param data: Data to deserialize.
        :type data: dict
        :param params_override: Parameters to override.
        :type params_override: List[dict]
        :return: Class to use for deserializing the data & its "type". Type will be None if no override is provided.
        :rtype: tuple[class, Optional[str]]
        """
        return cls, None

    @classmethod
    @abstractmethod
    def _load(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "Resource":
        """Construct a resource object from a file. @classmethod.

        :param cls: Indicates that this is a class method.
        :type cls: class
        :param path: Path to a local file as the source.
        :type path: Union[PathLike, str]
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        :return: Resource
        :rtype: Resource
        """

    # pylint: disable:unused-argument
    def _get_arm_resource(
        self,
        **kwargs, # pylint: disable=unused-argument
    ):
        """Get arm resource.

        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict

        :return: Resource
        :rtype: dict
        """
        from azure.ai.ml._arm_deployments.arm_helper import get_template

        # pylint: disable=no-member
        template = get_template(resource_type=self._arm_type)
        # pylint: disable=no-member
        template["copy"]["name"] = f"{self._arm_type}Deployment"
        return template

    def _get_arm_resource_and_params(self, **kwargs):
        """Get arm resource and parameters.

        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict

        :return: Resource and parameters
        :rtype: dict
        """
        resource = self._get_arm_resource(**kwargs)
        # pylint: disable=no-member
        param = self._to_arm_resource_param(**kwargs)
        return [(resource, param)]

    def __repr__(self) -> str:
        var_dict = {k.strip("_"): v for (k, v) in vars(self).items()}
        return f"{self.__class__.__name__}({var_dict})"

    def __str__(self) -> str:
        return self.__repr__()
