#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
from datetime import datetime, timedelta
from base64 import b64decode

from azure.mgmt.resource.resources import (
    ResourceManagementClient,
)
from azure.mgmt.resource.subscriptions import (
    SubscriptionClient,
)
from azure.mgmt.storage import (
    StorageManagementClient,
)
from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
)
from azure.mgmt.compute import (
    ComputeManagementClient,
)
from azure.mgmt.network import (
    NetworkManagementClient,
)

from azure.storage import AccessPolicy, CloudStorageAccount, SharedAccessPolicy
from azure.storage.blob import BlobService, BlobSharedAccessPermissions
from azure.storage.file import FileService
from azure.storage.queue import QueueService
from azure.storage.table import TableService

from . import storage_extensions

# Add some extensions to the service classes
# This functionality will eventually be part of the SDK
FileService.iterate_shares = storage_extensions.iterate_shares
BlobService.iterate_containers = storage_extensions.iterate_containers
BlobService.iterate_blobs = storage_extensions.iterate_blobs
QueueService.iterate_queues = storage_extensions.iterate_queues
TableService.iterate_tables = storage_extensions.iterate_tables


class AccountDetails(object):
    def __init__(self, subscriptions=None, tenants=None):
        self.subscriptions = subscriptions
        self.tenants = tenants

class SubscriptionDetails(object):
    def __init__(self, resource_groups=None, providers=None):
        self.resource_groups = resource_groups
        self.providers = providers

class ResourceGroupDetails(object):
    def __init__(self, storage_accounts=None, storage_accounts_locations=None,
                 vms=None, public_ip_addresses=None, virtual_networks=None):
        self.storage_accounts = storage_accounts
        self.storage_accounts_locations = storage_accounts_locations
        self.vms = vms
        self.public_ip_addresses = public_ip_addresses
        self.virtual_networks = virtual_networks

class StorageAccountDetails(object):
    def __init__(self, account_props=None, account_keys=None,
                 blob_containers=None, shares=None, tables=None, queues=None,
                 blob_service_properties=None, queue_service_properties=None,
                 table_service_properties=None):
        self.account_props = account_props
        self.account_keys = account_keys
        self.blob_containers = blob_containers
        self.shares = shares
        self.tables = tables
        self.queues = queues
        self.blob_service_properties = blob_service_properties
        self.queue_service_properties = queue_service_properties
        self.table_service_properties = table_service_properties

class StorageAccountContainerDetails(object):
    def __init__(self, container_name=None, sas_policy=None, blobs=None):
        self.container_name = container_name
        self.sas_policy = sas_policy
        self.blobs = blobs

class StorageAccountQueueDetails(object):
    def __init__(self, queue_name=None, metadata=None, messages=None):
        self.queue_name = queue_name
        self.metadata = metadata
        self.messages = messages

class StorageAccountTableDetails(object):
    def __init__(self, table_name=None, entities=None, custom_fields=None):
        self.table_name = table_name
        self.entities = entities
        self.custom_fields = custom_fields

class VMDetails(object):
    def __init__(self, name=None, vm=None):
        self.name = name
        self.vm = vm

class VirtualNetworkDetails(object):
    def __init__(self, name=None, network=None):
        self.name = name
        self.network = network


def get_account_details(creds):
    subscription_client = SubscriptionClient(creds)

    model = AccountDetails()
    model.subscriptions = list(subscription_client.subscriptions.list())
    model.tenants = list(subscription_client.tenants.list())
    return model

def get_subscription_details(subscription_id, creds):
    resource_client = ResourceManagementClient(creds, subscription_id)

    model = SubscriptionDetails()
    model.resource_groups = list(resource_client.resource_groups.list())
    model.providers = list(resource_client.providers.list())

    return model

def get_resource_group_details(subscription_id, creds, resource_group_name):
    storage_client = StorageManagementClient(creds, subscription_id)
    resource_client = ResourceManagementClient(creds, subscription_id)
    compute_client = ComputeManagementClient(creds, subscription_id)
    network_client = NetworkManagementClient(creds, subscription_id)

    model = ResourceGroupDetails()
    model.storage_accounts = list(storage_client.storage_accounts.list_by_resource_group(resource_group_name))
    provider = resource_client.providers.get('Microsoft.Storage')
    resource_type = [r for r in provider.resource_types if r.resource_type == 'storageAccounts'][0]
    model.storage_accounts_locations = resource_type.locations

    # TODO: make an iterate function
    model.vms = list(compute_client.virtual_machines.list(resource_group_name))
    model.public_ip_addresses = list(network_client.public_ip_addresses.list(resource_group_name))
    model.virtual_networks = list(network_client.virtual_networks.list(resource_group_name))

    return model

def get_vm_details(subscription_id, creds, resource_group_name, vm_name):
    compute_client = ComputeManagementClient(creds, subscription_id)

    model = VMDetails(
        name=vm_name,
        vm=compute_client.virtual_machines.get(resource_group_name, vm_name),
    )
    return model

def get_virtual_network_details(subscription_id, creds, resource_group_name, network_name):
    network_client = NetworkManagementClient(creds, subscription_id)

    model = VirtualNetworkDetails(
        name=network_name,
        network=network_client.virtual_networks.get(resource_group_name, network_name),
    )
    return model

