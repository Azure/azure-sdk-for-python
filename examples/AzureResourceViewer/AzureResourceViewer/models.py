import requests
from datetime import datetime, timedelta
from base64 import b64decode
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import (
    ResourceGroupListParameters,
    ResourceManagementClient,
)

from azure.storage import (
    BlobService,
    TableService,
    QueueService,
    BlobSharedAccessPermissions,
    AccessPolicy,
    SharedAccessPolicy,
)

# TODO: iteration helpers should be part of Azure SDK
from azure.mgmt.resource import (
    ProviderOperations,
    ResourceGroupOperations,
)

def iterate_generic(self, items_func):
    list_result = self.list(None)
    for obj in items_func(list_result):
        yield obj

    while list_result.next_link:
        list_result = self.list_next(
            list_result.next_link,
        )
        for obj in items_func(list_result):
            yield obj

def iterate_resource_groups(self):
    '''Iterate through all the resource groups.'''
    def get_items(result):
        return result.resource_groups
    return iterate_generic(self, get_items)

def iterate_providers(self):
    def get_items(result):
        return result.providers
    return iterate_generic(self, get_items)

ResourceGroupOperations.iterate = iterate_resource_groups

ProviderOperations.iterate = iterate_providers


# TODO: enumerating subscriptions should be part of Azure SDK

class Subscription(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

def get_subscriptions(auth_token):
    response = requests.get(
        'https://management.azure.com/subscriptions',
        params={'api-version': '2014-01-01'},
        headers={'authorization': 'Bearer {}'.format(auth_token)},
    )
    if response.ok:
        result = response.json()
        return [Subscription(item['subscriptionId'], item['displayName']) for item in result['value']]
    else:
        return []

def get_resource_groups(creds):
    resource_client = ResourceManagementClient(creds)
    return resource_client.resource_groups.iterate()

def get_providers(creds):
    resource_client = ResourceManagementClient(creds)
    return resource_client.providers.iterate()

def unregister_provider(creds, provider_namespace):
    resource_client = ResourceManagementClient(creds)
    resource_client.providers.unregister(provider_namespace)

def register_provider(creds, provider_namespace):
    resource_client = ResourceManagementClient(creds)
    resource_client.providers.register(provider_namespace)

def get_storage_accounts_for_resource_group(creds, resource_group_name):
    storage_client = StorageManagementClient(creds)
    account_result = storage_client.storage_accounts.list_by_resource_group(
        resource_group_name,
    )
    return account_result.storage_accounts

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
    containers = get_blob_containers(account_name, account_key)
    queues = get_queues(account_name, account_key)
    tables = get_tables(account_name, account_key)
    return account_result.storage_account, keys_result.storage_account_keys, containers, tables, queues

def get_storage_account_keys(creds, resource_group_name, account_name):
    storage_client = StorageManagementClient(creds)
    keys_result = storage_client.storage_accounts.list_keys(
        resource_group_name,
        account_name,
    )
    return keys_result.storage_account_keys

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

def get_blobs(account_name, account_key, container_name):
    blob_service = BlobService(account_name, account_key)
    blobs = []
    next_marker = None
    while True:
        results = blob_service.list_blobs(container_name, marker=next_marker, include='metadata')
        blobs.extend(results)
        next_marker = results.next_marker
        if not next_marker:
            break
    sas_policy = _get_shared_access_policy(BlobSharedAccessPermissions.READ)
    for blob in blobs:
        sas_token = blob_service.generate_shared_access_signature(container_name, blob.name, sas_policy)
        blob.sas_url = blob_service.make_blob_url(container_name, blob.name, sas_token=sas_token)
        raw_md5 = b64decode(blob.properties.content_md5)
        hex_md5 = ''.join([hex(val)[2:] for val in raw_md5])
        blob.properties.content_hex_md5 = hex_md5
    return blobs, sas_policy.access_policy.expiry

def get_blob_containers(account_name, account_key):
    blob_service = BlobService(account_name, account_key)
    containers = []
    next_marker = None
    while True:
        results = blob_service.list_containers(marker=next_marker)
        containers.extend(results)
        next_marker = results.next_marker
        if not next_marker:
            break
    return containers

def get_queues(account_name, account_key):
    queue_service = QueueService(account_name, account_key)
    queues = []
    next_marker = None
    while True:
        results = queue_service.list_queues(marker=next_marker)
        queues.extend(results)
        next_marker = results.next_marker
        if not next_marker:
            break
    return queues

def get_tables(account_name, account_key):
    table_service = TableService(account_name, account_key)
    tables = []
    next_marker = None
    while True:
        results = table_service.query_tables(next_table_name=next_marker)
        tables.extend(results)
        if hasattr(results, 'x_ms_continuation'):
            next_marker = results.x_ms_continuation.get('NextTableName')
        else:
            break
    return tables
