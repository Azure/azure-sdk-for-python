# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import abc
import os
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, List, Optional, Tuple, Union, cast

from msrest import Serializer

from azure.ai.ml._restclient.v2022_10_01 import models
from azure.ai.ml._telemetry.logging_handler import in_jupyter_notebook
from azure.ai.ml._utils.utils import dump_yaml

from ..constants._common import BASE_PATH_CONTEXT_KEY
from ._system_data import SystemData


class Resource(abc.ABC):
    """Base class for entity classes.

    Resource is an abstract object that serves as a base for creating resources. It contains common properties and
    methods for all resources.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :param name: The name of the resource.
    :type name: str
    :param description: The description of the resource.
    :type description: Optional[str]
    :param tags: Tags can be added, removed, and updated.
    :type tags: Optional[dict]
    :param properties: The resource's property dictionary.
    :type properties: Optional[dict]
    :keyword print_as_yaml: Specifies if the the resource should print out as a YAML-formatted object. If False,
        the resource will print out in a more-compact style. By default, the YAML output is only used in Jupyter
        notebooks. Be aware that some bookkeeping values are shown only in the non-YAML output.
    :paramtype print_as_yaml: bool
    """

    def __init__(
        self,
        name: Optional[str],
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.description = description
        self.tags: Optional[Dict] = dict(tags) if tags else {}
        self.properties = dict(properties) if properties else {}
        # Conditional assignment to prevent entity bloat when unused.
        self._print_as_yaml = kwargs.pop("print_as_yaml", False)

        # Hide read only properties in kwargs
        self._id = kwargs.pop("id", None)
        self.__source_path: Union[str, PathLike] = kwargs.pop("source_path", "")
        self._base_path = kwargs.pop(BASE_PATH_CONTEXT_KEY, None) or os.getcwd()  # base path should never be None
        self._creation_context: Optional[SystemData] = kwargs.pop("creation_context", None)
        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._serialize.client_side_validation = False
        super().__init__(**kwargs)

    @property
    def _source_path(self) -> Union[str, PathLike]:
        # source path is added to display file location for validation error messages
        # usually, base_path = Path(source_path).parent if source_path else os.getcwd()
        return self.__source_path

    @_source_path.setter
    def _source_path(self, value: Union[str, PathLike]) -> None:
        self.__source_path = Path(value).as_posix()

    @property
    def id(self) -> Optional[str]:
        """The resource ID.

        :return: The global ID of the resource, an Azure Resource Manager (ARM) ID.
        :rtype: Optional[str]
        """
        if self._id is None:
            return None
        return str(self._id)

    @property
    def creation_context(self) -> Optional[SystemData]:
        """The creation context of the resource.

        :return: The creation metadata for the resource.
        :rtype: Optional[~azure.ai.ml.entities.SystemData]
        """
        return cast(Optional[SystemData], self._creation_context)

    @property
    def base_path(self) -> str:
        """The base path of the resource.

        :return: The base path of the resource.
        :rtype: str
        """
        return self._base_path

    @abc.abstractmethod
    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> Any:
        """Dump the object content into a file.

        :param dest: The local path or file stream to write the YAML content to.
            If dest is a file path, a new file will be created.
            If dest is an open file, the file will be written to directly.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """

    @classmethod
    # pylint: disable=unused-argument
    def _resolve_cls_and_type(cls, data: Dict, params_override: Optional[List[Dict]] = None) -> Tuple:
        """Resolve the class to use for deserializing the data. Return current class if no override is provided.

        :param data: Data to deserialize.
        :type data: dict
        :param params_override: Parameters to override, defaults to None
        :type params_override: typing.Optional[list]
        :return: Class to use for deserializing the data & its "type". Type will be None if no override is provided.
        :rtype: tuple[class, typing.Optional[str]]
        """
        return cls, None

    @classmethod
    @abc.abstractmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "Resource":
        """Construct a resource object from a file. @classmethod.

        :param cls: Indicates that this is a class method.
        :type cls: class
        :param data: Path to a local file as the source, defaults to None
        :type data: typing.Optional[typing.Dict]
        :param yaml_path: Path to a yaml file as the source, defaults to None
        :type yaml_path: typing.Optional[typing.Union[typing.PathLike, str]]
        :param params_override: Parameters to override, defaults to None
        :type params_override: typing.Optional[list]
        :return: Resource
        :rtype: Resource
        """

    # pylint: disable:unused-argument
    def _get_arm_resource(
        self,
        # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> Dict:
        """Get arm resource.

        :return: Resource
        :rtype: dict
        """
        from azure.ai.ml._arm_deployments.arm_helper import get_template

        # pylint: disable=no-member
        template = get_template(resource_type=self._arm_type)  # type: ignore
        # pylint: disable=no-member
        template["copy"]["name"] = f"{self._arm_type}Deployment"  # type: ignore
        return dict(template)

    def _get_arm_resource_and_params(self, **kwargs: Any) -> List:
        """Get arm resource and parameters.

        :return: Resource and parameters
        :rtype: dict
        """
        resource = self._get_arm_resource(**kwargs)
        # pylint: disable=no-member
        param = self._to_arm_resource_param(**kwargs)  # type: ignore
        return [(resource, param)]

    def __repr__(self) -> str:
        var_dict = {k.strip("_"): v for (k, v) in vars(self).items()}
        return f"{self.__class__.__name__}({var_dict})"

    def __str__(self) -> str:
        if self._print_as_yaml or in_jupyter_notebook():
            # pylint: disable=no-member
            yaml_serialized = self._to_dict()  # type: ignore
            return str(dump_yaml(yaml_serialized, default_flow_style=False))
        return self.__repr__()
