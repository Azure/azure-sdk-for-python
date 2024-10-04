# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional

from azure.ai.ml._restclient.v2024_07_01_preview.models import ListWorkspaceKeysResult


class ContainerRegistryCredential:
    """Key for ACR associated with given workspace.

    :param location:  Location of the ACR
    :type location: str
    :param username: Username of the ACR
    :type username: str
    :param passwords: Passwords to access the ACR
    :type passwords: List[str]
    """

    def __init__(
        self, *, location: Optional[str] = None, username: Optional[str] = None, passwords: Optional[List[str]] = None
    ):
        self.location = location
        self.username = username
        self.passwords = passwords


class NotebookAccessKeys:
    """Key for notebook resource associated with given workspace.

    :param primary_access_key:  Primary access key of notebook resource
    :type primary_access_key: str
    :param secondary_access_key: Secondary access key of notebook resource
    :type secondary_access_key: str
    """

    def __init__(self, *, primary_access_key: Optional[str] = None, secondary_access_key: Optional[str] = None):
        self.primary_access_key = primary_access_key
        self.secondary_access_key = secondary_access_key


class WorkspaceKeys:
    """Workspace Keys.

    :param user_storage_key: Key for storage account associated with given workspace
    :type user_storage_key: str
    :param user_storage_resource_id: Resource id of storage account associated with given workspace
    :type user_storage_resource_id: str
    :param app_insights_instrumentation_key: Key for app insights associated with given workspace
    :type app_insights_instrumentation_key: str
    :param container_registry_credentials: Key for ACR associated with given workspace
    :type container_registry_credentials: ContainerRegistryCredential
    :param notebook_access_keys: Key for notebook resource associated with given workspace
    :type notebook_access_keys: NotebookAccessKeys
    """

    def __init__(
        self,
        *,
        user_storage_key: Optional[str] = None,
        user_storage_resource_id: Optional[str] = None,
        app_insights_instrumentation_key: Optional[str] = None,
        container_registry_credentials: Optional[ContainerRegistryCredential] = None,
        notebook_access_keys: Optional[NotebookAccessKeys] = None
    ):
        self.user_storage_key = user_storage_key
        self.user_storage_resource_id = user_storage_resource_id
        self.app_insights_instrumentation_key = app_insights_instrumentation_key
        self.container_registry_credentials = container_registry_credentials
        self.notebook_access_keys = notebook_access_keys

    @classmethod
    def _from_rest_object(cls, rest_obj: ListWorkspaceKeysResult) -> Optional["WorkspaceKeys"]:
        if not rest_obj:
            return None

        container_registry_credentials = None
        notebook_access_keys = None

        if hasattr(rest_obj, "container_registry_credentials") and rest_obj.container_registry_credentials is not None:
            container_registry_credentials = ContainerRegistryCredential(
                location=rest_obj.container_registry_credentials.location,
                username=rest_obj.container_registry_credentials.username,
                passwords=rest_obj.container_registry_credentials.passwords,
            )

        if hasattr(rest_obj, "notebook_access_keys") and rest_obj.notebook_access_keys is not None:
            notebook_access_keys = NotebookAccessKeys(
                primary_access_key=rest_obj.notebook_access_keys.primary_access_key,
                secondary_access_key=rest_obj.notebook_access_keys.secondary_access_key,
            )

        return WorkspaceKeys(
            user_storage_key=rest_obj.user_storage_key,
            user_storage_resource_id=rest_obj.user_storage_arm_id,
            app_insights_instrumentation_key=rest_obj.app_insights_instrumentation_key,
            container_registry_credentials=container_registry_credentials,
            notebook_access_keys=notebook_access_keys,
        )
