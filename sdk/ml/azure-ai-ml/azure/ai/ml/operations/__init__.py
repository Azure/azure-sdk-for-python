# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains supported operations for Azure Machine Learning SDKv2.

Operations are classes contain logic to interact with backend services, usually auto generated operations call.
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)


from ._azure_openai_deployment_operations import AzureOpenAIDeploymentOperations
from ._batch_deployment_operations import BatchDeploymentOperations
from ._batch_endpoint_operations import BatchEndpointOperations
from ._component_operations import ComponentOperations
from ._compute_operations import ComputeOperations
from ._data_operations import DataOperations
from ._datastore_operations import DatastoreOperations
from ._environment_operations import EnvironmentOperations
from ._feature_set_operations import FeatureSetOperations
from ._feature_store_entity_operations import FeatureStoreEntityOperations
from ._feature_store_operations import FeatureStoreOperations
from ._index_operations import IndexOperations
from ._job_operations import JobOperations
from ._model_operations import ModelOperations
from ._online_deployment_operations import OnlineDeploymentOperations
from ._online_endpoint_operations import OnlineEndpointOperations
from ._registry_operations import RegistryOperations
from ._schedule_operations import ScheduleOperations
from ._workspace_connections_operations import WorkspaceConnectionsOperations
from ._workspace_operations import WorkspaceOperations
from ._workspace_outbound_rule_operations import WorkspaceOutboundRuleOperations
from ._evaluator_operations import EvaluatorOperations
from ._serverless_endpoint_operations import ServerlessEndpointOperations
from ._marketplace_subscription_operations import MarketplaceSubscriptionOperations

__all__ = [
    "ComputeOperations",
    "DatastoreOperations",
    "JobOperations",
    "ModelOperations",
    "EvaluatorOperations",
    "WorkspaceOperations",
    "RegistryOperations",
    "OnlineEndpointOperations",
    "BatchEndpointOperations",
    "OnlineDeploymentOperations",
    "BatchDeploymentOperations",
    "DataOperations",
    "EnvironmentOperations",
    "ComponentOperations",
    "WorkspaceConnectionsOperations",
    "RegistryOperations",
    "ScheduleOperations",
    "WorkspaceOutboundRuleOperations",
    "FeatureSetOperations",
    "FeatureStoreEntityOperations",
    "FeatureStoreOperations",
    "ServerlessEndpointOperations",
    "MarketplaceSubscriptionOperations",
    "IndexOperations",
    "AzureOpenAIDeploymentOperations",
]
