from .operations import ConversationAuthoringProjectOperations
from .models import _models
from azure.core.polling import LROPoller

class ConversationAuthoringProject:
    def __init__(self, operations: ConversationAuthoringProjectOperations, project_name: str):
        self._operations = operations
        self._project_name = project_name

    def create_project(self, body, **kwargs) -> _models.ConversationAuthoringProjectMetadata:
        if not self._project_name:
            raise ValueError("project_name is required.")
        body.project_name = self._project_name  # Optional: inject if body allows it
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