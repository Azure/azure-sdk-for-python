from unittest import mock

from azure.projects import export, provision, Parameter
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects.resources.managedidentity import UserAssignedIdentity
from azure.projects.resources.ai import AIServices
from azure.projects.resources.ai.deployment import AIDeployment, AIChat, AIEmbeddings
