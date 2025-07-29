from .operations import TextAuthoringProjectOperations
from .. import models as _models
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from typing import Any, Callable, Dict, IO, Iterator, List, Optional, TypeVar, Union, cast, overload
from collections.abc import MutableMapping

JSON = MutableMapping[str, Any]

class TextAuthoringProjectClientAsync:
    def __init__(self, operations: TextAuthoringProjectOperations, project_name: str):
        self._operations = operations
        self._project_name = project_name

    async def authorize_project_copy(
        self,
        body: Union[dict, IO[bytes]],
        **kwargs: Any
    ):
        return await self._operations.authorize_project_copy(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    async def begin_assign_deployment_resources(
        self,
        body: Union[_models.TextAuthoringAssignDeploymentResourcesDetails, dict, IO[bytes]],
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_assign_deployment_resources(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    async def begin_cancel_training_job(
        self,
        job_id: str,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TextAuthoringTrainingJobResult]:
        return await self._operations.begin_cancel_training_job(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    async def begin_copy_project(
        self,
        body: Union[_models.TextAuthoringCopyProjectDetails, dict, IO[bytes]],
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_copy_project(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    async def begin_delete_project(self, **kwargs: Any) -> AsyncLROPoller[None]:
        return await self._operations.begin_delete_project(
            project_name=self._project_name,
            **kwargs
        )

    async def begin_export(
        self,
        asset_kind: Optional[str],
        string_index_type: Union[str, _models.StringIndexType],
        trained_model_label: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_export(
            project_name=self._project_name,
            asset_kind=asset_kind,
            string_index_type=string_index_type,
            trained_model_label=trained_model_label,
            **kwargs
        )

    async def begin_import_method(
        self,
        body: Union[_models.TextAuthoringExportedProject, IO[bytes], Any],
        format: Optional[str] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_import_method(
            project_name=self._project_name,
            body=body,
            format=format,
            content_type="application/json",
            **kwargs
        )

    async def begin_swap_deployments(
        self,
        body: Union[_models.TextAuthoringSwapDeploymentsDetails, IO[bytes], Any],
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_swap_deployments(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    async def begin_train(
        self,
        body: Union[_models.TextAuthoringTrainingJobDetails, IO[bytes], Any],
        **kwargs: Any
    ) -> AsyncLROPoller[_models.TextAuthoringTrainingJobResult]:
        return await self._operations.begin_train(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    async def begin_unassign_deployment_resources(
        self,
        body: Union[_models.TextAuthoringUnassignDeploymentResourcesDetails, IO[bytes], Any],
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_unassign_deployment_resources(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    async def create_project(
        self,
        body: Union[_models.TextAuthoringCreateProjectDetails, IO[bytes], Any],
        **kwargs: Any
    ) -> _models.TextAuthoringProjectMetadata:
        if isinstance(body, _models.TextAuthoringCreateProjectDetails):
            body.project_name = self._project_name
        return await self._operations.create_project(
            project_name=self._project_name,
            body=body,
            content_type="application/merge-patch+json",
            **kwargs
        )
    
    async def get_assign_deployment_resources_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringDeploymentResourcesState:
        return await self._operations.get_assign_deployment_resources_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    async def get_copy_project_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringCopyProjectState:
        return await self._operations.get_copy_project_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    async def get_export_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringExportProjectState:
        return await self._operations.get_export_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    async def get_import_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringImportProjectState:
        return await self._operations.get_import_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    async def get_project(
        self, **kwargs: Any
    ) -> _models.TextAuthoringProjectMetadata:
        return await self._operations.get_project(
            project_name=self._project_name,
            **kwargs
        )

    async def get_project_deletion_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringProjectDeletionState:
        return await self._operations.get_project_deletion_status(
            job_id=job_id,
            **kwargs
        )

    async def get_swap_deployments_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringSwapDeploymentsState:
        return await self._operations.get_swap_deployments_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    async def get_training_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringTrainingState:
        return await self._operations.get_training_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    async def get_unassign_deployment_resources_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringDeploymentResourcesState:
        return await self._operations.get_unassign_deployment_resources_status(
            job_id=job_id,
            **kwargs
        )