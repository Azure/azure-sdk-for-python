from .operations import ConversationAuthoringDeploymentOperations
from . import models as _models
from azure.core.polling import LROPoller
from typing import Any, Callable, Dict, IO, Iterator, List, Optional, TypeVar, Union, cast, overload
from collections.abc import MutableMapping

JSON = MutableMapping[str, Any]

class ConversationAuthoringDeploymentClient:
    def __init__(self, operations: ConversationAuthoringDeploymentOperations, project_name: str, deployment_name: str):
        self._operations = operations
        self._project_name = project_name
        self._deployment_name = deployment_name
    
    def begin_delete_deployment(self, **kwargs: Any) -> LROPoller[None]:
        return self._operations.begin_delete_deployment(
            project_name=self._project_name,
            deployment_name=self._deployment_name,
            **kwargs,
        )

    def begin_delete_deployment_from_resources(
        self,
        body: Union[_models.ConversationAuthoringDeleteDeploymentDetails, JSON, IO[bytes]],
        **kwargs: Any,
    ) -> LROPoller[None]:
        return self._operations.begin_delete_deployment_from_resources(
            project_name=self._project_name,
            deployment_name=self._deployment_name,
            body=body,
            **kwargs,
        )
    
    def begin_deploy_project(
        self,
        body: Union[_models.ConversationAuthoringCreateDeploymentDetails, dict, IO[bytes]],
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_deploy_project(
            self._project_name, self._deployment_name, body, **kwargs
        )

    def get_deployment(self, **kwargs: Any) -> _models.ConversationAuthoringProjectDeployment:
        return self._operations.get_deployment(
            self._project_name, self._deployment_name, **kwargs
        )
    
    def get_deployment_delete_from_resources_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringDeploymentDeleteFromResourcesState:
        return self._operations.get_deployment_delete_from_resources_status(
            self._project_name, self._deployment_name, job_id, **kwargs
        )
    
    def get_deployment_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringDeploymentState:
        return self._operations.get_deployment_status(
            self._project_name, self._deployment_name, job_id, **kwargs
        )
    
__all__ = ["ConversationAuthoringDeploymentClient"]