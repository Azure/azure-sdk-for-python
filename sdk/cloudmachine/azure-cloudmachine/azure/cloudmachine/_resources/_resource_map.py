# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------

from typing import Dict, Tuple, Union, Type, List, Any
from azure.core.utils import case_insensitive_dict
from azure.core import AzureClouds

try:
    from azure.storage.blob import BlobServiceClient, ContainerClient
    from azure.storage.blob.aio import (
        BlobServiceClient as AsyncBlobServiceClient,
        ContainerClient as AsyncContainerClient
    )
except ImportError:
    BlobServiceClient = 'azure.storage.blob.BlobServiceClient'
    AsyncBlobServiceClient = 'azure.storage.blob.aio.BlobServiceClient'
    ContainerClient = 'azure.storage.blob.ContainerClient'
    AsyncContainerClient = 'azure.storage.blob.aio.ContainerClient'

try:
    from azure.data.tables import TableServiceClient
    from azure.data.tables.aio import TableServiceClient as AsyncTableServiceClient
except ImportError:
    TableServiceClient = 'azure.data.tables.TableServiceClient'
    AsyncTableServiceClient = 'azure.data.tables.aio.TableServiceClient'

try:
    from azure.servicebus import ServiceBusClient
    from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient
except ImportError:
    ServiceBusClient = 'azure.servicebus.ServiceBusClient'
    AsyncServiceBusClient = 'azure.servicebus.aio.ServiceBusClient'

try:
    from azure.keyvault.keys import KeyClient
    from azure.keyvault.keys.aio import KeyClient as AsyncKeyClient
except ImportError:
    KeyClient = 'azure.keyvault.keys.KeyClient'
    AsyncKeyClient = 'azure.keyvault.keys.aio.KeyClient'

try:
    from azure.keyvault.secrets import SecretClient
    from azure.keyvault.secrets.aio import SecretClient as AsyncSecretClient
except ImportError:
    SecretClient = 'azure.keyvault.secrets.SecretClient'
    AsyncSecretClient = 'azure.keyvault.secrets.aio.SecretClient'

try:
    from openai import AzureOpenAI, AsyncAzureOpenAI
    from openai.resources import Embeddings, Chat
except ImportError:
    AzureOpenAI = Any
    AsyncAzureOpenAI = Any

try:
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient
except ImportError:
    SearchClient = Any
    SearchIndexClient = Any

try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
except ImportError:
    DocumentIntelligenceClient = Any


RESOURCE_SDK_MAP: Dict[List[str], Tuple[str, Union[str, Type]]] = case_insensitive_dict({
    'storage': (['storage', 'blob'], BlobServiceClient),
    'storage:blob': (['storage', 'blob'], BlobServiceClient),
    'storage:blob:container': (['storage', 'blob', 'container'], ContainerClient),
    'storage:table': (['table'], TableServiceClient),
    'keyvault': (['keyvault'], None),
    'keyvault:secrets': (['secrets'], SecretClient),
    'keyvault:keys': (['keys'], KeyClient),
    'servicebus': (['service_bus'], ServiceBusClient),
    'openai': (['openai', 'open_ai'], AzureOpenAI),
    'search': (['search'], SearchIndexClient),
    'search:index': (['search', 'search_index'], SearchClient),
    'documentai': (['document_intelligence', 'form_recognizer'], DocumentIntelligenceClient),
})

RESOURCE_SDK_ASYNC_MAP: Dict[str, Tuple[str, str]] = case_insensitive_dict({
    'storage': ('storage', AsyncBlobServiceClient),
    'blobstorage': ('blob', AsyncBlobServiceClient),
    'blobcontainer': ('container', AsyncContainerClient),
    'tablestorage': ('table', AsyncTableServiceClient),
    'keyvault': ('keyvault', None),
    'keyvaultsecrets': ('secrets', AsyncSecretClient),
    'keyvaultkeys': ('keys', AsyncKeyClient),
    'servicebus': ('service_bus', AsyncServiceBusClient),
    'openai': ('openai', AsyncAzureOpenAI)
})

AUDIENCES: Dict[str, Dict[AzureClouds, str]] = case_insensitive_dict({
    'storage': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'storage:blob': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'storage:blob:container': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'storage:table': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'servicebus': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://servicebus.azure.net/.default",
    },
    'openai': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://cognitiveservices.azure.com/.default",
    },
    'search': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://search.azure.com/.default",
    },
    'search:index': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://search.azure.com/.default",
    },
    'documentai': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://cognitiveservices.azure.com/.default",
    }
})

RESOURCE_IDS: Dict[str, str] = case_insensitive_dict({
    'storage': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{name}',
    'storage:blob': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{name}',
    'storage:table': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{name}',
    'servicebus': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.ServiceBus/namespaces/{name}',
    'openai': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CognitiveServices/accounts/{name}',
    'search': '"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Search/searchServices/{name}',
    'documentai': '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.CognitiveServices/accounts/{name}'
})

DEFAULT_API_VERSIONS = {
    "storage:table": "2019-02-02",
    "storage:blob": "2020-12-06", # "2025-01-05"
    "storage": "2020-12-06",
    "servicebus": "2021-05",
    "openai": "2023-05-15"
}

