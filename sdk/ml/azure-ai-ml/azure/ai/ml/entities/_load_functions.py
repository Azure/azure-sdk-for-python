# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from os import PathLike
from typing import Union
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


def load_job(path: Union[PathLike, str], **kwargs) -> Job:

    """Construct a job object from a yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Loaded job object.
    :rtype: Job
    """
    return Job.load(path, **kwargs)


def load_workspace(path: Union[PathLike, str], **kwargs) -> Workspace:
    """Load a workspace object from a yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Loaded workspace object.
    :rtype: Workspace
    """
    return Workspace.load(path, **kwargs)


def load_datastore(path: Union[PathLike, str], **kwargs) -> Datastore:
    """Construct a datastore object from a yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Loaded datastore object.
    :rtype: Datastore
    """
    return Datastore.load(path, **kwargs)


def load_compute(path: Union[PathLike, str], **kwargs) -> Compute:
    """Construct a compute object from a yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Loaded compute object.
    :rtype: Compute
    """
    return Compute.load(path, **kwargs)


def load_component(path: Union[PathLike, str], **kwargs) -> Component:
    """Construct a component object from a yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Loaded component object.
    :rtype: Component
    """
    return Component.load(path, **kwargs)


def load_model(path: Union[PathLike, str], **kwargs) -> Model:
    """Construct a model object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Constructed model object.
    :rtype: Model
    """
    return Model.load(path, **kwargs)


def load_data(path: Union[PathLike, str], **kwargs) -> Data:
    """Construct a data object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Constructed data object.
    :rtype: Data
    """
    return Data.load(path, **kwargs)


def load_environment(path: Union[PathLike, str], **kwargs) -> Environment:
    """Construct a environment object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Constructed environment object.
    :rtype: Environment
    """
    return Environment.load(path, **kwargs)


def load_online_deployment(path: Union[PathLike, str], **kwargs) -> OnlineDeployment:
    """Construct a online deployment object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Constructed online deployment object.
    :rtype: OnlineDeployment
    """
    return OnlineDeployment.load(path, **kwargs)


def load_batch_deployment(path: Union[PathLike, str], **kwargs) -> BatchDeployment:
    """Construct a batch deployment object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Constructed batch deployment object.
    :rtype: BatchDeployment
    """
    return BatchDeployment.load(path, **kwargs)


def load_online_endpoint(path: Union[PathLike, str], **kwargs) -> OnlineEndpoint:
    """Construct a online endpoint object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Constructed online endpoint object.
    :rtype: OnlineEndpoint
    """
    return OnlineEndpoint.load(path, **kwargs)


def load_batch_endpoint(path: Union[PathLike, str], **kwargs) -> BatchEndpoint:
    """Construct a batch endpoint object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Constructed batch endpoint object.
    :rtype: BatchEndpoint
    """
    return BatchEndpoint.load(path, **kwargs)


def load_workspace_connection(path: Union[PathLike, str], **kwargs) -> WorkspaceConnection:
    """Construct a workspace connection object from yaml file.

    :param path: Path to a local file as the source.
    :type path: str
    :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
    :type params_override: list

    :return: Constructed workspace connection object.
    :rtype: WorkspaceConnection
    """
    return WorkspaceConnection.load(path, **kwargs)
