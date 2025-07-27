from .operations import ConversationAuthoringProjectOperations
from .models import _models
from azure.core.polling import LROPoller
from typing import Any, Callable, Dict, IO, Iterator, List, Optional, TypeVar, Union, cast, overload
from collections.abc import MutableMapping

JSON = MutableMapping[str, Any]

class ConversationAuthoringProject:
    def __init__(self, operations: ConversationAuthoringProjectOperations, project_name: str):
        self._operations = operations
        self._project_name = project_name

    def create_project(
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
            return self._operations.create_project(
                project_name=self._project_name,
                body=body,
                **kwargs
            )

    def begin_delete_project(self, **kwargs) -> LROPoller[None]:
        return self._operations.begin_delete_project(
            project_name=self._project_name,
            **kwargs
        )
    
    def authorize_project_copy(
            self,
            *,
            allow_overwrite: Optional[bool] = None,
            project_kind: Union[str, _models.ConversationAuthoringProjectKind],
            storage_input_container_name: Optional[str] = None,
            **kwargs
        ) -> _models.ConversationAuthoringCopyProjectDetails:
            return self._operations.authorize_project_copy(
                project_name=self._project_name,
                allow_overwrite=allow_overwrite,
                project_kind=project_kind,
                storage_input_container_name=storage_input_container_name,
                **kwargs
            )
    
    def begin_assign_deployment_resources(
        self,
        body: Union[
            _models.ConversationAuthoringAssignDeploymentResourcesDetails,
            JSON,
            IO[bytes]
        ],
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_assign_deployment_resources(
            project_name=self._project_name,
            body=body,
            **kwargs
        )

    def begin_copy_project(
        self,
        body: Union[
            _models.ConversationAuthoringCopyProjectDetails,
            JSON,
            IO[bytes]
        ],
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_copy_project(
            project_name=self._project_name,
            body=body,
            **kwargs
        )

    def begin_cancel_training_job(
        self,
        job_id: str,
        **kwargs: Any
    ) -> LROPoller[_models.ConversationAuthoringTrainingJobResult]:
        return self._operations.begin_cancel_training_job(
            project_name=self._project_name,
            job_id=job_id,
            **kwargs
        )