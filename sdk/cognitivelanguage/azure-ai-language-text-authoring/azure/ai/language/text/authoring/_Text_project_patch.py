from .operations import TextAuthoringProjectOperations
from . import models as _models
from azure.core.polling import LROPoller
from typing import Any, Callable, Dict, IO, Iterator, List, Optional, TypeVar, Union, cast, overload
from collections.abc import MutableMapping

JSON = MutableMapping[str, Any]

class TextAuthoringProject:
    def __init__(self, operations: TextAuthoringProjectOperations, project_name: str):
        self._operations = operations
        self._project_name = project_name

    def authorize_project_copy(
        self,
        body: Union[dict, IO[bytes]],
        **kwargs: Any
    ):
        return self._operations.authorize_project_copy(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    def begin_assign_deployment_resources(
        self,
        body: Union[_models.TextAuthoringAssignDeploymentResourcesDetails, dict, IO[bytes]],
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_assign_deployment_resources(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    def begin_cancel_training_job(
        self,
        job_id: str,
        **kwargs: Any
    ) -> LROPoller[_models.TextAuthoringTrainingJobResult]:
        return self._operations.begin_cancel_training_job(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    def begin_copy_project(
        self,
        body: Union[_models.TextAuthoringCopyProjectDetails, dict, IO[bytes]],
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_copy_project(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    def begin_delete_project(self, **kwargs: Any) -> LROPoller[None]:
        return self._operations.begin_delete_project(
            project_name=self._project_name,
            **kwargs
        )
    
    def begin_export(
        self,
        asset_kind: Optional[str],
        string_index_type: Union[str, _models.StringIndexType],
        trained_model_label: Optional[str] = None,
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_export(
            project_name=self._project_name,
            asset_kind=asset_kind,
            string_index_type=string_index_type,
            trained_model_label=trained_model_label,
            **kwargs
        )

    def begin_import_method(
        self,
        body: Union[_models.TextAuthoringExportedProject, IO[bytes], Any],
        format: Optional[str] = None,
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_import_method(
            project_name=self._project_name,
            body=body,
            format=format,
            content_type="application/json",
            **kwargs
        )

    def begin_swap_deployments(
        self,
        body: Union[_models.TextAuthoringSwapDeploymentsDetails, IO[bytes], Any],
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_swap_deployments(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    def begin_train(
        self,
        body: Union[_models.TextAuthoringTrainingJobDetails, IO[bytes], Any],
        **kwargs: Any
    ) -> LROPoller[_models.TextAuthoringTrainingJobResult]:
        return self._operations.begin_train(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    def begin_unassign_deployment_resources(
        self,
        body: Union[_models.TextAuthoringUnassignDeploymentResourcesDetails, IO[bytes], Any],
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_unassign_deployment_resources(
            project_name=self._project_name,
            body=body,
            content_type="application/json",
            **kwargs
        )

    def create_project(
        self,
        body: Union[_models.TextAuthoringCreateProjectDetails, IO[bytes], Any],
        **kwargs: Any
    ) -> _models.TextAuthoringProjectMetadata:
        return self._operations.create_project(
            project_name=self._project_name,
            body=body,
            content_type="application/merge-patch+json",
            **kwargs
        )
    
    def get_assign_deployment_resources_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringDeploymentResourcesState:
        return self._operations.get_assign_deployment_resources_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    def get_copy_project_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringCopyProjectState:
        return self._operations.get_copy_project_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    def get_export_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringExportProjectState:
        return self._operations.get_export_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    def get_import_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringImportProjectState:
        return self._operations.get_import_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    def get_project(
        self, **kwargs: Any
    ) -> _models.TextAuthoringProjectMetadata:
        return self._operations.get_project(
            project_name=self._project_name,
            **kwargs
        )

    def get_project_deletion_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringProjectDeletionState:
        return self._operations.get_project_deletion_status(
            job_id=job_id,
            **kwargs
        )

    def get_swap_deployments_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringSwapDeploymentsState:
        return self._operations.get_swap_deployments_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )

    def get_training_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringTrainingState:
        return self._operations.get_training_status(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )
    
    def get_unassign_deployment_resources_status(
        self, job_id: str, **kwargs: Any
    ) -> _models.TextAuthoringDeploymentResourcesState:
        return self._operations.get_unassign_deployment_resources_status(
            job_id=job_id,
            **kwargs
        )