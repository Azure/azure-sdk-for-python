# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=client-accepts-api-version-keyword,(line-too-long,too-many-locals,no-member,too-many-statements,too-many-instance-attributes,too-many-lines,using-constant-test

import json
import logging
import os
from functools import singledispatch
from itertools import product
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, TypeVar, Union

from azure.ai.ml._azure_environments import (
    CloudArgumentKeys,
    _add_cloud_to_environments,
    _get_base_url_from_metadata,
    _get_cloud_information_from_metadata,
    _get_default_cloud_name,
    _set_cloud,
)
from azure.ai.ml._file_utils.file_utils import traverse_up_path_and_find_file
from azure.ai.ml._restclient.v2020_09_01_dataplanepreview import (
    AzureMachineLearningWorkspaces as ServiceClient092020DataplanePreview,
)
from azure.ai.ml._restclient.v2022_02_01_preview import AzureMachineLearningWorkspaces as ServiceClient022022Preview
from azure.ai.ml._restclient.v2022_05_01 import AzureMachineLearningWorkspaces as ServiceClient052022
from azure.ai.ml._restclient.v2022_10_01 import AzureMachineLearningWorkspaces as ServiceClient102022
from azure.ai.ml._restclient.v2022_10_01_preview import AzureMachineLearningWorkspaces as ServiceClient102022Preview
from azure.ai.ml._restclient.v2023_02_01_preview import AzureMachineLearningWorkspaces as ServiceClient022023Preview
from azure.ai.ml._restclient.v2023_04_01 import AzureMachineLearningWorkspaces as ServiceClient042023
from azure.ai.ml._restclient.v2023_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042023Preview
from azure.ai.ml._restclient.v2023_06_01_preview import AzureMachineLearningWorkspaces as ServiceClient062023Preview
from azure.ai.ml._restclient.v2023_08_01_preview import AzureMachineLearningWorkspaces as ServiceClient082023Preview

