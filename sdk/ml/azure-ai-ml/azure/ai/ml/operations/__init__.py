# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains supported operations for Azure Machine Learning SDKv2.

Operations are classes contain logic to interact with backend services, usually auto generated operations call.
"""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore


from ._batch_deployment_operations import BatchDeploymentOperations
from ._batch_endpoint_operations import BatchEndpointOperations
from ._component_operations import ComponentOperations
from ._compute_operations import ComputeOperations
from ._data_operations import DataOperations
from ._datastore_operations import DatastoreOperations
from ._environment_operations import EnvironmentOperations
from ._featureset_operations import FeaturesetOperations
from ._featurestore_entity_operations import FeaturestoreEntityOperations
from ._feature_store_operations import FeatureStoreOperations
from ._job_operations import JobOperations
from ._model_operations import ModelOperations
from ._online_deployment_operations import OnlineDeploymentOperations
from ._online_endpoint_operations import OnlineEndpointOperations
from ._registry_operations import RegistryOperations
from ._schedule_operations import ScheduleOperations
from ._workspace_connections_operations import WorkspaceConnectionsOperations
from ._workspace_operations import WorkspaceOperations
from ._virtual_cluster_operations import VirtualClusterOperations
from ._workspace_outbound_rule_operations import WorkspaceOutboundRuleOperations

__all__ = [
    "ComputeOperations",
    "DatastoreOperations",
    "JobOperations",
    "ModelOperations",
    "WorkspaceOperations",
    "WorkspaceOutboundRuleOperations",
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
    "VirtualClusterOperations",
    "FeaturesetOperations",
    "FeaturestoreEntityOperations",
    "FeatureStoreOperations",
]
