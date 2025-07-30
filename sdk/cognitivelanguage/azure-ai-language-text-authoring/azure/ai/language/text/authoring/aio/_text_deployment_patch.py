from .operations import TextAuthoringDeploymentOperations
from .. import models as _models
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from typing import Any, Callable, Dict, IO, Iterator, List, Optional, TypeVar, Union, cast, overload
from collections.abc import MutableMapping

JSON = MutableMapping[str, Any]

class TextAuthoringDeploymentClientAsync:
    def __init__(self, operations: TextAuthoringDeploymentOperations, project_name: str, deployment_name: str):
        self._operations = operations
        self._project_name = project_name
        self._deployment_name = deployment_name

    async def begin_delete_deployment(self, **kwargs: Any) -> AsyncLROPoller[None]:
        """Begin deleting the deployment."""
        return await self._operations.begin_delete_deployment(
            self._project_name,
            self._deployment_name,
            **kwargs
        )

    async def begin_delete_deployment_from_resources(
        self,
        body: Union[_models.TextAuthoringDeleteDeploymentDetails, dict, IO[bytes]],
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Begin deleting deployment from its assigned resources."""
        return await self._operations.begin_delete_deployment_from_resources(
            self._project_name,
            self._deployment_name,
            body=body,
            **kwargs
        )

    async def begin_deploy_project(
        self,
        body: Union[_models.TextAuthoringCreateDeploymentDetails, dict, IO[bytes]],
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Begin deploying the project to this deployment slot."""
        return await self._operations.begin_deploy_project(
            self._project_name,
            self._deployment_name,
            body=body,
            **kwargs
        )

    async def get_deployment(self, **kwargs: Any) -> _models.TextAuthoringProjectDeployment:
        """Get deployment metadata."""
        return await self._operations.get_deployment(
            self._project_name,
            self._deployment_name,
            **kwargs
        )

    async def get_deployment_delete_from_resources_status(self, job_id: str, **kwargs: Any) -> _models.TextAuthoringDeploymentDeleteFromResourcesState:
        """Get status of a deployment delete-from-resources operation."""
        return await self._operations.get_deployment_delete_from_resources_status(
            self._project_name,
            self._deployment_name,
            job_id,
            **kwargs
        )

    async def get_deployment_status(self, job_id: str, **kwargs: Any) -> _models.TextAuthoringDeploymentState:
        """Get status of a deployment creation/update/delete operation."""
        return await self._operations.get_deployment_status(
            self._project_name,
            self._deployment_name,
            job_id,
            **kwargs
        )