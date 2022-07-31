# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from os import PathLike
from typing import Union, Type
from azure.ai.ml.entities._assets._artifacts.code import Code
from azure.ai.ml.entities._assets._artifacts.data import Data
from azure.ai.ml.entities._assets._artifacts.model import Model
from azure.ai.ml.entities._assets.environment import Environment
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._compute.compute import Compute
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.entities._deployment.batch_deployment import BatchDeployment
from azure.ai.ml.entities._deployment.online_deployment import OnlineDeployment
from azure.ai.ml.entities._endpoint.batch_endpoint import BatchEndpoint
from azure.ai.ml.entities._endpoint.online_endpoint import OnlineEndpoint

from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._workspace.connections.workspace_connection import WorkspaceConnection
from azure.ai.ml.entities._workspace.workspace import Workspace
from azure.ai.ml.entities import CommandComponent, ParallelComponent, Resource
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget
from azure.ai.ml._utils.utils import load_yaml


def load_common(cls: Type[Resource], path: Union[PathLike, str], params_override: list = None, **kwargs) -> Resource:
    """Private function to load a yaml file to an entity object.

    :param cls: The entity class type.
    :type cls: type[Resource]
    :param path: _description_
    :type path: Union[PathLike, str]
    :param params_override: _description_, defaults to None
    :type params_override: list, optional
    :return: _description_
    :rtype: Resource
    """

    params_override = params_override or []
    yaml_dict = load_yaml(path)
    if yaml_dict is None:  # This happens when a YAML is empty.
        msg = "Target yaml file is empty: {}"
        raise ValidationException(
            message=msg.format(path),
            target=ErrorTarget.COMPONENT,
            no_personal_data_message=msg.format(path),
            error_category=ErrorCategory.USER_ERROR,
        )
    elif not isinstance(yaml_dict, dict):  # This happens when a YAML file is mal formatted.
        msg = "Expect dict but get {} after parsing yaml file: {}"
        raise ValidationException(
            message=msg.format(type(yaml_dict), path),
            target=ErrorTarget.COMPONENT,
            no_personal_data_message=msg.format(type(yaml_dict), ""),
            error_category=ErrorCategory.USER_ERROR,
        )
    return cls._load(data=yaml_dict, yaml_path=path, params_override=params_override, **kwargs)


def load_job(path: Union[PathLike, str], **kwargs) -> Job:

    """Construct a job object from a yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Loaded job object.
    :rtype: Job
    """
    return load_common(Job, path, **kwargs)


def load_workspace(path: Union[PathLike, str], **kwargs) -> Workspace:
    """Load a workspace object from a yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Loaded workspace object.
    :rtype: Workspace
    """
    return load_common(Workspace, path, **kwargs)


def load_datastore(path: Union[PathLike, str], **kwargs) -> Datastore:
    """Construct a datastore object from a yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Loaded datastore object.
    :rtype: Datastore
    """
    return load_common(Datastore, path, **kwargs)


def load_code(path: Union[PathLike, str], **kwargs) -> Code:
    """Construct a compute object from a yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Loaded compute object.
    :rtype: Compute
    """
    return load_common(Code, path, **kwargs)


def load_compute(path: Union[PathLike, str], **kwargs) -> Compute:
    """Construct a compute object from a yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Loaded compute object.
    :rtype: Compute
    """
    return load_common(Compute, path, **kwargs)


def load_component(path: Union[PathLike, str] = None, **kwargs) -> Union[CommandComponent, ParallelComponent]:
    """Load component from local or remote to a component function.

    For example:

    .. code-block:: python

        # Load a local component to a component function.
        component_func = load_component(path="custom_component/component_spec.yaml")
        # Load a remote component to a component function.
        component_func = load_component(client=ml_client, name="my_component", version=1)

        # Consuming the component func
        component = component_func(param1=xxx, param2=xxx)

    :param path: Local component yaml file.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]
    :param client: An MLClient instance.
    :type client: MLClient
    :param name: Name of the component.
    :type name: str
    :param version: Version of the component.
    :type version: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    :return: A function that can be called with parameters to get a `azure.ai.ml.entities.Component`
    :rtype: Union[CommandComponent, ParallelComponent]
    """

    client = kwargs.pop("client", None)
    name = kwargs.pop("name", None)
    version = kwargs.pop("version", None)

    if path:
        component_entity = load_common(Component, path, **kwargs)
    elif client and name and version:
        component_entity = client.components.get(name, version)
    else:
        msg = "One of (client, name, version), (yaml_file) should be provided."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.COMPONENT,
            error_category=ErrorCategory.USER_ERROR,
        )
    return component_entity


def load_model(path: Union[PathLike, str], **kwargs) -> Model:
    """Construct a model object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Constructed model object.
    :rtype: Model
    """
    return load_common(Model, path, **kwargs)


def load_data(path: Union[PathLike, str], **kwargs) -> Data:
    """Construct a data object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Constructed data object.
    :rtype: Data
    """
    return load_common(Data, path, **kwargs)


def load_environment(path: Union[PathLike, str], **kwargs) -> Environment:
    """Construct a environment object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Constructed environment object.
    :rtype: Environment
    """
    return load_common(Environment, path, **kwargs)


def load_online_deployment(path: Union[PathLike, str], **kwargs) -> OnlineDeployment:
    """Construct a online deployment object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Constructed online deployment object.
    :rtype: OnlineDeployment
    """
    return load_common(OnlineDeployment, path, **kwargs)


def load_batch_deployment(path: Union[PathLike, str], **kwargs) -> BatchDeployment:
    """Construct a batch deployment object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Constructed batch deployment object.
    :rtype: BatchDeployment
    """
    return load_common(BatchDeployment, path, **kwargs)


def load_online_endpoint(path: Union[PathLike, str], **kwargs) -> OnlineEndpoint:
    """Construct a online endpoint object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Constructed online endpoint object.
    :rtype: OnlineEndpoint
    """
    return load_common(OnlineEndpoint, path, **kwargs)


def load_batch_endpoint(path: Union[PathLike, str], **kwargs) -> BatchEndpoint:
    """Construct a batch endpoint object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Constructed batch endpoint object.
    :rtype: BatchEndpoint
    """
    return load_common(BatchEndpoint, path, **kwargs)


def load_workspace_connection(path: Union[PathLike, str], **kwargs) -> WorkspaceConnection:
    """Construct a workspace connection object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: List[Dict]

    :return: Constructed workspace connection object.
    :rtype: WorkspaceConnection
    """
    return load_common(WorkspaceConnection, path, **kwargs)
