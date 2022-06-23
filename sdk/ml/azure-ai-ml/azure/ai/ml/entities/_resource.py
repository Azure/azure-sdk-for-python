# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from abc import ABC, abstractmethod
from os import PathLike
from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2021_10_01.models import SystemData
from azure.ai.ml._restclient.v2021_10_01 import models
from msrest import Serializer


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
        self._base_path = kwargs.pop("base_path", "./")
        self._creation_context = kwargs.pop("creation_context", None)
        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._serialize.client_side_validation = False
        super().__init__(**kwargs)

    @property
    def id(self) -> Optional[str]:
        """Resource ID.

        :return: Global id of the resource, Azure Resource Manager ID
        :rtype: Optional[str]
        """
        return self._id

    @property
    def creation_context(self) -> Optional[SystemData]:
        """Creation context

        :return: Creation metadata of the resource.
        :rtype: Optional[SystemData]
        """
        return self._creation_context

    @property
    def base_path(self) -> str:
        """Base path of the resource

        :return: Base path of the resource
        :rtype: str
        """
        return self._base_path

    @abstractmethod
    def dump(self, path: Union[PathLike, str]) -> None:
        """Dump the object content into a file.

        :param path: Path to a local file as the target.
        :type path: Union[PathLike, str]
        """
        pass

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
        pass

    def _get_arm_resource(self, **kwargs):
        """Get arm resource

        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict

        :return: Resource
        :rtype: dict
        """
        from azure.ai.ml._arm_deployments.arm_helper import get_template

        template = get_template(resource_type=self._arm_type)
        template["copy"]["name"] = f"{self._arm_type}Deployment"
        return template

    def _get_arm_resource_and_params(self, **kwargs):
        """Get arm resource and parameters

        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict

        :return: Resource and parameters
        :rtype: dict
        """
        resource = self._get_arm_resource(**kwargs)
        param = self._to_arm_resource_param(**kwargs)
        return [(resource, param)]

    def __repr__(self) -> str:
        var_dict = {k.strip("_"): v for (k, v) in vars(self).items()}
        return f"{self.__class__.__name__}({var_dict})"

    def __str__(self) -> str:
        return self.__repr__()
