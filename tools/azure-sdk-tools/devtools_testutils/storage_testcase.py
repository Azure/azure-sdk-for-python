# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import logging
from time import sleep

# let this import fail, this package is used intentionally without the presence of azure-core
try:
    from azure.core.exceptions import ResourceExistsError
except:
    pass

try:
    # Note: these models are only available from v17.0.0 and higher, if you need them you'll also need azure-core 1.4.0 and higher
    from azure.mgmt.storage import StorageManagementClient
    from azure.mgmt.storage.models import (
        StorageAccount,
        Endpoints,
        LastAccessTimeTrackingPolicy,
        BlobServiceProperties,
        DeleteRetentionPolicy,
    )
except ImportError:
    pass

from azure_devtools.scenario_tests.exceptions import AzureTestError

from . import AzureMgmtPreparer, ResourceGroupPreparer, FakeResource
from .resource_testcase import RESOURCE_GROUP_PARAM


FakeStorageAccount = FakeResource


# Storage Account Preparer and its shorthand decorator
class StorageAccountPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix="",
        sku="Standard_LRS",
        location="westus",
        kind="StorageV2",
        parameter_name="storage_account",
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=False,
        use_cache=False,
    ):
        super(StorageAccountPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
            random_name_enabled=random_name_enabled,
        )
        self.location = location
        self.sku = sku
        self.kind = kind
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.storage_key = ""
        self.resource_moniker = self.name_prefix
        self.set_cache(use_cache, sku, location, name_prefix)
        if random_name_enabled:
            self.resource_moniker += "storname"

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(StorageManagementClient)
            group = self._get_resource_group(**kwargs)
            storage_async_operation = self._create_account(group.name, name)

            self.resource = storage_async_operation.result()
            storage_keys = {v.key_name: v.value for v in self.client.storage_accounts.list_keys(group.name, name).keys}
            self.storage_key = storage_keys["key1"]

            self.test_class_instance.scrubber.register_name_pair(name, self.resource_moniker)
        else:
            self.resource = StorageAccount(
                location=self.location,
            )
            self.resource.name = name
            self.resource.id = name
            self.resource.primary_endpoints = Endpoints()
            self.resource.primary_endpoints.blob = "https://{}.{}.core.windows.net".format(name, "blob")
            self.resource.primary_endpoints.queue = "https://{}.{}.core.windows.net".format(name, "queue")
            self.resource.primary_endpoints.table = "https://{}.{}.core.windows.net".format(name, "table")
            self.resource.primary_endpoints.file = "https://{}.{}.core.windows.net".format(name, "file")
            self.storage_key = "ZmFrZV9hY29jdW50X2tleQ=="
        return {
            self.parameter_name: self.resource,
            "{}_key".format(self.parameter_name): self.storage_key,
            "{}_cs".format(self.parameter_name): ";".join(
                [
                    "DefaultEndpointsProtocol=https",
                    "AccountName={}".format(name),
                    "AccountKey={}".format(self.storage_key),
                    "BlobEndpoint={}".format(self.resource.primary_endpoints.blob),
                    "TableEndpoint={}".format(self.resource.primary_endpoints.table),
                    "QueueEndpoint={}".format(self.resource.primary_endpoints.queue),
                    "FileEndpoint={}".format(self.resource.primary_endpoints.file),
                ]
            ),
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            retries = 3
            for _ in range(retries):
                try:
                    group = self._get_resource_group(**kwargs)
                    self.client.storage_accounts.delete(group.name, name)
                except ResourceExistsError as e:
                    # Occassionally a storage test will try to delete the
                    # resource before the previous operation has been completed
                    logger = logging.getLogger()
                    logger.warning(
                        "An error occurred while trying to delete storage account {}. Waiting \
                            ten seconds and retrying the delete.".format(
                            self.resource.name
                        )
                    )
                    sleep(30)

    def _create_account(self, resource_group_name, account_name):
        return self.client.storage_accounts.begin_create(
            resource_group_name,
            account_name,
            {
                "sku": {"name": self.sku},
                "location": self.location,
                "kind": self.kind,
                "enable_https_traffic_only": True,
            },
        )

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = (
                "To create a storage account a resource group is required. Please add "
                "decorator @{} in front of this storage account preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))


class BlobAccountPreparer(StorageAccountPreparer):
    def __init__(self, **kwargs):
        self.is_versioning_enabled = kwargs.pop("is_versioning_enabled", None)
        self.is_last_access_time_enabled = kwargs.pop("is_last_access_time_enabled", None)
        self.container_retention_days = kwargs.pop("container_retention_days", None)

        super(BlobAccountPreparer, self).__init__(**kwargs)

    def _create_account(self, resource_group_name, account_name):
        storage_async_operation = self.client.storage_accounts.begin_create(
            resource_group_name,
            account_name,
            {
                "sku": {"name": self.sku},
                "location": self.location,
                "kind": self.kind,
                "enable_https_traffic_only": True,
            },
        )

        props = BlobServiceProperties()
        if self.is_versioning_enabled is True:
            props.is_versioning_enabled = True
        if self.container_retention_days:
            props.container_delete_retention_policy = DeleteRetentionPolicy(
                enabled=True, days=self.container_retention_days
            )
        if self.is_last_access_time_enabled:
            props.last_access_time_tracking_policy = LastAccessTimeTrackingPolicy(enable=True)

        if not all(prop is None for prop in props.as_dict().values()):
            self.client.blob_services.set_service_properties(resource_group_name, account_name, props)

        sleep(30)

        return storage_async_operation


CachedStorageAccountPreparer = functools.partial(StorageAccountPreparer, use_cache=True, random_name_enabled=True)
