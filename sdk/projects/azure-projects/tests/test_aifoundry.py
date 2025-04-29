from dataclasses import dataclass
from uuid import uuid4

import pytest
from azure.projects.resources.ai import AIServices
from azure.projects.resources.search import SearchService
from azure.projects.resources.foundry import AIHub, AIProject
from azure.projects.resources.storage.blobs import BlobStorage
from azure.projects.resources.keyvault import KeyVault
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, field, AzureInfrastructure, export, AzureApp

TEST_SUB = str(uuid4())
RG = ResourceSymbol("resourcegroup")
IDENTITY = {"type": "UserAssigned", "userAssignedIdentities": {GLOBAL_PARAMS["managedIdentityId"]: {}}}


def test_aifoundry_export(export_dir):
    class test(AzureInfrastructure):
        r: AIHub = AIHub()

    with pytest.raises(ValueError):
        export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])

    class test(AzureInfrastructure):
        ai: AIServices = AIServices()
        search: SearchService = SearchService()
        storage: BlobStorage = BlobStorage()
        vault: KeyVault = KeyVault()
        hub: AIHub = AIHub()
        project: AIProject = AIProject()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])
