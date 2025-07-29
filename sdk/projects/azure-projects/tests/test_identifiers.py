import pytest

from azure.projects.resources import ResourceIdentifiers
from azure.projects.resources._extension.roles import RoleAssignment
from azure.projects.resources.ai._resource import CognitiveServicesAccount, AIServices
from azure.projects.resources.ai.deployment import AIDeployment, AIChat, AIEmbeddings
from azure.projects.resources.appconfig import ConfigStore
from azure.projects.resources.appconfig.setting import ConfigSetting
from azure.projects.resources.foundry._resource import MLWorkspace, AIHub, AIProject
from azure.projects.resources.foundry._connection import AIConnection
from azure.projects.resources.keyvault import KeyVault
from azure.projects.resources.managedidentity import UserAssignedIdentity
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects.resources.search import SearchService
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.storage.blobs import BlobStorage
from azure.projects.resources.storage.blobs.container import BlobContainer
from azure.projects.resources.storage.tables import TableStorage
from azure.projects.resources.storage.tables.table import Table


def test_identifiers():
    with pytest.raises(TypeError):
        ResourceIdentifiers.resource()
    assert ResourceIdentifiers.resource_group.resource() is ResourceGroup
    assert ResourceIdentifiers.user_assigned_identity.resource() is UserAssignedIdentity
    assert ResourceIdentifiers.role_assignment.resource() is RoleAssignment
    assert ResourceIdentifiers.storage_account.resource() is StorageAccount
    assert ResourceIdentifiers.blob_storage.resource() is BlobStorage
    with pytest.raises(NotImplementedError):
        assert ResourceIdentifiers.datalake_storage.resource()
    assert ResourceIdentifiers.blob_container.resource() is BlobContainer
    with pytest.raises(NotImplementedError):
        assert ResourceIdentifiers.file_system.resource()
    assert ResourceIdentifiers.table_storage.resource() is TableStorage
    assert ResourceIdentifiers.table.resource() is Table
    with pytest.raises(NotImplementedError):
        assert ResourceIdentifiers.queue_storage.resource()
    with pytest.raises(NotImplementedError):
        assert ResourceIdentifiers.queue.resource()
    with pytest.raises(NotImplementedError):
        assert ResourceIdentifiers.file_storage.resource()
    with pytest.raises(NotImplementedError):
        assert ResourceIdentifiers.file_share.resource()
    with pytest.raises(NotImplementedError):
        assert ResourceIdentifiers.system_topic.resource()
    with pytest.raises(NotImplementedError):
        assert ResourceIdentifiers.system_topic_subscription.resource()
    assert ResourceIdentifiers.keyvault.resource() is KeyVault
    with pytest.raises(NotImplementedError):
        assert ResourceIdentifiers.keyvault_key.resource()
    with pytest.raises(NotImplementedError):
        assert ResourceIdentifiers.keyvault_secret.resource()
    assert ResourceIdentifiers.search.resource() is SearchService
    assert ResourceIdentifiers.cognitive_services.resource() is CognitiveServicesAccount
    assert ResourceIdentifiers.ml_workspace.resource() is MLWorkspace
    assert ResourceIdentifiers.ai_services.resource() is AIServices
    assert ResourceIdentifiers.ai_project.resource() is AIProject
    assert ResourceIdentifiers.ai_hub.resource() is AIHub
    assert ResourceIdentifiers.ai_deployment.resource() is AIDeployment
    assert ResourceIdentifiers.ai_chat_deployment.resource() is AIChat
    assert ResourceIdentifiers.ai_embeddings_deployment.resource() is AIEmbeddings
    assert ResourceIdentifiers.ai_connection.resource() is AIConnection
    assert ResourceIdentifiers.config_store.resource() is ConfigStore
    assert ResourceIdentifiers.config_setting.resource() is ConfigSetting
