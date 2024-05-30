# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Any, Dict, Optional

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._schema.workspace import ProjectSchema
from azure.ai.ml.constants._common import WorkspaceKind
from azure.ai.ml.entities import Workspace


# Effectively a lightweight wrapper around a v2 SDK workspace
@experimental
class Project(Workspace):
    """A Project is a lightweight object for orchestrating AI applications, and is parented by a hub.
    Unlike a standard workspace, a project does not have a variety of sub-resources directly associated with it.
    Instead, its parent hub managed these resources, which are then used by the project and its siblings.

    As a type of workspace, project management is controlled by an MLClient's workspace operations.

    :param name: The name of the project.
    :type name: str
    :param hub_id: The hub parent of the project, as a resource ID.
    :type hub_id: str
    :param description: The description of the project.
    :type description: Optional[str]
    :param tags: Tags associated with the project.
    :type tags: Optional[Dict[str, str]]
    :param display_name: The display name of the project.
    :type display_name: Optional[str]
    :param location: The location of the project. Must match that of the parent hub
        and is automatically assigned to match the parent hub's location during creation.
    :type location: Optional[str]
    :param resource_group: The project's resource group name.
    :type resource_group: Optional[str]
    """

    def __init__(
        self,
        *,
        name: str,
        hub_id: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        display_name: Optional[str] = None,
        location: Optional[str] = None,
        resource_group: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Ensure user can't overwrite/double input kind.
        kwargs.pop("kind", None)
        super().__init__(
            name=name,
            description=description,
            tags=tags,
            kind=WorkspaceKind.PROJECT,
            display_name=display_name,
            location=location,
            resource_group=resource_group,
            hub_id=hub_id,
            **kwargs,
        )

    @classmethod
    def _get_schema_class(cls) -> Any:
        return ProjectSchema

    @property
    def hub_id(self) -> str:
        """The UID of the hub parent of the project.

        :return: Resource ID of the parent hub.
        :rtype: str
        """
        return self._hub_id if self._hub_id else ""

    @hub_id.setter
    def hub_id(self, value: str):
        """Set the parent hub id of the project.

        :param value: The hub id to assign to the project.
            Note: cannot be reassigned after creation.
        :type value: str
        """
        if not value:
            return
        self._hub_id = value
