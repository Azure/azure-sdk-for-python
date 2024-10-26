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

from typing import Dict, Tuple, Union, Type
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
except ImportError:
    AzureOpenAI = 'openai.AzureOpenAI'
    AsyncAzureOpenAI = 'openai.AsyncAzureOpenAI'


RESOURCE_SDK_MAP: Dict[str, Tuple[str, Union[str, Type]]] = case_insensitive_dict({
    'storage': ('storage', BlobServiceClient),
    'blobstorage': ('blob', BlobServiceClient),
    'blobcontainer': ('container', ContainerClient),
    'tablestorage': ('table', TableServiceClient),
    'keyvault': ('keyvault', None),
    'keyvaultsecrets': ('secrets', SecretClient),
    'keyvaultkeys': ('keys', KeyClient),
    'servicebus': ('service_bus', ServiceBusClient),
    'openai': ('openai', AzureOpenAI)
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
    'blobstorage': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'blobcontainer': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'tablestorage': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://storage.azure.com/.default",
    },
    'servicebus': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://servicebus.azure.net/.default",
    },
    'openai': {
        AzureClouds.AZURE_PUBLIC_CLOUD: "https://cognitiveservices.azure.com/.default",
    },
})