# Same object, but was renamed starting in v2023_08_01_preview
from azure.ai.ml._restclient.v2023_10_01 import AzureMachineLearningServices as ServiceClient102023
from azure.ai.ml._restclient.v2024_01_01_preview import AzureMachineLearningWorkspaces as ServiceClient012024Preview
from azure.ai.ml._restclient.v2024_04_01_preview import AzureMachineLearningWorkspaces as ServiceClient042024Preview
from azure.ai.ml._restclient.v2024_07_01_preview import AzureMachineLearningWorkspaces as ServiceClient072024Preview
from azure.ai.ml._restclient.workspace_dataplane import (
    AzureMachineLearningWorkspaces as ServiceClientWorkspaceDataplane,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationsContainer, OperationScope
from azure.ai.ml._telemetry.logging_handler import get_appinsights_log_handler
from azure.ai.ml._user_agent import USER_AGENT
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils._http_utils import HttpPipeline
from azure.ai.ml._utils._preflight_utils import get_deployments_operation
from azure.ai.ml._utils._registry_utils import get_registry_client
from azure.ai.ml._utils.utils import _is_https_url
from azure.ai.ml.constants._common import AzureMLResourceType, DefaultOpenEncoding
from azure.ai.ml.entities import (
    BatchDeployment,
    BatchEndpoint,
    Component,
    Compute,
    Datastore,
    Environment,
    Index,
    Job,
    MarketplaceSubscription,
    Model,
    ModelBatchDeployment,
    OnlineDeployment,
    OnlineEndpoint,
    PipelineComponentBatchDeployment,
    Registry,
    Schedule,
    ServerlessEndpoint,
    Workspace,
)
from azure.ai.ml.entities._assets import WorkspaceAssetReference
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml.operations import (
    AzureOpenAIDeploymentOperations,
    BatchDeploymentOperations,
    BatchEndpointOperations,
    ComponentOperations,
    ComputeOperations,
    DataOperations,
    DatastoreOperations,
    EnvironmentOperations,
    EvaluatorOperations,
    IndexOperations,
    JobOperations,
    MarketplaceSubscriptionOperations,
    ModelOperations,
    OnlineDeploymentOperations,
    OnlineEndpointOperations,
    RegistryOperations,
    ServerlessEndpointOperations,
    WorkspaceConnectionsOperations,
    WorkspaceOperations,
)
from azure.ai.ml.operations._code_operations import CodeOperations
from azure.ai.ml.operations._feature_set_operations import FeatureSetOperations
from azure.ai.ml.operations._feature_store_entity_operations import FeatureStoreEntityOperations
from azure.ai.ml.operations._feature_store_operations import FeatureStoreOperations
from azure.ai.ml.operations._local_deployment_helper import _LocalDeploymentHelper
from azure.ai.ml.operations._local_endpoint_helper import _LocalEndpointHelper
from azure.ai.ml.operations._schedule_operations import ScheduleOperations
from azure.ai.ml.operations._workspace_outbound_rule_operations import WorkspaceOutboundRuleOperations
from azure.core.credentials import TokenCredential
from azure.core.polling import LROPoller

module_logger = logging.getLogger(__name__)


# pylint: disable=too-many-public-methods
class MLClient:
    """A client class to interact with Azure ML services.

    Use this client to manage Azure ML resources such as workspaces, jobs, models, and so on.

    :param credential: The credential to use for authentication.
    :type credential: ~azure.core.credentials.TokenCredential
    :param subscription_id: The Azure subscription ID. Optional for registry assets only. Defaults to None.
    :type subscription_id: Optional[str]
    :param resource_group_name: The Azure resource group. Optional for registry assets only. Defaults to None.
    :type resource_group_name: Optional[str]
    :param workspace_name: The workspace to use in the client. Optional only for operations that are not
        workspace-dependent. Defaults to None.
    :type workspace_name: Optional[str]
    :param registry_name: The registry to use in the client. Optional only for operations that are not
        workspace-dependent. Defaults to None.
    :type registry_name: Optional[str]
    :keyword show_progress: Specifies whether or not to display progress bars for long-running operations (e.g.
        customers may consider setting this to False if not using this SDK in an interactive setup). Defaults to True.
    :paramtype show_progress: Optional[bool]
    :keyword enable_telemetry: Specifies whether or not to enable telemetry. Will be overridden to False if not in a
        Jupyter Notebook. Defaults to True if in a Jupyter Notebook.
    :paramtype enable_telemetry: Optional[bool]
    :keyword cloud: The cloud name to use. Defaults to "AzureCloud".
    :paramtype cloud: Optional[str]
    :raises ValueError: Raised if credential is None.
    :raises ~azure.ai.ml.ValidationException: Raised if both workspace_name and registry_name are provided.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_authentication.py
            :start-after: [START create_ml_client_default_credential]
            :end-before: [END create_ml_client_default_credential]
            :language: python
            :dedent: 8
            :caption: Creating the MLClient with Azure Identity credentials.

    .. admonition:: Example:

       .. literalinclude:: ../samples/ml_samples_authentication.py
            :start-after: [START create_ml_client_sovereign_cloud]
            :end-before: [END create_ml_client_sovereign_cloud]
            :language: python
            :dedent: 8
            :caption: When using sovereign domains (i.e. any cloud other than AZURE_PUBLIC_CLOUD), you must pass in the
                cloud name in kwargs and you must use an authority with DefaultAzureCredential.
    """

    # pylint: disable=client-method-missing-type-annotations
    def __init__(
        self,
        credential: TokenCredential,
        subscription_id: Optional[str] = None,
        resource_group_name: Optional[str] = None,
        workspace_name: Optional[str] = None,
        registry_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if credential is None:
            raise ValueError("credential can not be None")

        if registry_name and workspace_name:
            raise ValidationException(
                message="Both workspace_name and registry_name cannot be used together, for the ml_client.",
                no_personal_data_message="Both workspace_name and registry_name are used for ml_client.",
                target=ErrorTarget.GENERAL,
                error_category=ErrorCategory.USER_ERROR,
            )

        self._credential = credential
        self._ws_rg: Any = None
        self._ws_sub: Any = None
        show_progress = kwargs.pop("show_progress", True)
        enable_telemetry = kwargs.pop("enable_telemetry", True)
        self._operation_config = OperationConfig(show_progress=show_progress, enable_telemetry=enable_telemetry)

        if "cloud" in kwargs:
            cloud_name = kwargs["cloud"]
            if CloudArgumentKeys.CLOUD_METADATA in kwargs:
                try:
                    _add_cloud_to_environments(kwargs)
                except AttributeError as e:
                    module_logger.debug("Cloud already exists: %s", e)
                except LookupError as e:
                    module_logger.debug("Missing keyword: %s", e)
            else:
                module_logger.debug("%s key not found in kwargs", CloudArgumentKeys.CLOUD_METADATA)
        else:
            module_logger.debug("cloud key not found in kwargs")
            cloud_name = _get_default_cloud_name()

        self._cloud = cloud_name
        _set_cloud(cloud_name)
        if "cloud" not in kwargs:
            module_logger.debug(
                "Cloud input is missing. Using default Cloud setting in MLClient: '%s'.",
                cloud_name,
            )
        module_logger.debug("Cloud configured in MLClient: '%s'.", cloud_name)

        # Add cloud information to kwargs
        kwargs.update(_get_cloud_information_from_metadata(cloud_name))

        # registry_name is present when the operations need referring assets from registry.
        # the subscription, resource group, if provided, will be ignored and replaced by
        # whatever is received from the registry discovery service.
        workspace_location = None
        workspace_id = None
        registry_reference = kwargs.pop("registry_reference", None)
        if registry_name or registry_reference:
            # get the workspace location here if workspace_reference is provided
            self._ws_operation_scope = OperationScope(
                str(subscription_id),
                str(resource_group_name),
                workspace_name,
            )
            workspace_reference = kwargs.pop("workspace_reference", None)
            if workspace_reference or registry_reference:
                ws_ops = WorkspaceOperations(
                    OperationScope(str(subscription_id), str(resource_group_name), workspace_reference),
                    ServiceClient042023Preview(
                        credential=self._credential,
                        subscription_id=subscription_id,
                        **kwargs,
                    ),
                    self._credential,
                )
                self._ws_rg = resource_group_name
                self._ws_sub = subscription_id
                workspace_details = ws_ops.get(workspace_reference if workspace_reference else workspace_name)
                workspace_location, workspace_id = (
                    workspace_details.location,
                    workspace_details._workspace_id,
                )

            (
                self._service_client_10_2021_dataplanepreview,
                resource_group_name,
                subscription_id,
            ) = get_registry_client(
                self._credential, registry_name if registry_name else registry_reference, workspace_location, **kwargs
            )
            if not workspace_name:
                workspace_name = workspace_reference

        self._operation_scope = OperationScope(
            str(subscription_id),
            str(resource_group_name),
            workspace_name,
            registry_name,
            workspace_id,
            workspace_location,
        )

        # Cannot send multiple base_url as azure-cli sets the base_url automatically.
        kwargs.pop("base_url", None)
        _add_user_agent(kwargs)

        properties = {
            "subscription_id": subscription_id,
            "resource_group_name": resource_group_name,
        }
        if workspace_name:
            properties.update({"workspace_name": workspace_name})
        if registry_name:
            properties.update({"registry_name": registry_name})

        user_agent = kwargs.get("user_agent", None)

        app_insights_handler: Tuple = get_appinsights_log_handler(
            user_agent,
            **{"properties": properties},
            enable_telemetry=self._operation_config.enable_telemetry,
        )
        app_insights_handler_kwargs: Dict[str, Tuple] = {"app_insights_handler": app_insights_handler}

        base_url = _get_base_url_from_metadata(cloud_name=cloud_name, is_local_mfe=True)
        self._base_url = base_url
        self._kwargs = kwargs

        self._operation_container = OperationsContainer()

        # kwargs related to operations alone not all kwargs passed to MLClient are needed by operations
        ops_kwargs = app_insights_handler_kwargs
        if base_url:
            ops_kwargs["enforce_https"] = _is_https_url(base_url)

        self._service_client_09_2020_dataplanepreview = ServiceClient092020DataplanePreview(
            subscription_id=self._operation_scope._subscription_id,
            credential=self._credential,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_workspace_dataplane = ServiceClientWorkspaceDataplane(
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

        self._service_client_04_2023 = ServiceClient042023(
            credential=self._credential,
            subscription_id=(
                self._ws_operation_scope._subscription_id
                if registry_reference
                else self._operation_scope._subscription_id
            ),
            base_url=base_url,
            **kwargs,
        )

        self._service_client_06_2023_preview = ServiceClient062023Preview(
            credential=self._credential,
            subscription_id=self._operation_scope._subscription_id,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_08_2023_preview = ServiceClient082023Preview(
            credential=self._credential,
            subscription_id=self._operation_scope._subscription_id,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_10_2023 = ServiceClient102023(
            credential=self._credential,
            subscription_id=self._operation_scope._subscription_id,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_01_2024_preview = ServiceClient012024Preview(
            credential=self._credential,
            subscription_id=self._operation_scope._subscription_id,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_04_2024_preview = ServiceClient042024Preview(
            credential=self._credential,
            subscription_id=self._operation_scope._subscription_id,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_07_2024_preview = ServiceClient072024Preview(
            credential=self._credential,
            subscription_id=(
                self._ws_operation_scope._subscription_id
                if registry_reference
                else self._operation_scope._subscription_id
            ),
            base_url=base_url,
            **kwargs,
        )

        # A general purpose, user-configurable pipeline for making
        # http requests
        self._requests_pipeline = HttpPipeline(**kwargs)

        self._service_client_10_2022_preview = ServiceClient102022Preview(
            credential=self._credential,
            subscription_id=(
                self._ws_operation_scope._subscription_id
                if registry_reference
                else self._operation_scope._subscription_id
            ),
            base_url=base_url,
            **kwargs,
        )

        self._service_client_10_2022 = ServiceClient102022(
            credential=self._credential,
            subscription_id=self._operation_scope._subscription_id,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_02_2023_preview = ServiceClient022023Preview(
            credential=self._credential,
            subscription_id=self._operation_scope._subscription_id,
            base_url=base_url,
            **kwargs,
        )

        self._service_client_04_2023_preview = ServiceClient042023Preview(
            credential=self._credential,
            subscription_id=(
                self._ws_operation_scope._subscription_id
                if registry_reference
                else self._operation_scope._subscription_id
            ),
            base_url=base_url,
            **kwargs,
        )

        self._service_client_06_2023_preview = ServiceClient062023Preview(
            credential=self._credential,
            subscription_id=(
                self._ws_operation_scope._subscription_id
                if registry_reference
                else self._operation_scope._subscription_id
            ),
            base_url=base_url,
            **kwargs,
        )

        self._service_client_08_2023_preview = ServiceClient082023Preview(
            credential=self._credential,
            subscription_id=(
                self._ws_operation_scope._subscription_id
                if registry_reference
                else self._operation_scope._subscription_id
            ),
            base_url=base_url,
            **kwargs,
        )

        self._service_client_10_2023 = ServiceClient102023(
            credential=self._credential,
            subscription_id=(
                self._ws_operation_scope._subscription_id
                if registry_reference
                else self._operation_scope._subscription_id
            ),
            base_url=base_url,
            **kwargs,
        )

        self._service_client_01_2024_preview = ServiceClient012024Preview(
            credential=self._credential,
            subscription_id=(
                self._ws_operation_scope._subscription_id
                if registry_reference
                else self._operation_scope._subscription_id
            ),
            base_url=base_url,
            **kwargs,
        )

        self._service_client_04_2024_preview = ServiceClient042024Preview(
            credential=self._credential,
            subscription_id=(
                self._ws_operation_scope._subscription_id
                if registry_reference
                else self._operation_scope._subscription_id
            ),
            base_url=base_url,
            **kwargs,
        )

        self._workspaces = WorkspaceOperations(
            self._ws_operation_scope if registry_reference else self._operation_scope,
            self._service_client_07_2024_preview,
            self._operation_container,
            self._credential,
            requests_pipeline=self._requests_pipeline,
            dataplane_client=self._service_client_workspace_dataplane,
            **app_insights_handler_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.WORKSPACE, self._workspaces)  # type: ignore[arg-type]

        self._workspace_outbound_rules = WorkspaceOutboundRuleOperations(
            self._operation_scope,
            self._service_client_07_2024_preview,
            self._operation_container,
            self._credential,
            **kwargs,
        )

        # TODO make sure that at least one reviewer who understands operation initialization details reviews this
        self._registries = RegistryOperations(
            self._operation_scope,
            self._service_client_10_2022_preview,
            self._operation_container,
            self._credential,
            **app_insights_handler_kwargs,  # type: ignore[arg-type]
        )
        self._operation_container.add(AzureMLResourceType.REGISTRY, self._registries)  # type: ignore[arg-type]

        self._connections = WorkspaceConnectionsOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_04_2024_preview,
            self._operation_container,
            self._credential,
        )

        self._preflight = get_deployments_operation(
            credentials=self._credential,
            subscription_id=self._operation_scope._subscription_id,
        )

        self._compute = ComputeOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_08_2023_preview,
            self._service_client_04_2024_preview,
            **app_insights_handler_kwargs,  # type: ignore[arg-type]
        )
        self._operation_container.add(AzureMLResourceType.COMPUTE, self._compute)
        self._datastores = DatastoreOperations(
            operation_scope=self._operation_scope,
            operation_config=self._operation_config,
            serviceclient_2024_07_01_preview=self._service_client_07_2024_preview,
            serviceclient_2024_01_01_preview=self._service_client_01_2024_preview,
            **ops_kwargs,  # type: ignore[arg-type]
        )
        self._operation_container.add(AzureMLResourceType.DATASTORE, self._datastores)
        self._models = ModelOperations(
            self._operation_scope,
            self._operation_config,
            (
                self._service_client_10_2021_dataplanepreview
                if registry_name or registry_reference
                else self._service_client_08_2023_preview
            ),
            self._datastores,
            self._operation_container,
            requests_pipeline=self._requests_pipeline,
            control_plane_client=self._service_client_08_2023_preview,
            workspace_rg=self._ws_rg,
            workspace_sub=self._ws_sub,
            registry_reference=registry_reference,
            **app_insights_handler_kwargs,  # type: ignore[arg-type]
        )
        # Evaluators
        self._evaluators = EvaluatorOperations(
            self._operation_scope,
            self._operation_config,
            (
                self._service_client_10_2021_dataplanepreview
                if registry_name or registry_reference
                else self._service_client_08_2023_preview
            ),
            self._datastores,
            self._operation_container,
            requests_pipeline=self._requests_pipeline,
            control_plane_client=self._service_client_08_2023_preview,
            workspace_rg=self._ws_rg,
            workspace_sub=self._ws_sub,
            registry_reference=registry_reference,
            **app_insights_handler_kwargs,  # type: ignore[arg-type]
        )

        self._operation_container.add(AzureMLResourceType.MODEL, self._models)
        self._code = CodeOperations(
            self._ws_operation_scope if registry_reference else self._operation_scope,
            self._operation_config,
            self._service_client_10_2021_dataplanepreview if registry_name else self._service_client_04_2023,
            self._datastores,
            **ops_kwargs,  # type: ignore[arg-type]
        )
        self._operation_container.add(AzureMLResourceType.CODE, self._code)
        self._environments = EnvironmentOperations(
            self._ws_operation_scope if registry_reference else self._operation_scope,
            self._operation_config,
            self._service_client_10_2021_dataplanepreview if registry_name else self._service_client_04_2023_preview,
            self._operation_container,
            **ops_kwargs,  # type: ignore[arg-type]
        )
        self._operation_container.add(AzureMLResourceType.ENVIRONMENT, self._environments)
        self._local_endpoint_helper = _LocalEndpointHelper(requests_pipeline=self._requests_pipeline)
        self._local_deployment_helper = _LocalDeploymentHelper(self._operation_container)
        self._online_endpoints = OnlineEndpointOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_02_2022_preview,
            self._operation_container,
            self._local_endpoint_helper,
            self._credential,
            requests_pipeline=self._requests_pipeline,
            **ops_kwargs,  # type: ignore[arg-type]
        )
        self._batch_endpoints = BatchEndpointOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_10_2023,
            self._operation_container,
            self._credential,
            requests_pipeline=self._requests_pipeline,
            service_client_09_2020_dataplanepreview=self._service_client_09_2020_dataplanepreview,
            **ops_kwargs,  # type: ignore[arg-type]
        )
        self._operation_container.add(AzureMLResourceType.BATCH_ENDPOINT, self._batch_endpoints)
        self._operation_container.add(AzureMLResourceType.ONLINE_ENDPOINT, self._online_endpoints)
        self._online_deployments = OnlineDeploymentOperations(
            self._ws_operation_scope if registry_reference else self._operation_scope,
            self._operation_config,
            self._service_client_04_2023_preview,
            self._operation_container,
            self._local_deployment_helper,
            self._credential,
            **ops_kwargs,  # type: ignore[arg-type]
        )
        self._batch_deployments = BatchDeploymentOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_01_2024_preview,
            self._operation_container,
            credentials=self._credential,
            requests_pipeline=self._requests_pipeline,
            service_client_09_2020_dataplanepreview=self._service_client_09_2020_dataplanepreview,
            service_client_02_2023_preview=self._service_client_02_2023_preview,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.ONLINE_DEPLOYMENT, self._online_deployments)
        self._operation_container.add(AzureMLResourceType.BATCH_DEPLOYMENT, self._batch_deployments)
        self._data = DataOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_10_2021_dataplanepreview if registry_name else self._service_client_04_2023_preview,
            self._service_client_01_2024_preview,
            self._datastores,
            requests_pipeline=self._requests_pipeline,
            all_operations=self._operation_container,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.DATA, self._data)
        self._components = ComponentOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_10_2021_dataplanepreview if registry_name else self._service_client_01_2024_preview,
            self._operation_container,
            self._preflight,
            **ops_kwargs,  # type: ignore[arg-type]
        )
        self._operation_container.add(AzureMLResourceType.COMPONENT, self._components)
        self._jobs = JobOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_04_2023_preview,
            self._operation_container,
            self._credential,
            _service_client_kwargs=kwargs,
            requests_pipeline=self._requests_pipeline,
            service_client_01_2024_preview=self._service_client_01_2024_preview,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.JOB, self._jobs)
        self._schedules = ScheduleOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_06_2023_preview,
            self._service_client_01_2024_preview,
            self._operation_container,
            self._credential,
            _service_client_kwargs=kwargs,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.SCHEDULE, self._schedules)

        self._indexes = IndexOperations(
            operation_scope=self._operation_scope,
            operation_config=self._operation_config,
            credential=self._credential,
            all_operations=self._operation_container,
            datastore_operations=self._datastores,
            _service_client_kwargs=kwargs,
            requests_pipeline=self._requests_pipeline,
            **ops_kwargs,
        )
        self._operation_container.add(AzureMLResourceType.INDEX, self._indexes)

        try:
            from azure.ai.ml.operations._virtual_cluster_operations import VirtualClusterOperations

            self._virtual_clusters = VirtualClusterOperations(
                self._operation_scope,
                self._credential,
                _service_client_kwargs=kwargs,
                **ops_kwargs,  # type: ignore[arg-type]
            )
            self._operation_container.add(
                AzureMLResourceType.VIRTUALCLUSTER, self._virtual_clusters  # type: ignore[arg-type]
            )
        except Exception as ex:  # pylint: disable=broad-except
            module_logger.debug("Virtual Cluster operations could not be initialized due to %s ", ex)

        self._featurestores = FeatureStoreOperations(
            self._operation_scope,
            self._service_client_07_2024_preview,
            self._operation_container,
            self._credential,
            **app_insights_handler_kwargs,  # type: ignore[arg-type]
        )

        self._featuresets = FeatureSetOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_10_2023,
            self._service_client_08_2023_preview,
            self._datastores,
            **ops_kwargs,  # type: ignore[arg-type]
        )

        self._featurestoreentities = FeatureStoreEntityOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_10_2023,
            **ops_kwargs,  # type: ignore[arg-type]
        )
        self._azure_openai_deployments = AzureOpenAIDeploymentOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_04_2024_preview,
            self._connections,
        )

        self._serverless_endpoints = ServerlessEndpointOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_01_2024_preview,
            self._operation_container,
        )
        self._marketplace_subscriptions = MarketplaceSubscriptionOperations(
            self._operation_scope,
            self._operation_config,
            self._service_client_01_2024_preview,
        )
        self._operation_container.add(AzureMLResourceType.FEATURE_STORE, self._featurestores)  # type: ignore[arg-type]
        self._operation_container.add(AzureMLResourceType.FEATURE_SET, self._featuresets)
        self._operation_container.add(AzureMLResourceType.FEATURE_STORE_ENTITY, self._featurestoreentities)
        self._operation_container.add(AzureMLResourceType.SERVERLESS_ENDPOINT, self._serverless_endpoints)
        self._operation_container.add(AzureMLResourceType.MARKETPLACE_SUBSCRIPTION, self._marketplace_subscriptions)

    @classmethod
    def from_config(  # pylint: disable=C4758
        cls,
        credential: TokenCredential,
        *,
        path: Optional[Union[os.PathLike, str]] = None,
        file_name=None,
        **kwargs,
    ) -> "MLClient":
        """Returns a client from an existing Azure Machine Learning Workspace using a file configuration.

        This method provides a simple way to reuse the same workspace across multiple Python notebooks or projects.
        You can save a workspace's Azure Resource Manager (ARM) properties in a JSON configuration file using this
        format:

        .. code-block:: json

            {
                "subscription_id": "<subscription-id>",
                "resource_group": "<resource-group>",
                "workspace_name": "<workspace-name>"
            }

        Then, you can use this method to load the same workspace in different Python notebooks or projects without
        retyping the workspace ARM properties. Note that `from_config` accepts the same kwargs as the main
        `~azure.ai.ml.MLClient` constructor such as `cloud`.

        :param credential: The credential object for the workspace.
        :type credential: ~azure.core.credentials.TokenCredential
        :keyword path: The path to the configuration file or starting directory to search for the configuration file
            within. Defaults to None, indicating the current directory will be used.
        :paramtype path: Optional[Union[os.PathLike, str]]
        :keyword file_name: The configuration file name to search for when path is a directory path. Defaults to
            "config.json".
        :paramtype file_name: Optional[str]
        :keyword cloud: The cloud name to use. Defaults to "AzureCloud".
        :paramtype cloud: Optional[str]
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if "config.json", or file_name if overridden,
            cannot be found in directory. Details will be provided in the error message.
        :returns: The client for an existing Azure ML Workspace.
        :rtype: ~azure.ai.ml.MLClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/ml_samples_authentication.py
                :start-after: [START create_ml_client_from_config_default]
                :end-before: [END create_ml_client_from_config_default]
                :language: python
                :dedent: 8
                :caption: Creating an MLClient from a file named "config.json" in directory "src".

            .. literalinclude:: ../samples/ml_samples_authentication.py
                :start-after: [START create_ml_client_from_config_custom_filename]
                :end-before: [END create_ml_client_from_config_custom_filename]
                :language: python
                :dedent: 8
                :caption: Creating an MLClient from a file named "team_workspace_configuration.json" in the current
                    directory.
        """

        path = Path(".") if path is None else Path(path)
        found_path: Optional[Union[Path, str]]

        if path.is_file():
            found_path = path
        else:
            # Based on priority
            # Look in config dirs like .azureml, aml_config or plain directory
            # with None
            directories_to_look = [".azureml", "aml_config", None]
            if file_name:
                files_to_look = [file_name]
            else:
                files_to_look = ["config.json", "project.json"]

            found_path = None
            for curr_dir, curr_file in product(directories_to_look, files_to_look):
                module_logger.debug(
                    (
                        "No config file directly found, starting search from %s "
                        "directory, for %s file name to be present in "
                        "%s subdirectory"
                    ),
                    path,
                    curr_file,
                    curr_dir,
                )

                found_path = traverse_up_path_and_find_file(
                    path=path,
                    file_name=curr_file,
                    directory_name=curr_dir,
                    num_levels=20,
                )
                if found_path:
                    break

            if not found_path:
                msg = (
                    "We could not find config.json in: {} or in its parent directories. "
                    "Please provide the full path to the config file or ensure that "
                    "config.json exists in the parent directories."
                )
                raise ValidationException(
                    message=msg.format(path),
                    no_personal_data_message=msg.format("[path]"),
                    target=ErrorTarget.GENERAL,
                    error_category=ErrorCategory.USER_ERROR,
                )

        subscription_id, resource_group, workspace_name = MLClient._get_workspace_info(str(found_path))

        module_logger.info("Found the config file in: %s", found_path)
        return MLClient(
            credential=credential,
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            workspace_name=workspace_name,
            **kwargs,
        )

    @classmethod
    def _ml_client_cli(cls, credentials: TokenCredential, subscription_id: Optional[str], **kwargs) -> "MLClient":
        """This method provides a way to create MLClient object for cli to leverage cli context for authentication.

        With this we do not have to use AzureCliCredentials from azure-identity package (not meant for heavy usage). The
        credentials are passed by cli get_mgmt_service_client when it created a object of this class.

        :param credentials: The authentication credentials
        :type credentials: TokenCredential
        :param subscription_id: The subscription ID
        :type subscription_id: Optional[str]
        :return: An MLClient
        :rtype: ~azure.ai.ml.MLClient
        """

        ml_client = cls(credential=credentials, subscription_id=subscription_id, **kwargs)
        return ml_client

    @property
    def workspaces(self) -> WorkspaceOperations:
        """A collection of workspace-related operations. Also manages workspace
        sub-classes like projects and hubs.

        :return: Workspace operations
        :rtype: ~azure.ai.ml.operations.WorkspaceOperations
        """
        return self._workspaces

    @property
    def workspace_outbound_rules(self) -> WorkspaceOutboundRuleOperations:
        """A collection of workspace outbound rule related operations.

        :return: Workspace outbound rule operations
        :rtype: ~azure.ai.ml.operations.WorkspaceOutboundRuleOperations
        """
        return self._workspace_outbound_rules

    @property
    def registries(self) -> RegistryOperations:
        """A collection of registry-related operations.

        :return: Registry operations
        :rtype: ~azure.ai.ml.operations.RegistryOperations
        """
        return self._registries

    @property
    def feature_stores(self) -> FeatureStoreOperations:
        """A collection of feature store related operations.

        :return: FeatureStore operations
        :rtype: ~azure.ai.ml.operations.FeatureStoreOperations
        """
        return self._featurestores

    @property
    def feature_sets(self) -> FeatureSetOperations:
        """A collection of feature set related operations.

        :return: FeatureSet operations
        :rtype: ~azure.ai.ml.operations.FeatureSetOperations
        """
        return self._featuresets

    @property
    def feature_store_entities(self) -> FeatureStoreEntityOperations:
        """A collection of feature store entity related operations.

        :return: FeatureStoreEntity operations
        :rtype: ~azure.ai.ml.operations.FeatureStoreEntityOperations
        """
        return self._featurestoreentities

    @property
    def connections(self) -> WorkspaceConnectionsOperations:
        """A collection of connection related operations.

        :return: Connections operations
        :rtype: ~azure.ai.ml.operations.WorkspaceConnectionsOperations
        """
        return self._connections

    @property
    def jobs(self) -> JobOperations:
        """A collection of job related operations.

        :return: Job operations
        :rtype: ~azure.ai.ml.operations.JobOperations
        """
        return self._jobs

    @property
    def compute(self) -> ComputeOperations:
        """A collection of compute related operations.

        :return: Compute operations
        :rtype: ~azure.ai.ml.operations.ComputeOperations
        """
        return self._compute

    @property
    def models(self) -> ModelOperations:
        """A collection of model related operations.

        :return: Model operations
        :rtype: ~azure.ai.ml.operations.ModelOperations
        """
        return self._models

    @property
    @experimental
    def evaluators(self) -> EvaluatorOperations:
        """A collection of model related operations.

        :return: Model operations
        :rtype: ~azure.ai.ml.operations.ModelOperations
        """
        return self._evaluators

    @property
    def online_endpoints(self) -> OnlineEndpointOperations:
        """A collection of online endpoint related operations.

        :return: Online Endpoint operations
        :rtype: ~azure.ai.ml.operations.OnlineEndpointOperations
        """
        return self._online_endpoints

    @property
    def batch_endpoints(self) -> BatchEndpointOperations:
        """A collection of batch endpoint related operations.

        :return: Batch Endpoint operations
        :rtype: ~azure.ai.ml.operations.BatchEndpointOperations
        """
        return self._batch_endpoints

    @property
    def online_deployments(self) -> OnlineDeploymentOperations:
        """A collection of online deployment related operations.

        :return: Online Deployment operations
        :rtype: ~azure.ai.ml.operations.OnlineDeploymentOperations
        """
        return self._online_deployments

    @property
    def batch_deployments(self) -> BatchDeploymentOperations:
        """A collection of batch deployment related operations.

        :return: Batch Deployment operations.
        :rtype: ~azure.ai.ml.operations.BatchDeploymentOperations
        """
        return self._batch_deployments

    @property
    def datastores(self) -> DatastoreOperations:
        """A collection of datastore related operations.

        :return: Datastore operations.
        :rtype: ~azure.ai.ml.operations.DatastoreOperations
        """
        return self._datastores

    @property
    def environments(self) -> EnvironmentOperations:
        """A collection of environment related operations.

        :return: Environment operations.
        :rtype: ~azure.ai.ml.operations.EnvironmentOperations
        """
        return self._environments

    @property
    def data(self) -> DataOperations:
        """A collection of data related operations.

        :return: Data operations.
        :rtype: ~azure.ai.ml.operations.DataOperations
        """
        return self._data

    @property
    def components(self) -> ComponentOperations:
        """A collection of component related operations.

        :return: Component operations.
        :rtype: ~azure.ai.ml.operations.ComponentOperations
        """
        return self._components

    @property
    def schedules(self) -> ScheduleOperations:
        """A collection of schedule related operations.

        :return: Schedule operations.
        :rtype: ~azure.ai.ml.operations.ScheduleOperations
        """
        return self._schedules

    @property
    @experimental
    def serverless_endpoints(self) -> ServerlessEndpointOperations:
        """A collection of serverless endpoint related operations.

        :return: Serverless endpoint operations.
        :rtype: ~azure.ai.ml.operations.ServerlessEndpointOperations
        """
        return self._serverless_endpoints

    @property
    @experimental
    def marketplace_subscriptions(self) -> MarketplaceSubscriptionOperations:
        """A collection of marketplace subscription related operations.

        :return: Marketplace subscription operations.
        :rtype: ~azure.ai.ml.operations.MarketplaceSubscriptionOperations
        """
        return self._marketplace_subscriptions

    @property
    @experimental
    def indexes(self) -> IndexOperations:
        """A collection of index related operations.

        :return: Index operations.
        :rtype: ~azure.ai.ml.operations.IndexOperations
        """
        return self._indexes

    @property
    @experimental
    def azure_openai_deployments(self) -> AzureOpenAIDeploymentOperations:
        """A collection of Azure OpenAI deployment related operations.

        :return: Azure OpenAI deployment operations.
        :rtype: ~azure.ai.ml.operations.AzureOpenAIDeploymentOperations
        """
        return self._azure_openai_deployments

    @property
    def subscription_id(self) -> str:
        """Get the subscription ID of an MLClient object.

        :return: An Azure subscription ID.
        :rtype: str
        """
        return self._operation_scope.subscription_id

    @property
    def resource_group_name(self) -> str:
        """Get the resource group name of an MLClient object.

        :return: An Azure resource group name.
        :rtype: str
        """
        return self._operation_scope.resource_group_name

    @property
    def workspace_name(self) -> Optional[str]:
        """The name of the workspace where workspace-dependent operations will be executed.

        :return: The name of the default workspace.
        :rtype: Optional[str]
        """
        return self._operation_scope.workspace_name

    def _get_new_client(self, workspace_name: str, **kwargs) -> "MLClient":
        """Returns a new MLClient object with the specified arguments.

        :param workspace_name: AzureML workspace of the new MLClient.
        :type workspace_name: str
        :return: An updated MLClient
        :rtype: MLClient
        """

        return MLClient(
            credential=self._credential,
            subscription_id=self._operation_scope.subscription_id,
            resource_group_name=self._operation_scope.resource_group_name,
            workspace_name=workspace_name,
            **kwargs,
        )

    @classmethod
    def _get_workspace_info(cls, found_path: Optional[str]) -> Tuple[str, str, str]:
        with open(str(found_path), encoding=DefaultOpenEncoding.READ) as config_file:
            config = json.load(config_file)

        # Checking the keys in the config.json file to check for required parameters.
        scope = config.get("Scope")
        if not scope:
            if not all(k in config.keys() for k in ("subscription_id", "resource_group", "workspace_name")):
                msg = (
                    "The config file found in: {} does not seem to contain the required "
                    "parameters. Please make sure it contains your subscription_id, "
                    "resource_group and workspace_name."
                )
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
        else:
            pieces = scope.split("/")
            # User provided ARM parameters take precedence over values from config.json
            subscription_id_from_config = pieces[2]
            resource_group_from_config = pieces[4]
            workspace_name_from_config = pieces[8]
        return (
            subscription_id_from_config,
            resource_group_from_config,
            workspace_name_from_config,
        )

    # Leftover thoughts for anyone considering refactoring begin_create_or_update and create_or_update
    # Advantages of using generics+singledispatch (current impl)
    # - Minimal refactoring over previous iteration AKA Easy
    # - Only one docstring
    # Advantages of using @overload on public functions
    # - Custom docstring per overload
    # - More customized code per input type without needing @singledispatch helper function
    # IMO we don't need custom docstrings yet, so the former option's simplicity wins for now.

    # T = valid inputs/outputs for create_or_update
    # Each entry here requires a registered _create_or_update function below
    T = TypeVar("T", Job, Model, Environment, Component, Datastore)

    # pylint: disable-next=client-method-missing-tracing-decorator
    def create_or_update(
        self,
        entity: T,
        **kwargs,
    ) -> T:
        """Creates or updates an Azure ML resource.

        :param entity: The resource to create or update.
        :type entity: typing.Union[~azure.ai.ml.entities.Job
            , ~azure.ai.ml.entities.Model, ~azure.ai.ml.entities.Environment, ~azure.ai.ml.entities.Component
            , ~azure.ai.ml.entities.Datastore]
        :return: The created or updated resource.
        :rtype: typing.Union[~azure.ai.ml.entities.Job, ~azure.ai.ml.entities.Model
            , ~azure.ai.ml.entities.Environment, ~azure.ai.ml.entities.Component, ~azure.ai.ml.entities.Datastore]
        """

        return _create_or_update(entity, self._operation_container.all_operations, **kwargs)

    # R = valid inputs/outputs for begin_create_or_update
    # Each entry here requires a registered _begin_create_or_update function below
    R = TypeVar(
        "R",
        Workspace,
        Registry,
        Compute,
        OnlineDeployment,
        OnlineEndpoint,
        BatchDeployment,
        BatchEndpoint,
        Schedule,
    )

    # pylint: disable-next=client-method-missing-tracing-decorator
    def begin_create_or_update(
        self,
        entity: R,
        **kwargs,
    ) -> LROPoller[R]:
        """Creates or updates an Azure ML resource asynchronously.

        :param entity: The resource to create or update.
        :type entity: typing.Union[~azure.ai.ml.entities.Workspace
            , ~azure.ai.ml.entities.Registry, ~azure.ai.ml.entities.Compute, ~azure.ai.ml.entities.OnlineDeployment
            , ~azure.ai.ml.entities.OnlineEndpoint, ~azure.ai.ml.entities.BatchDeployment
            , ~azure.ai.ml.entities.BatchEndpoint, ~azure.ai.ml.entities.Schedule]
        :return: The resource after create/update operation.
        :rtype: azure.core.polling.LROPoller[typing.Union[~azure.ai.ml.entities.Workspace
            , ~azure.ai.ml.entities.Registry, ~azure.ai.ml.entities.Compute, ~azure.ai.ml.entities.OnlineDeployment
            , ~azure.ai.ml.entities.OnlineEndpoint, ~azure.ai.ml.entities.BatchDeployment
            , ~azure.ai.ml.entities.BatchEndpoint, ~azure.ai.ml.entities.Schedule]]
        """

        return _begin_create_or_update(entity, self._operation_container.all_operations, **kwargs)

    def __repr__(self) -> str:
        return f"""MLClient(credential={self._credential},
         subscription_id={self._operation_scope.subscription_id},
         resource_group_name={self._operation_scope.resource_group_name},
         workspace_name={self.workspace_name})"""