def get_storage_account_details(subscription_id, creds, resource_group_name, account_name):
    storage_client = StorageManagementClient(creds, subscription_id)
    account_result = storage_client.storage_accounts.get_properties(
        resource_group_name,
        account_name,
    )
    storage_account_keys = storage_client.storage_accounts.list_keys(
        resource_group_name,
        account_name,
    )
    account_key = storage_account_keys.key1

    account = CloudStorageAccount(account_name, account_key)
    blob_service = account.create_blob_service()
    file_service = account.create_file_service()
    queue_service = account.create_queue_service()
    table_service = account.create_table_service()

    model = StorageAccountDetails()
    model.account_props = account_result
    model.account_keys = storage_account_keys
    model.blob_containers = blob_service.iterate_containers()
    model.queues = queue_service.iterate_queues()
    #TODO: find out why listing shares doesn't work
    #model.shares = file_service.iterate_shares()
    model.shares = []
    model.tables = table_service.iterate_tables()
    model.blob_service_properties = blob_service.get_blob_service_properties()
    model.queue_service_properties = queue_service.get_queue_service_properties()
    model.table_service_properties = table_service.get_table_service_properties()

    return model

def _get_storage_account_keys(subscription_id, creds, resource_group_name, account_name):
    storage_client = StorageManagementClient(creds, subscription_id)
    storage_account_keys = storage_client.storage_accounts.list_keys(
        resource_group_name,
        account_name,
    )
    return storage_account_keys

def get_container_details(subscription_id, creds, resource_group_name, account_name, container_name):
    keys = _get_storage_account_keys(subscription_id, creds, resource_group_name, account_name)
    blob_service = BlobService(account_name, keys.key1)

    model = StorageAccountContainerDetails()
    model.container_name = container_name
    model.sas_policy = _get_shared_access_policy(BlobSharedAccessPermissions.READ)
    model.blobs = []
    for blob in blob_service.iterate_blobs(container_name, include='metadata'):
        sas_token = blob_service.generate_shared_access_signature(container_name, blob.name, model.sas_policy)
        blob.sas_url = blob_service.make_blob_url(container_name, blob.name, sas_token=sas_token)
        raw_md5 = b64decode(blob.properties.content_md5)
        hex_md5 = ''.join([hex(val)[2:] for val in raw_md5])
        blob.properties.content_hex_md5 = hex_md5
        model.blobs.append(blob)

    return model

def _get_shared_access_policy(permission):
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    start = datetime.utcnow() - timedelta(minutes=1)
    expiry = start + timedelta(hours=1)
    return SharedAccessPolicy(
        AccessPolicy(
            start.strftime(date_format),
            expiry.strftime(date_format),
            permission,
        )
    )

def get_queue_details(subscription_id, creds, resource_group_name, account_name, queue_name):
    keys = _get_storage_account_keys(subscription_id, creds, resource_group_name, account_name)
    queue_service = QueueService(account_name, keys.key1)

    model = StorageAccountQueueDetails()
    model.queue_name = queue_name
    model.metadata = queue_service.get_queue_metadata(queue_name)
    count = int(model.metadata.get('x-ms-approximate-messages-count', '0'))
    model.messages = queue_service.peek_messages(queue_name, count) if count else []
    for msg in model.messages:
        try:
            msg.decoded_text = b64decode(msg.message_text).decode()
        except:
            msg.decoded_text = None

    return model

def get_table_details(subscription_id, creds, resource_group_name, account_name, table_name, next_partition_key=None, next_row_key=None):
    keys = _get_storage_account_keys(subscription_id, creds, resource_group_name, account_name)
    table_service = TableService(account_name, keys.key1)

    model = StorageAccountTableDetails()
    model.table_name = table_name
    model.entities = table_service.query_entities(
        table_name,
        top=3, # small to demonstrate continuations
        next_partition_key=next_partition_key,
        next_row_key=next_row_key,
    )
    model.custom_fields = _get_entities_custom_fields(model.entities)

    return model

def _get_entities_custom_fields(entities):
    '''Get the union of all custom fields in the specified entities.'''
    custom_fields = set()
    for entity in entities:
        fields = dir(entity)
        for field in fields:
            if not field.startswith('_'):
                custom_fields.add(field)
    for skip_field in ['PartitionKey', 'RowKey', 'Timestamp', 'etag']:
        custom_fields.discard(skip_field)
    return custom_fields

def unregister_provider(subscription_id, creds, provider_namespace):
    resource_client = ResourceManagementClient(creds, subscription_id)
    resource_client.providers.unregister(provider_namespace)

def register_provider(subscription_id, creds, provider_namespace):
    resource_client = ResourceManagementClient(creds, subscription_id)
    resource_client.providers.register(provider_namespace)

def create_storage_account(subscription_id, creds, resource_group_name, account_name, location, type):
    storage_client = StorageManagementClient(creds, subscription_id)
    result = storage_client.storage_accounts.create(
        resource_group_name,
        account_name,
        StorageAccountCreateParameters(
            location=location,
            account_type=type,
        ),
        raw=True
    )
    return result.response

def delete_storage_account(subscription_id, creds, resource_group_name, account_name):
    storage_client = StorageManagementClient(creds, subscription_id)
    result = storage_client.storage_accounts.delete(
        resource_group_name,
        account_name,
    )
    return result

def get_create_storage_account_status(subscription_id, creds, link):
    storage_client = StorageManagementClient(creds, subscription_id)
    request = storage_client._client.get(link)
    result = storage_client._client.send(request)
    return result
