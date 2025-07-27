from .operations import ConversationAuthoringExportedModelOperations
import models as _models
from azure.core.polling import LROPoller
from typing import Any, IO, Union
from collections.abc import MutableMapping

JSON = MutableMapping[str, Any]

class ConversationAuthoringExportedModel:
    def __init__(self, operations: ConversationAuthoringExportedModelOperations, project_name: str, exported_model_name: str):
        self._operations = operations
        self._project_name = project_name
        self._exported_model_name = exported_model_name

    def begin_create_or_update_exported_model(
        self,
        body: Union[_models.ConversationAuthoringExportedModelDetails, JSON, IO[bytes]],
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_create_or_update_exported_model(
            project_name=self._project_name,
            exported_model_name=self._exported_model_name,
            body=body,
            **kwargs,
        )
    
    def begin_delete_exported_model(
        self,
        **kwargs: Any
    ) -> LROPoller[None]:
        return self._operations.begin_delete_exported_model(
            self._project_name, self._exported_model_name, **kwargs
        )

    def get_exported_model(
        self,
        **kwargs: Any
    ) -> _models.ConversationAuthoringExportedTrainedModel:
        return self._operations.get_exported_model(
            self._project_name, self._exported_model_name, **kwargs
        )

    def get_exported_model_job_status(
        self,
        job_id: str,
        **kwargs: Any
    ) -> _models.ConversationAuthoringExportedModelState:
        return self._operations.get_exported_model_job_status(
            self._project_name, self._exported_model_name, job_id, **kwargs
        )

__all__ = ["ConversationAuthoringExportedModel"]