def _add_user_agent(kwargs) -> None:
    user_agent = kwargs.pop("user_agent", None)
    user_agent = f"{user_agent} {USER_AGENT}" if user_agent else USER_AGENT
    kwargs.setdefault("user_agent", user_agent)


@singledispatch
def _create_or_update(entity, operations, **kwargs):
    raise TypeError("Please refer to create_or_update docstring for valid input types.")


@_create_or_update.register(Job)
def _(entity: Job, operations, **kwargs):
    module_logger.debug("Creating or updating job")
    return operations[AzureMLResourceType.JOB].create_or_update(entity, **kwargs)


@_create_or_update.register(Model)
def _(entity: Model, operations):
    module_logger.debug("Creating or updating model")
    return operations[AzureMLResourceType.MODEL].create_or_update(entity)


@_create_or_update.register(WorkspaceAssetReference)
def _(entity: WorkspaceAssetReference, operations):
    module_logger.debug("Promoting model to registry")
    return operations[AzureMLResourceType.MODEL].create_or_update(entity)


@_create_or_update.register(Environment)
def _(entity: Environment, operations):
    module_logger.debug("Creating or updating environment")
    return operations[AzureMLResourceType.ENVIRONMENT].create_or_update(entity)


@_create_or_update.register(WorkspaceAssetReference)
def _(entity: WorkspaceAssetReference, operations):
    module_logger.debug("Promoting environment to registry")
    return operations[AzureMLResourceType.ENVIRONMENT].create_or_update(entity)


