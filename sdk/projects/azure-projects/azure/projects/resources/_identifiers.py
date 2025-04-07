# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Dict, Type, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .._resource import Resource


class ResourceIdentifiers(Enum):
    resource_group = "resourcegroup"
    user_assigned_identity = "userassignedidentity"
    role_assignment = "roleassignment"
    storage_account = "storage"
    blob_storage = "storage:blobs"
    datalake_storage = "storage:datalake"
    blob_container = "storage:blobs:container"
    file_system = "storage:datalake:filesystem"
    table_storage = "storage:tables"
    table = "storage:tables:table"
    queue_storage = "storage:queues"
    queue = "storage:queues:queue"
    file_storage = "storage:files"
    file_share = "storage:files:share"
    system_topic = "events:systemtopic"
    system_topic_subscription = "events:systemtopic:subscription"
    keyvault = "keyvault"
    keyvault_key = "keyvault:key"
    keyvault_secret = "keyvault:secret"
    search = "search"
    cognitive_services = "cognitive_services"
    ml_workspace = "ml_workspace"
    ai_services = "ai"
    ai_project = "ai:project"
    ai_hub = "ai:hub"
    ai_deployment = "ai:deployment"
    ai_chat_deployment = "ai:deployment:chat"
    ai_embeddings_deployment = "ai:deployment:embeddings"
    ai_connection = "ai:connection"
    config_store = "appconfig"
    config_setting = "appconfig.setting"
    app_service_plan = "appservice:plan"
    app_service_site = "appservice:site"
    app_service_site_config = "appservice:site:config"

    def resource(  # pylint: disable=too-many-branches,too-many-statements,too-many-return-statements
        self,
    ) -> Type["Resource"]:
        if self == self.resource_group:
            from .resourcegroup._resource import ResourceGroup

            return ResourceGroup
        if self == self.user_assigned_identity:
            from .managedidentity._resource import UserAssignedIdentity

            return UserAssignedIdentity
        if self == self.role_assignment:
            from ._extension.roles import RoleAssignment

            return RoleAssignment
        if self == self.storage_account:
            from .storage._resource import StorageAccount

            return StorageAccount
        if self == self.blob_storage:
            from .storage.blobs._resource import BlobStorage

            return BlobStorage
        if self == self.datalake_storage:
            raise NotImplementedError()
        if self == self.blob_container:
            from .storage.blobs.container._resource import BlobContainer

            return BlobContainer
        if self == self.file_system:
            raise NotImplementedError()
        if self == self.table_storage:
            from .storage.tables._resource import TableStorage

            return TableStorage
        if self == self.table:
            from .storage.tables.table._resource import Table

            return Table
        if self == self.queue_storage:
            raise NotImplementedError()
        if self == self.queue:
            raise NotImplementedError()
        if self == self.file_storage:
            raise NotImplementedError()
        if self == self.file_share:
            raise NotImplementedError()
        if self == self.system_topic:
            raise NotImplementedError()
        if self == self.system_topic_subscription:
            raise NotImplementedError()
        if self == self.keyvault:
            from .keyvault._resource import KeyVault

            return KeyVault
        if self == self.keyvault_key:
            raise NotImplementedError()
        if self == self.keyvault_secret:
            raise NotImplementedError()
        if self == self.search:
            from .search._resource import SearchService

            return SearchService
        if self == self.cognitive_services:
            from .ai._resource import CognitiveServicesAccount

            return CognitiveServicesAccount
        if self == self.ml_workspace:
            from .foundry._resource import MLWorkspace

            return MLWorkspace
        if self == self.ai_services:
            from .ai._resource import AIServices

            return AIServices
        if self == self.ai_project:
            from .foundry._resource import AIProject

            return AIProject
        if self == self.ai_hub:
            from .foundry._resource import AIHub

            return AIHub
        if self == self.ai_deployment:
            from .ai.deployment._resource import AIDeployment

            return AIDeployment
        if self == self.ai_chat_deployment:
            from .ai.deployment._resource import AIChat

            return AIChat
        if self == self.ai_embeddings_deployment:
            from .ai.deployment._resource import AIEmbeddings

            return AIEmbeddings
        if self == self.ai_connection:
            from .foundry._connection import AIConnection

            return AIConnection
        if self == self.config_store:
            from .appconfig._resource import ConfigStore

            return ConfigStore
        if self == self.config_setting:
            from .appconfig.setting._resource import ConfigSetting

            return ConfigSetting
        if self == self.app_service_plan:
            from .appservice._resource import AppServicePlan

            return AppServicePlan
        if self == self.app_service_site:
            from .appservice.site._resource import AppSite

            return AppSite
        if self == self.app_service_site_config:
            from .appservice.site._config import SiteConfig

            return SiteConfig
        raise TypeError(f"Unknown resource identifier: {self}")


RESOURCE_FROM_CLIENT_ANNOTATION: Dict[str, ResourceIdentifiers] = {
    "BlobServiceClient": ResourceIdentifiers.blob_storage,
    "DataLakeServiceClient": ResourceIdentifiers.blob_storage,
    "ContainerClient": ResourceIdentifiers.blob_container,
    "FileSystemClient": ResourceIdentifiers.blob_container,
    "TableServiceClient": ResourceIdentifiers.table_storage,
    "TableClient": ResourceIdentifiers.table,
    "ShareServiceClient": ResourceIdentifiers.file_share,
    "ShareClient": ResourceIdentifiers.file_share,
    "QueueServiceClient": ResourceIdentifiers.queue_storage,
    "KeyClient": ResourceIdentifiers.keyvault,
    "SecretClient": ResourceIdentifiers.keyvault,
    "CertificateClient": ResourceIdentifiers.keyvault,
    "ChatCompletionsClient": ResourceIdentifiers.ai_chat_deployment,
    "Chat": ResourceIdentifiers.ai_chat_deployment,
    "Completions": ResourceIdentifiers.ai_chat_deployment,
    "AsyncChat": ResourceIdentifiers.ai_chat_deployment,
    "AsyncCompletions": ResourceIdentifiers.ai_chat_deployment,
    "EmbeddingsClient": ResourceIdentifiers.ai_embeddings_deployment,
    "Embeddings": ResourceIdentifiers.ai_embeddings_deployment,
    "AsyncEmbeddings": ResourceIdentifiers.ai_embeddings_deployment,
    "AIServices": ResourceIdentifiers.ai_services,
    "AIHub": ResourceIdentifiers.ai_hub,
    "AIProject": ResourceIdentifiers.ai_project,
    "AIProjectClient": ResourceIdentifiers.ai_project,
    "SearchIndexerClient": ResourceIdentifiers.search,
    "SearchIndexClient": ResourceIdentifiers.search,
    "SearchClient": ResourceIdentifiers.search,
    "AzureAppConfigurationClient": ResourceIdentifiers.config_store,
    "AzureAppConfigurationProvider": ResourceIdentifiers.config_store,
}
