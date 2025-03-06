# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Literal, Type, TYPE_CHECKING
from enum import StrEnum

if TYPE_CHECKING:
    from .._resource import Resource


class ResourceIdentifiers(StrEnum):
    resource_group: Literal['resourcegroup'] = 'resourcegroup'
    user_assigned_identity: Literal['userassignedidentity'] = 'userassignedidentity'
    role_assignment: Literal['roleassignment'] = 'roleassignment'
    storage_account: Literal['storage'] = 'storage'
    blob_storage: Literal['storage:blobs'] = 'storage:blobs'
    datalake_storage: Literal['storage:datalake'] = 'storage:datalake'
    blob_container: Literal['storage:blobs:container'] = 'storage:blobs:container'
    file_system: Literal['storage:datalake:filesystem'] = 'storage:datalake:filesystem'
    table_storage: Literal['storage:tables'] = 'storage:tables'
    table: Literal['storage:tables:table'] = 'storage:tables:table'
    queue_storage: Literal['storage:queues'] = 'storage:queues'
    queue: Literal['storage:queues:queue'] = 'storage:queues:queue'
    file_storage: Literal['storage:files'] = 'storage:files'
    file_share: Literal['storage:files:share'] = 'storage:files:share'
    system_topic: Literal['events:systemtopic'] = 'events:systemtopic'
    system_topic_subscription: Literal['events:systemtopic:subscription'] = 'events:systemtopic:subscription'
    keyvault: Literal['keyvault'] = 'keyvault'
    keyvault_key: Literal['keyvault:key'] = 'keyvault:key'
    keyvault_secret: Literal['keyvault:secret'] = 'keyvault:secret'
    search: Literal['search'] = 'search'
    cognitive_services: Literal['cognitive_services'] = 'cognitive_services'
    ml_workspace: Literal['ml_workspace'] = 'ml_workspace'
    ai_services: Literal['ai'] = 'ai'
    ai_project: Literal['ai:project'] = 'ai:project'
    ai_hub: Literal['ai:hub'] = 'ai:hub'
    ai_deployment: Literal['ai:deployment'] = 'ai:deployment'
    ai_chat_deployment: Literal['ai:deployment:chat'] = 'ai:deployment:chat'
    ai_embeddings_deployment: Literal['ai:deployment:embeddings'] = 'ai:deployment:embeddings'
    ai_connection: Literal['ai:connection'] = 'ai:connection'

    def resource(self) -> Type['Resource']:
        if self.value == self.resource_group:
            from .resourcegroup import ResourceGroup
            return ResourceGroup
        if self.value == self.user_assigned_identity:
            from .managedidentity import UserAssignedIdentity
            return UserAssignedIdentity
        if self.value == self.role_assignment:
            from ._extension.roles import RoleAssignment
            return RoleAssignment
        if self.value == self.storage_account:
            from .storage import StorageAccount
            return StorageAccount
        if self.value == self.blob_storage:
            from .storage.blobs import BlobStorage
            return BlobStorage
        if self.value == self.datalake_storage:
            raise NotImplementedError()
        if self.value == self.blob_container:
            from .storage.blobs.container import BlobContainer
            return BlobContainer
        if self.value == self.file_system:
            raise NotImplementedError()
        if self.value == self.table_storage:
            from .storage.tables import TableStorage
            return TableStorage
        if self.value == self.table:
            raise NotImplementedError()
        if self.value == self.queue_storage:
            raise NotImplementedError()
        if self.value == self.queue:
            raise NotImplementedError()
        if self.value == self.file_storage:
            raise NotImplementedError()
        if self.value == self.file_share:
            raise NotImplementedError()
        if self.value == self.system_topic:
            raise NotImplementedError()
        if self.value == self.system_topic_subscription:
            raise NotImplementedError()
        if self.value == self.keyvault:
            from .keyvault import KeyVault
            return KeyVault
        if self.value == self.keyvault_key:
            raise NotImplementedError()
        if self.value == self.keyvault_secret:
            raise NotImplementedError()
        if self.value == self.search:
            from .search import SearchService
            return SearchService
        if self.value == self.cognitive_services:
            from .ai import CognitiveServicesAccount
            return CognitiveServicesAccount
        if self.value == self.ml_workspace:
            from .foundry import MLWorkspace
            return MLWorkspace
        if self.value == self.ai_services:
            from .ai import AIServices
            return AIServices
        if self.value == self.ai_project:
            from .foundry import AIProject
            return AIProject
        if self.value == self.ai_hub:
            from .foundry import AIHub
            return AIHub
        if self.value == self.ai_deployment:
            from .ai.deployment import AIDeployment
            return AIDeployment
        if self.value == self.ai_chat_deployment:
            from .ai.deployment import AIChat
            return AIChat
        if self.value == self.ai_embeddings_deployment:
            from .ai.deployment import AIEmbeddings
            return AIEmbeddings
        if self.value == self.ai_connection:
            from .foundry._connection import AIConnection
            return AIConnection
        raise TypeError(f"Unknown resource identifier: {self}")