@_create_or_update.register(Component)
def _(entity: Component, operations, **kwargs):
    module_logger.debug("Creating or updating components")
    return operations[AzureMLResourceType.COMPONENT].create_or_update(entity, **kwargs)


@_create_or_update.register(Datastore)
def _(entity: Datastore, operations):
    module_logger.debug("Creating or updating datastores")
    return operations[AzureMLResourceType.DATASTORE].create_or_update(entity)


@_create_or_update.register(Index)
def _(entity: Index, operations, *args, **kwargs):
    module_logger.debug("Creating or updating indexes")
    return operations[AzureMLResourceType.INDEX].create_or_update(entity, **kwargs)


@singledispatch
def _begin_create_or_update(entity, operations, **kwargs):
    raise TypeError("Please refer to begin_create_or_update docstring for valid input types.")


@_begin_create_or_update.register(Workspace)
def _(entity: Workspace, operations, *args, **kwargs):
    module_logger.debug("Creating or updating workspaces")
    return operations[AzureMLResourceType.WORKSPACE].begin_create(entity, **kwargs)


@_begin_create_or_update.register(Registry)
def _(entity: Registry, operations, *args, **kwargs):
    module_logger.debug("Creating or updating registries")
    return operations[AzureMLResourceType.REGISTRY].begin_create_or_update(entity, **kwargs)


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


