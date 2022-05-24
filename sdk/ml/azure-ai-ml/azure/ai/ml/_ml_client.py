# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
from functools import singledispatch
from itertools import product
from os import PathLike
from pathlib import Path
from typing import Optional, Tuple, Union
from azure.ai.ml._azure_environments import ENDPOINT_URLS, _get_cloud_details, _get_default_cloud_name, _set_cloud
import configparser

from azure.identity import ChainedTokenCredential
from azure.core.polling import LROPoller
from azure.ai.ml.entities._builders.base_node import BaseNode

from azure.ai.ml.constants import AzureMLResourceType
from azure.ai.ml._file_utils.file_utils import traverse_up_path_and_find_file
from azure.ai.ml._operations import (
    BatchDeploymentOperations,
    BatchEndpointOperations,
    CodeOperations,
    ComponentOperations,
    ComputeOperations,
    DataOperations,
    DatasetOperations,
    DatastoreOperations,
    EnvironmentOperations,
    JobOperations,
    ModelOperations,
    OnlineDeploymentOperations,
    OnlineEndpointOperations,
    WorkspaceOperations,
    _LocalDeploymentHelper,
    _LocalEndpointHelper,
)

from azure.ai.ml._operations.workspace_connections_operations import WorkspaceConnectionsOperations
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient092020DataplanePreview,
)
from azure.ai.ml._restclient.v2021_10_01 import AzureMachineLearningWorkspaces as ServiceClient102021
from azure.ai.ml._restclient.v2022_01_01_preview import AzureMachineLearningWorkspaces as ServiceClient012022Preview
from azure.ai.ml._restclient.v2022_02_01_preview import AzureMachineLearningWorkspaces as ServiceClient022022Preview
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._restclient.registry_discovery import AzureMachineLearningWorkspaces as ServiceClientRegistryDiscovery
from azure.ai.ml._user_agent import USER_AGENT
from azure.ai.ml._utils.utils import (
    _is_https_url,
    _get_mfe_base_url_from_registry_discovery_service,
)
from azure.ai.ml._utils._registry_utils import get_registry_service_client
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml._ml_exceptions import ErrorTarget, ErrorCategory, ValidationException
from azure.ai.ml.entities import (
    BatchDeployment,
    BatchEndpoint,
    Component,
    Compute,
    Datastore,
    Environment,
    Job,
    Model,
    OnlineDeployment,
    OnlineEndpoint,
    Workspace,
)

from azure.ai.ml._telemetry.logging_handler import get_appinsights_log_handler

module_logger = logging.getLogger(__name__)


