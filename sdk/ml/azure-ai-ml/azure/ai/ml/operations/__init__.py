# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore


from ._batch_deployment_operations import BatchDeploymentOperations
from ._batch_endpoint_operations import BatchEndpointOperations
from ._component_operations import ComponentOperations
from ._compute_operations import ComputeOperations
from ._data_operations import DataOperations
from ._datastore_operations import DatastoreOperations
from ._environment_operations import EnvironmentOperations
from ._job_operations import JobOperations
from ._model_operations import ModelOperations
from ._online_deployment_operations import OnlineDeploymentOperations
from ._online_endpoint_operations import OnlineEndpointOperations
from ._workspace_connections_operations import WorkspaceConnectionsOperations
from ._workspace_operations import WorkspaceOperations

__all__ = [
    "ComputeOperations",
    "DatastoreOperations",
    "JobOperations",
    "ModelOperations",
    "WorkspaceOperations",
    "OnlineEndpointOperations",
    "BatchEndpointOperations",
    "OnlineDeploymentOperations",
    "BatchDeploymentOperations",
    "DataOperations",
    "EnvironmentOperations",
    "ComponentOperations",
    "WorkspaceConnectionsOperations",
]
