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

from azure.mgmt.resource import (
    ProviderOperations,
    ResourceGroupListParameters,
    ResourceGroupOperations,
    ResourceManagementClient,
)
from azure.mgmt.storage import (
    StorageManagementClient,
    StorageAccountCreateParameters,
)

from azure.storage import AccessPolicy, CloudStorageAccount, SharedAccessPolicy
from azure.storage.blob import BlobService, BlobSharedAccessPermissions
from azure.storage.file import FileService
from azure.storage.queue import QueueService
from azure.storage.table import TableService

from . import storage_extensions
from . import mgmt_extensions

# Add some extensions to the service classes
# This functionality will eventually be part of the SDK
ResourceGroupOperations.iterate = mgmt_extensions.iterate_resource_groups
ProviderOperations.iterate = mgmt_extensions.iterate_providers
FileService.iterate_shares = storage_extensions.iterate_shares
BlobService.iterate_containers = storage_extensions.iterate_containers
BlobService.iterate_blobs = storage_extensions.iterate_blobs
QueueService.iterate_queues = storage_extensions.iterate_queues
TableService.iterate_tables = storage_extensions.iterate_tables


class AccountDetails(object):
    subscriptions = None
    tenants = None

class SubscriptionDetails(object):
    resource_groups = None
    providers = None

class ResourceGroupDetails(object):
    storage_accounts = None
    storage_accounts_locations = None

class StorageAccountDetails(object):
    account_props = None
    account_keys = None
    blob_containers = None
    shares = None
    tables = None
    queues = None
    blob_service_properties = None
    queue_service_properties = None
    table_service_properties = None

class StorageAccountContainerDetails(object):
    container_name = None
    sas_policy = None
    blobs = None

class StorageAccountQueueDetails(object):
    queue_name = None
    metadata = None
    messages = None

class StorageAccountTableDetails(object):
    table_name = None
    entities = None
    custom_fields = None


def get_account_details(auth_token):
    model = AccountDetails()
    model.subscriptions = mgmt_extensions.get_subscriptions(auth_token)
    model.tenants = mgmt_extensions.get_tenants(auth_token)
    return model

def get_subscription_details(creds):
    resource_client = ResourceManagementClient(creds)

    model = SubscriptionDetails()
    model.resource_groups = list(resource_client.resource_groups.iterate())
    model.providers = list(resource_client.providers.iterate())

    return model

def get_resource_group_details(creds, resource_group_name):
    storage_client = StorageManagementClient(creds)
    resource_client = ResourceManagementClient(creds)

    model = ResourceGroupDetails()
    model.storage_accounts = storage_client.storage_accounts.list_by_resource_group(resource_group_name).storage_accounts
    provider = resource_client.providers.get('Microsoft.Storage').provider
    resource_type = [r for r in provider.resource_types if r.name == 'storageAccounts'][0]
    model.storage_accounts_locations = resource_type.locations

    return model

def get_storage_account_details(creds, resource_group_name, account_name):
    storage_client = StorageManagementClient(creds)
    account_result = storage_client.storage_accounts.get_properties(
        resource_group_name,
        account_name,
    )
    keys_result = storage_client.storage_accounts.list_keys(
        resource_group_name,
        account_name,
    )
    account_key = keys_result.storage_account_keys.key1

    account = CloudStorageAccount(account_name, account_key)
    blob_service = account.create_blob_service()
    file_service = account.create_file_service()
    queue_service = account.create_queue_service()
    table_service = account.create_table_service()

    model = StorageAccountDetails()
    model.account_props = account_result.storage_account
    model.account_keys = keys_result.storage_account_keys
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

def _get_storage_account_keys(creds, resource_group_name, account_name):
    storage_client = StorageManagementClient(creds)
    keys_result = storage_client.storage_accounts.list_keys(
        resource_group_name,
        account_name,
    )
    return keys_result.storage_account_keys

def get_container_details(creds, resource_group_name, account_name, container_name):
    keys = _get_storage_account_keys(creds, resource_group_name, account_name)
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

def get_queue_details(creds, resource_group_name, account_name, queue_name):
    keys = _get_storage_account_keys(creds, resource_group_name, account_name)
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

def get_table_details(creds, resource_group_name, account_name, table_name, next_partition_key=None, next_row_key=None):
    keys = _get_storage_account_keys(creds, resource_group_name, account_name)
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

def unregister_provider(creds, provider_namespace):
    resource_client = ResourceManagementClient(creds)
    resource_client.providers.unregister(provider_namespace)

def register_provider(creds, provider_namespace):
    resource_client = ResourceManagementClient(creds)
    resource_client.providers.register(provider_namespace)

def create_storage_account(creds, resource_group_name, account_name, location, type):
    storage_client = StorageManagementClient(creds)
    result = storage_client.storage_accounts.begin_create(
        resource_group_name,
        account_name,
        StorageAccountCreateParameters(
            location=location,
            account_type=type,
        ),
    )
    return result

def delete_storage_account(creds, resource_group_name, account_name):
    storage_client = StorageManagementClient(creds)
    result = storage_client.storage_accounts.delete(
        resource_group_name,
        account_name,
    )
    return result

def get_create_storage_account_status(creds, link):
    storage_client = StorageManagementClient(creds)
    result = storage_client.get_create_operation_status(
        link,
    )
    return result