class MLClient(object):
    """A client class to interact with Azure ML services.

    Use this client to manage Azure ML resources, e.g. workspaces, jobs, models and so on.
    """

    def __init__(
        self,
        credential: ChainedTokenCredential,
        subscription_id: str,
        resource_group_name: str,
        workspace_name: str = None,
        cloud_name: str = "AzureCloud",
        **kwargs,
    ):
        """Initiate Azure ML client

        :param credential: Credential to use for authentication.
        :type credential: ChainedTokenCredential
        :param subscription_id: Azure subscription ID.
        :type subscription_id: str
        :param resource_group_name: Azure resource group.
        :type resource_group_name: str
        :param workspace_name: Workspace to use in the client, optional for non workspace dependent operations., defaults to None
        :type workspace_name: str, optional
        :param cloud: The name of the target cloud. If no cloud is specified, any configured default from the Azure CLI
            is used. If no default is found, "AzureCloud" is used.
        :type cloud: str
        """
        module_logger.debug("Cloud configured in MLClient: '%s'.", cloud_name)
        _set_cloud(cloud_name)
        self._registry_name = kwargs.pop("registry_name", None)
        self._operation_scope = OperationScope(
            subscription_id, resource_group_name, workspace_name, self._registry_name, cloud_name
        )

        self._add_user_agent(kwargs)
        # Cannot send multiple base_url as azure-cli sets the base_url automatically.
        kwargs.pop("base_url", None)

        user_agent = None
        properties = {"subscription_id": subscription_id, "resource_group_name": resource_group_name}
        if workspace_name:
            properties.update({"workspace_name": workspace_name})
        if "user_agent" in kwargs:
            user_agent = kwargs.get("user_agent")
        app_insights_handler = get_appinsights_log_handler(user_agent, **{"properties": properties})
        app_insights_handler_kwargs = {"app_insights_handler": app_insights_handler}

        self._credential = credential

        cloud_details = _get_cloud_details(cloud_name)
        base_url = cloud_details.get(ENDPOINT_URLS.RESOURCE_MANAGER_ENDPOINT).strip("/")

        self._operation_container = OperationsContainer()

        self._rp_service_client = ServiceClient012022Preview(
            subscription_id=self._operation_scope._subscription_id,
            credential=self._credential,
            base_url=base_url,
            **kwargs,
        )
        # kwargs related to operations alone not all kwargs passed to MLClient are needed by operations
        ops_kwargs = app_insights_handler_kwargs
        if base_url:
            ops_kwargs["enforce_https"] = _is_https_url(base_url)

        self._service_client_10_2021 = ServiceClient102021(
            subscription_id=self._operation_scope._subscription_id,
            credential=self._credential,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_09_2020_dataplanepreview = ServiceClient092020DataplanePreview(
            subscription_id=self._operation_scope._subscription_id,
            credential=self._credential,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_02_2022_preview = ServiceClient022022Preview(
            subscription_id=self._operation_scope._subscription_id,
            credential=self._credential,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_05_2022 = ServiceClient052022(
            credential=self._credential,
            subscription_id=self._operation_scope._subscription_id,
            base_url=base_url,
            **kwargs,
        )

        self._workspaces = WorkspaceOperations(
            self._operation_scope,
            self._rp_service_client,
            self._operation_container,
            self._credential,
            base_url=base_url,
            **app_insights_handler_kwargs,
        )

        if self._registry_name:
            base_url = _get_mfe_base_url_from_registry_discovery_service(self._workspaces, workspace_name)
            kwargs_registry = {**kwargs}
            kwargs_registry.pop("base_url", None)
            self._service_client_registry_discovery_client = ServiceClientRegistryDiscovery(
                credential=self._credential, base_url=base_url, **kwargs_registry
            )
            self._service_client_10_2021_dataplanepreview = get_registry_service_client(
                subscription_id=self._operation_scope._subscription_id,
                registry_name=self._registry_name,
                credential=self._credential,
                service_client_registry_discovery_client=self._service_client_registry_discovery_client,
                **kwargs_registry,
            )

        self._workspace_connections = WorkspaceConnectionsOperations(
            self._operation_scope, self._rp_service_client, self._operation_container, self._credential
        )
        self._operation_container.add(AzureMLResourceType.WORKSPACE, self._workspaces)
        self._compute = ComputeOperations(self._operation_scope, self._rp_service_client, **app_insights_handler_kwargs)
        self._operation_container.add(AzureMLResourceType.COMPUTE, self._compute)
        self._datastores = DatastoreOperations(
            operation_scope=self._operation_scope,
            serviceclient_2022_05_01=self._service_client_05_2022,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.DATASTORE, self._datastores)
        self._models = ModelOperations(
            self._operation_scope, self._service_client_05_2022, self._datastores, **app_insights_handler_kwargs
        )
        self._operation_container.add(AzureMLResourceType.MODEL, self._models)
        self._code = CodeOperations(
            self._operation_scope,
            self._service_client_10_2021_dataplanepreview if self._registry_name else self._service_client_05_2022,
            self._datastores,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.CODE, self._code)
        self._environments = EnvironmentOperations(
            self._operation_scope,
            self._service_client_10_2021_dataplanepreview if self._registry_name else self._service_client_05_2022,
            self._operation_container,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.ENVIRONMENT, self._environments)
        self._local_endpoint_helper = _LocalEndpointHelper()
        self._local_deployment_helper = _LocalDeploymentHelper(self._operation_container)
        self._online_endpoints = OnlineEndpointOperations(
            self._operation_scope,
            self._service_client_02_2022_preview,
            self._operation_container,
            self._local_endpoint_helper,
            self._credential,
            **ops_kwargs,
        )
        self._batch_endpoints = BatchEndpointOperations(
            self._operation_scope,
            self._service_client_05_2022,
            self._service_client_09_2020_dataplanepreview,
            self._operation_container,
            self._credential,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.BATCH_ENDPOINT, self._batch_endpoints)
        self._operation_container.add(AzureMLResourceType.ONLINE_ENDPOINT, self._online_endpoints)
        self._online_deployments = OnlineDeploymentOperations(
            self._operation_scope,
            self._service_client_02_2022_preview,
            self._operation_container,
            self._local_deployment_helper,
            self._credential,
            **ops_kwargs,
        )

        self._batch_deployments = BatchDeploymentOperations(
            self._operation_scope,
            self._service_client_05_2022,
            self._service_client_09_2020_dataplanepreview,
            self._operation_container,
            self._credential,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.ONLINE_DEPLOYMENT, self._online_deployments)
        self._operation_container.add(AzureMLResourceType.BATCH_DEPLOYMENT, self._batch_deployments)
        self._data = DataOperations(
            self._operation_scope,
            self._service_client_05_2022,
            self._datastores,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.DATA, self._data)
        self._datasets = DatasetOperations(
            self._operation_scope, self._service_client_10_2021, self._datastores, **ops_kwargs
        )
        self._operation_container.add(AzureMLResourceType.DATASET, self._datasets)
        self._components = ComponentOperations(
            self._operation_scope,
            self._service_client_10_2021_dataplanepreview if self._registry_name else self._service_client_05_2022,
            self._operation_container,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.COMPONENT, self._components)
        self._jobs = JobOperations(
            self._operation_scope,
            self._service_client_02_2022_preview,
            self._operation_container,
            self._credential,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.JOB, self._jobs)

    @classmethod
    def from_config(
        cls, credential: ChainedTokenCredential, path: Union[PathLike, str] = None, _file_name=None, **kwargs
    ) -> "MLClient":
        """Return a workspace object from an existing Azure Machine Learning Workspace.

        Reads workspace configuration from a file. Throws an exception if the config file can't be found.

        The method provides a simple way to reuse the same workspace across multiple Python notebooks or projects.
        Users can save the workspace Azure Resource Manager (ARM) properties using the [workspace.write_config](https://docs.microsoft.com/python/api/azureml-core/azureml.core.workspace.workspace?view=azure-ml-py) method,
        and use this method to load the same workspace in different Python notebooks or projects without
        retyping the workspace ARM properties.

        :param credential: The credential object for the workspace.
        :type credential: azureml.core.authentication.ChainedTokenCredential
        :param path: The path to the config file or starting directory to search. The parameter defaults to starting the search in the current directory.
        :type path: str
        :param _file_name: Allows overriding the config file name to search for when path is a directory path.
        :type _file_name: str
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict

        :return: The workspace object for an existing Azure ML Workspace.
        :rtype: MLClient
        """

        path = Path(".") if path is None else Path(path)

        if path.is_file():
            found_path = path
        else:

            # Based on priority
            # Look in config dirs like .azureml, aml_config or plain directory
            # with None
            directories_to_look = [".azureml", "aml_config", None]
            if _file_name:
                files_to_look = [_file_name]
            else:
                files_to_look = ["config.json", "project.json"]

            found_path = None
            for curr_dir, curr_file in product(directories_to_look, files_to_look):
                module_logger.debug(
                    "No config file directly found, starting search from {} "
                    "directory, for {} file name to be present in "
                    "{} subdirectory".format(path, curr_file, curr_dir)
                )

                found_path = traverse_up_path_and_find_file(
                    path=path, file_name=curr_file, directory_name=curr_dir, num_levels=5
                )
                if found_path:
                    break

            if not found_path:
                msg = "We could not find config.json in: {} or in its parent directories. "
                "Please provide the full path to the config file or ensure that "
                "config.json exists in the parent directories."
                raise ValidationException(
                    message=msg.format(path),
                    no_personal_data_message=msg.format("[path]"),
                    target=ErrorTarget.GENERAL,
                    error_category=ErrorCategory.USER_ERROR,
                )

        subscription_id, resource_group, workspace_name, cloud_name = MLClient._get_workspace_info(found_path)

        module_logger.info("Found the config file in: %s", found_path)
        return MLClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name,
            cloud_name=cloud_name,
            **kwargs,
        )

    """
    This method provides a way to create MLClient object for cli to levarage cli context for authentication.
    With this we do not have to use AzureCliCredentials from azure-identity package (not meant for heavy usage).
    The credentials are passed by cli get_mgmt_service_client when it created a object of this class.
    """

    @classmethod
    def _ml_client_cli(cls, credentials, subscription_id, **kwargs):
        ml_client = cls(credential=credentials, subscription_id=subscription_id, **kwargs)
        return ml_client

    @property
    def workspaces(self) -> WorkspaceOperations:
        """A collection of workspace related operations

        :return: Workspace operations
        :rtype: WorkspaceOperations
        """
        return self._workspaces

    @property
    def connections(self) -> WorkspaceConnectionsOperations:
        """A collection of workspace connections related operations

        :return: Workspace Connections operations
        :rtype: WorkspaceConnectionsOperations
        """
        return self._workspace_connections

    @property
    def jobs(self) -> JobOperations:
        """A collection of job related operations

        :return: Job operations
        :rtype: JObOperations
        """
        return self._jobs

    @property
    def compute(self) -> ComputeOperations:
        """A collection of compute related operations

        :return: Compute operations
        :rtype: ComputeOperations
        """
        return self._compute

    @property
    def models(self) -> ModelOperations:
        """A collection of model related operations

        :return: Model operations
        :rtype: ModelOperations
        """
        return self._models

    @property
    def datasets(self) -> DatasetOperations:
        """A collection of datasets related operations

        :return: Dataset operations
        :rtype: DatasetOperations
        """
        return self._datasets

    @property
    def online_endpoints(self) -> OnlineEndpointOperations:
        """A collection of online endpoint related operations

        :return: Online Endpoint operations
        :rtype: OnlineEndpointOperations
        """
        return self._online_endpoints

    @property
    def batch_endpoints(self) -> BatchEndpointOperations:
        """A collection of batch endpoint related operations

        :return: Batch Endpoint operations
        :rtype: BatchEndpointOperations
        """
        return self._batch_endpoints

    @property
    def online_deployments(self) -> OnlineDeploymentOperations:
        """A collection of online deployment related operations

        :return: Online Deployment operations
        :rtype: OnlineDeploymentOperations
        """
        return self._online_deployments

    @property
    def batch_deployments(self) -> BatchDeploymentOperations:
        """A collection of batch deployment related operations

        :return: Batch Deployment operations
        :rtype: BatchDeploymentOperations
        """
        return self._batch_deployments

    @property
    def datastores(self) -> DatastoreOperations:
        """A collection of datastore related operations

        :return: Datastore operations
        :rtype: DatastoreOperations
        """
        return self._datastores

    @property
    def environments(self) -> EnvironmentOperations:
        """A collection of environment related operations

        :return: Environment operations
        :rtype: EnvironmentOperations
        """
        return self._environments

    @property
    def data(self) -> DataOperations:
        """A collection of data related operations

        :return: Data operations
        :rtype: DataOperations
        """
        return self._data

    @property
    def components(self) -> ComponentOperations:
        """A collection of component related operations

        :return: Component operations
        :rtype: ComponentOperations
        """
        return self._components

    @property
    def workspace_name(self) -> Optional[str]:
        """The workspace where workspace dependent operations will be executed in.

        :return: Default workspace name
        :rtype: Optional[str]
        """
        return self._operation_scope.workspace_name

    def _get_new_client(self, workspace_name: str) -> "MLClient":
        """Returns a new MLClient object with the specified arguments

        :param str workspace_name: AzureML workspace of the new MLClient
        """

        return MLClient(
            credential=self._credential,
            subscription_id=self._operation_scope.subscription_id,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=workspace_name,
        )

    @classmethod
    def _get_workspace_info(cls, found_path: str) -> Tuple[str, str, str, str]:
        with open(found_path, "r") as config_file:
            config = json.load(config_file)

        # Checking the keys in the config.json file to check for required parameters.
        scope = config.get("Scope")
        if not scope:
            if not all([k in config.keys() for k in ("subscription_id", "resource_group", "workspace_name")]):
                msg = "The config file found in: {} does not seem to contain the required "
                "parameters. Please make sure it contains your subscription_id, "
                "resource_group and workspace_name."
                raise ValidationException(
                    message=msg.format(found_path),
                    no_personal_data_message=msg.format("[found_path]"),
                    target=ErrorTarget.GENERAL,
                    error_category=ErrorCategory.USER_ERROR,
                )
            # User provided ARM parameters take precedence over values from config.json
            subscription_id_from_config = config["subscription_id"]
            resource_group_from_config = config["resource_group"]
            workspace_name_from_config = config["workspace_name"]
            cloud_name_from_config = config.get("cloud", None) or _get_default_cloud_name()
        else:
            pieces = scope.split("/")
            # User provided ARM parameters take precedence over values from config.json
            subscription_id_from_config = pieces[2]
            resource_group_from_config = pieces[4]
            workspace_name_from_config = pieces[8]
            # Read cloud information from .azure/cloud file
            cloud_name_from_config = self._get_cloud_name_from_config("config")
        return (
            subscription_id_from_config,
            resource_group_from_config,
            workspace_name_from_config,
            cloud_name_from_config,
        )

    def _get_cloud_name_from_config(self, cloud_config_file) -> str:
        config = configparser.ConfigParser()
        config.read(cloud_config_file)
        try:
            return config.get("cloud", "name")
        except (configparser.NoOptionError, configparser.NoSectionError):
            return _get_default_cloud_name()

    def _add_user_agent(self, kwargs) -> None:
        user_agent = kwargs.pop("user_agent", None)
        user_agent = f"{user_agent} {USER_AGENT}" if user_agent else USER_AGENT
        kwargs.setdefault("user_agent", user_agent)

    def create_or_update(
        self, entity: Union[Job, BaseNode, Model, Environment, Component, Datastore], **kwargs
    ) -> Union[Job, Model, Environment, Component, Datastore]:
        """Creates or updates an Azure ML resource.

        :param entity: The resource to create or update.
        :type entity: Union[azure.ai.ml.entities.Job, azure.ai.ml.entities.Model, azure.ai.ml.entities.Environment, azure.ai.ml.entities.Component, azure.ai.ml.entities.Datastore]
        :return: The created or updated resource
        :rtype: Union[azure.ai.ml.entities.Job, azure.ai.ml.entities.Model, azure.ai.ml.entities.Environment, azure.ai.ml.entities.Component, azure.ai.ml.entities.Datastore]
        """

        return _create_or_update(entity, self._operation_container.all_operations, **kwargs)

    def begin_create_or_update(
        self,
        entity: Union[Workspace, Compute, OnlineDeployment, OnlineEndpoint, BatchDeployment, BatchEndpoint],
        **kwargs,
    ) -> LROPoller:
        """Creates or updates an Azure ML resource asynchronously.

        :param entity: The resource to create or update.
        :type entity: Union[azure.ai.ml.entities.Workspace, azure.ai.ml.entities.Compute, azure.ai.ml.entities.OnlineDeployment, azure.ai.ml.entities.OnlineEndpoint, azure.ai.ml.entities.BatchDeployment, azure.ai.ml.entities.BatchEndpoint]
        :return: The resource after create/update operation
        :rtype: Optional[Union[azure.ai.ml.entities.Workspace, azure.ai.ml.entities.Compute, azure.ai.ml.entities.OnlineDeployment, azure.ai.ml.entities.OnlineEndpoint, azure.ai.ml.entities.BatchDeployment, azure.ai.ml.entities.BatchEndpoint]]
        """

        return _begin_create_or_update(entity, self._operation_container.all_operations, **kwargs)

    def __repr__(self) -> str:
        return f"""MLClient(credential={self._credential},
         subscription_id={self._operation_scope.subscription_id},
         resource_group_name={self._operation_scope.resource_group_name},
         workspace_name={self.workspace_name})"""


@singledispatch
def _create_or_update(entity, operations, **kwargs):
    raise NotImplementedError()


@_create_or_update.register(Job)
def _(entity: Job, operations, **kwargs):
    module_logger.debug("Creating or updating job")
    return operations[AzureMLResourceType.JOB].create_or_update(entity, **kwargs)


@_create_or_update.register(BaseNode)
def _(entity: Job, operations):
    module_logger.debug("Creating or updating job")
    return operations[AzureMLResourceType.JOB].create_or_update(entity)


@_create_or_update.register(Model)
def _(entity: Model, operations):
    module_logger.debug("Creating or updating model")
    return operations[AzureMLResourceType.MODEL].create_or_update(entity)


@_create_or_update.register(Environment)
def _(entity: Environment, operations):
    module_logger.debug("Creating or updating environment")
    return operations[AzureMLResourceType.ENVIRONMENT].create_or_update(entity)


@_create_or_update.register(Component)
def _(entity: Component, operations, **kwargs):
    module_logger.debug("Creating or updating components")
    return operations[AzureMLResourceType.COMPONENT].create_or_update(entity, **kwargs)


@_create_or_update.register(Datastore)
def _(entity: Datastore, operations):
    module_logger.debug("Creating or updating datastores")
    return operations[AzureMLResourceType.DATASTORE].create_or_update(entity)


@singledispatch
def _begin_create_or_update(entity, operations, **kwargs):
    raise NotImplementedError()


@_begin_create_or_update.register(Workspace)
def _(entity: Workspace, operations, *args, **kwargs):
    module_logger.debug("Creating or updating workspaces")
    return operations[AzureMLResourceType.WORKSPACE].begin_create(entity, **kwargs)


@_begin_create_or_update.register(Compute)
def _(entity: Compute, operations, *args, **kwargs):
    module_logger.debug("Creating or updating compute")
    return operations[AzureMLResourceType.COMPUTE].begin_create_or_update(entity, **kwargs)


@_begin_create_or_update.register(OnlineEndpoint)
def _(entity: OnlineEndpoint, operations, *args, **kwargs):
    module_logger.debug("Creating or updating online_endpoints")
    return operations[AzureMLResourceType.ONLINE_ENDPOINT].begin_create_or_update(entity, **kwargs)


@_begin_create_or_update.register(BatchEndpoint)
def _(entity: BatchEndpoint, operations, *args, **kwargs):
    module_logger.debug("Creating or updating batch_endpoints")
    return operations[AzureMLResourceType.BATCH_ENDPOINT].begin_create_or_update(entity, **kwargs)


@_begin_create_or_update.register(OnlineDeployment)
def _(entity: OnlineDeployment, operations, *args, **kwargs):
    module_logger.debug("Creating or updating online_deployments")
    return operations[AzureMLResourceType.ONLINE_DEPLOYMENT].begin_create_or_update(entity, **kwargs)


@_begin_create_or_update.register(BatchDeployment)
def _(entity: BatchDeployment, operations, *args, **kwargs):
    module_logger.debug("Creating or updating batch_deployments")
    return operations[AzureMLResourceType.BATCH_DEPLOYMENT].begin_create_or_update(entity, **kwargs)