@_begin_create_or_update.register(ModelBatchDeployment)
def _(entity: ModelBatchDeployment, operations, *args, **kwargs):
    module_logger.debug("Creating or updating batch_deployments")
    return operations[AzureMLResourceType.BATCH_DEPLOYMENT].begin_create_or_update(entity, **kwargs)


@_begin_create_or_update.register(PipelineComponentBatchDeployment)
def _(entity: PipelineComponentBatchDeployment, operations, *args, **kwargs):
    module_logger.debug("Creating or updating batch_deployments")
    return operations[AzureMLResourceType.BATCH_DEPLOYMENT].begin_create_or_update(entity, **kwargs)


@_begin_create_or_update.register(Schedule)
def _(entity: Schedule, operations, *args, **kwargs):
    module_logger.debug("Creating or updating schedules")
    return operations[AzureMLResourceType.SCHEDULE].begin_create_or_update(entity, **kwargs)


@_begin_create_or_update.register(ServerlessEndpoint)
def _(entity: ServerlessEndpoint, operations, *args, **kwargs):
    module_logger.debug("Creating or updating serverless endpoints")
    return operations[AzureMLResourceType.SERVERLESS_ENDPOINT].begin_create_or_update(entity, **kwargs)


@_begin_create_or_update.register(MarketplaceSubscription)
def _(entity: MarketplaceSubscription, operations, *args, **kwargs):
    module_logger.debug("Creating or updating marketplace subscriptions")
    return operations[AzureMLResourceType.MARKETPLACE_SUBSCRIPTION].begin_create_or_update(entity, **kwargs)
