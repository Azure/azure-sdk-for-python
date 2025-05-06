import os

from azure.projects import export, provision, Parameter
from azure.projects._provision import _get_resource_defaults
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects.resources.managedidentity import UserAssignedIdentity
from azure.projects.resources.ai import AIServices
from azure.projects.resources.ai.deployment import AIDeployment, AIChat, AIEmbeddings


def test_provision_load_resource_defaults():
    parameters = {}
    output = _get_resource_defaults("notafile.yaml", "foo", parameters=parameters)
    assert parameters == {}
    assert output == {}
    resource_file = os.path.join(os.path.dirname(__file__), "test_resources.yaml")
    output = _get_resource_defaults(resource_file, "foo", parameters=parameters)
    output.pop("TestDeployment")
    assert parameters == {
        'location': Parameter("location"),
        'tagPrefix': Parameter("tagPrefix"),
        'sasPolicy': Parameter("sasPolicy"),
        'ENDPOINTS': Parameter("ENDPOINTS"),
        'environmentName': Parameter("environmentName"),
    }
    assert output == {
        'Microsoft.Storage/storageAccounts': {
            'kind': 'StorageV2',
            'location': Parameter("location"),
            'sku': {'name': 'Standard_LRS'},
            'properties': {
                'accessTier': 'Premium',
                'isHnsEnabled': True,
                'routingPreference': {
                    'publishInternetEndpoints': Parameter("ENDPOINTS"),
                    'routingChoice': 'MicrosoftRouting'
                },
                'sasPolicy': Parameter("sasPolicy"),
            },
            'tags': {'foo': '${tagPrefix}/one', 'bar': '${environmentName}/two'}
        }
    }
    parameters = {}
    output = _get_resource_defaults(resource_file, "TestDeployment", parameters=parameters)
    output.pop("TestDeployment")
    assert parameters == {
        'location': Parameter("location"),
        'tagPrefix': Parameter("tagPrefix"),
        'sasPolicy': Parameter("sasPolicy"),
        'ENDPOINTS': Parameter("ENDPOINTS"),
        'environmentName': Parameter("environmentName"),
    }
    assert output == {
        'Microsoft.Storage/storageAccounts': {
            'kind': 'StorageV2',
            'location': 'westus2',
            'sku': {'name': 'Standard_LRS'},
            'properties': {
                'accessTier': 'Hot',
                'allowedCopyScope': 'AAD',
                'isHnsEnabled': True,
                'routingPreference': {
                    'publishInternetEndpoints': False,
                },
                'sasPolicy': Parameter("sasPolicy"),
            },
            'tags': {'foo': '${tagPrefix}/one', 'bar': '${environmentName}/two', 'baz': 'three'}
        }
    }
