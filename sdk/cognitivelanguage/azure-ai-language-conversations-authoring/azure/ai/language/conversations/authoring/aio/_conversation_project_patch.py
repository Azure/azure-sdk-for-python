from .operations import ConversationAuthoringProjectOperations
from .. import models as _models
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from typing import Any, Callable, Dict, IO, Iterator, List, Optional, TypeVar, Union, cast, overload
from collections.abc import MutableMapping

JSON = MutableMapping[str, Any]

class ConversationAuthoringProjectClientAsync:
    def __init__(self, operations: ConversationAuthoringProjectOperations, project_name: str):
        self._operations = operations
        self._project_name = project_name

    async def create_project(
            self,
            body: Union[
                _models.ConversationAuthoringCreateProjectDetails,
                JSON,
                IO[bytes]
            ],
            **kwargs: Any
        ) -> _models.ConversationAuthoringProjectMetadata:
            if not self._project_name:
                raise ValueError("project_name is required.")
            # Optionally inject project_name if the model has that field
            if isinstance(body, _models.ConversationAuthoringCreateProjectDetails):
                body.project_name = self._project_name
            return await self._operations.create_project(
                project_name=self._project_name,
                body=body,
                **kwargs
            )

    async def begin_delete_project(self, **kwargs) -> AsyncLROPoller[None]:
        return await self._operations.begin_delete_project(
            project_name=self._project_name,
            **kwargs
        )

    async def authorize_project_copy(
            self,
            *,
            allow_overwrite: Optional[bool] = None,
            project_kind: Union[str, _models.ConversationAuthoringProjectKind],
            storage_input_container_name: Optional[str] = None,
            **kwargs
        ) -> _models.ConversationAuthoringCopyProjectDetails:
            return await self._operations.authorize_project_copy(
                project_name=self._project_name,
                allow_overwrite=allow_overwrite,
                project_kind=project_kind,
                storage_input_container_name=storage_input_container_name,
                **kwargs
            )

    async def begin_assign_deployment_resources(
        self,
        body: Union[
            _models.ConversationAuthoringAssignDeploymentResourcesDetails,
            JSON,
            IO[bytes]
        ],
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_assign_deployment_resources(
            project_name=self._project_name,
            body=body,
            **kwargs
        )

    async def begin_copy_project(
        self,
        body: Union[
            _models.ConversationAuthoringCopyProjectDetails,
            JSON,
            IO[bytes]
        ],
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_copy_project(
            project_name=self._project_name,
            body=body,
            **kwargs
        )

    async def begin_cancel_training_job(
        self,
        job_id: str,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.ConversationAuthoringTrainingJobResult]:
        return await self._operations.begin_cancel_training_job(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )
    
    async def begin_export(
        self,
        *,
        asset_kind: Optional[str] = ...,
        exported_project_format: Optional[Union[str, _models.ConversationAuthoringExportedProjectFormat]] = ...,
        string_index_type: Union[str, _models.StringIndexType],
        trained_model_label: Optional[str] = ...,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_export(
            project_name=self._project_name,
            asset_kind=asset_kind,
            exported_project_format=exported_project_format,
            string_index_type=string_index_type,
            trained_model_label=trained_model_label,
            **kwargs
        )

    async def begin_import_method(
        self,
        body: Union[
            _models.ConversationAuthoringExportedProject,
            JSON,
            IO[bytes]
        ],
        *,
        exported_project_format: Optional[Union[str, _models.ConversationAuthoringExportedProjectFormat]] = ...,
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_import_method(
            project_name=self._project_name,
            body=body,
            exported_project_format=exported_project_format,
            **kwargs
        )

    async def begin_swap_deployments(
        self,
        body: Union[
            _models.ConversationAuthoringSwapDeploymentsDetails,
            JSON,
            IO[bytes]
        ],
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_swap_deployments(
            project_name=self._project_name,
            body=body,
            **kwargs
        )

    async def begin_train(
        self,
        body: Union[
            _models.ConversationAuthoringTrainingJobDetails,
            JSON,
            IO[bytes]
        ],
        **kwargs: Any
    ) -> AsyncLROPoller[_models.ConversationAuthoringTrainingJobResult]:
        return await self._operations.begin_train(
            project_name=self._project_name,
            body=body,
            **kwargs
        )

    async def begin_unassign_deployment_resources(
        self,
        body: Union[
            _models.ConversationAuthoringUnassignDeploymentResourcesDetails,
            JSON,
            IO[bytes],
        ],
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        return await self._operations.begin_unassign_deployment_resources(
            project_name=self._project_name,
            body=body,
            **kwargs,
        )


    async def get_assign_deployment_resources_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringDeploymentResourcesState:
        return await self._operations.get_assign_deployment_resources_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs,
        )


    async def get_copy_project_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringCopyProjectState:
        return await self._operations.get_copy_project_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs,
        )

    async def get_export_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringExportProjectState:
        return await self._operations.get_export_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs,
        )

    async def get_import_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringImportProjectState:
        return await self._operations.get_import_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs,
        )

    async def get_project(
        self,
        **kwargs: Any
    ) -> _models.ConversationAuthoringProjectMetadata:
        return await self._operations.get_project(
            project_name=self._project_name,
            **kwargs,
        )

    async def get_project_deletion_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringProjectDeletionState:
        return await self._operations.get_project_deletion_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs,
        )

    async def get_swap_deployments_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringSwapDeploymentsState:
        return await self._operations.get_swap_deployments_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs,
        )

    async def get_training_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringTrainingState:
        return await self._operations.get_training_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs,
        )

    async def get_unassign_deployment_resources_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringDeploymentResourcesState:
        return await self._operations.get_unassign_deployment_resources_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs,
        )