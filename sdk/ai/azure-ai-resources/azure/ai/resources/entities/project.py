# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Dict, Optional

from azure.ai.ml.entities import Workspace


# Effectively a lightweight wrapper around a v2 SDK workspace
class Project:
    """A Project is a lightweight object for orchestrating AI applications, and is parented by an AI resource.
    
    :param name: The name of the project.
    :type name: str
    :param ai_resource: The AI resource parent of the project.
    :type ai_resource: str
    :param description: The description of the project.
    :type description: Optional[str]
    :param tags: Tags associated with the project.
    :type tags: Optional[Dict[str, str]]
    :param display_name: The display name of the project.
    :type display_name: Optional[str]
    :param location: The location of the project.
    :type location: Optional[str]
    :param resource_group: The project's resource group name.
    :type resource_group: Optional[str]
    """

    def __init__(
        self,
        *,
        name: str,
        ai_resource: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        display_name: Optional[str] = None,
        location: Optional[str] = None,
        resource_group: Optional[str] = None,
        **kwargs,
    ) -> None:
        self._workspace = Workspace(
            name=name,
            workspace_hub=ai_resource,
            description=description,
            tags=tags,
            display_name=display_name,
            location=location,
            resource_group=resource_group,
            **kwargs,
        )

    @classmethod
    def _from_v2_workspace(cls, workspace: Workspace) -> "Project":
        """Create a project from a v2 AML SDK workspace. For internal use.

        :param workspace: The workspace object to convert into a workspace.
        :type workspace: ~azure.ai.ml.entities.Workspace

        :return: The converted project.
        :rtype: ~azure.ai.resources.entities.Project
        """
        # It's simpler to create a placeholder internal workspace, then overwrite the internal WC.
        # We don't need to worry about the potentially changing WC fields this way.
        project = cls(name="a", ai_resource="a")
        project._workspace = workspace
        return project

    # TODO test all accessors/setters
    @property
    def name(self) -> str:
        """The name of the project.

        :return: Name of the project.
        :rtype: str
        """
        return self._workspace.name

    @name.setter
    def name(self, value: str):
        """Set the name of the project.

        :param value: The name to assign to the project.
        :type value: str
        """
        if not value:
            return
        self._workspace.name = value

    @property
    def ai_resource(self) -> str:
        """The AI resource parent of the project.

        :return: Name of the AI resource.
        :rtype: str
        """
        return self._workspace.workspace_hub

    @ai_resource.setter
    def ai_resource(self, value: str):
        """Set the AI resource of the project.

        :param value: The AI resource to assign to the project.
        :type value: str
        """
        if not value:
            return
        self._workspace.workspace_hub = value

    @property
    def description(self) -> str:
        """The description of the project.

        :return: Name of the project.
        :rtype: str
        """
        return self._workspace.description

    @description.setter
    def description(self, value: str):
        """Set the description of the project.

        :param value: The description to assign to the project.
        :type value: str
        """
        if not value:
            return
        self._workspace.description = value

    @property
    def tags(self) -> str:
        """The project's tags.

        :return: The tags associated with the project.
        :rtype: str
        """
        return self._workspace.tags

    @tags.setter
    def tags(self, value: Dict[str, str]):
        """Set the project's tags

        :param value: Tags to assign to the project.
        :type value: Dict[str, str]
        """
        if not value:
            return
        self._workspace.tags = value

    @property
    def display_name(self) -> str:
        """The project display name

        :return: The project display name
        :rtype: str
        """
        return self._workspace.display_name

    @display_name.setter
    def display_name(self, value: str):
        """Set the project display name

        :param value: The display name to assign to the project.
        :type value: str
        """
        if not value:
            return
        self._workspace.display_name = value

    @property
    def location(self) -> str:
        """The location of the project.

        :return: The location of the project.
        :rtype: str
        """
        return self._workspace.location

    @location.setter
    def location(self, value: str):
        """Set the location of the project.

        :param value: The location to assign to the project.
        :type value: str
        """
        if not value:
            return
        self._workspace.location = value

    @property
    def resource_group(self) -> str:
        """The resource group associated with the project.

        :return: The name of the resource group associated with the project.
        :rtype: str
        """
        return self._workspace.resource_group

    @resource_group.setter
    def resource_group(self, value: str):
        """Set the project's resource group.

        :param value: The name of the resource group to assign to the project.
        :type value: str
        """
        if not value:
            return
        self._workspace.resource_group = value
