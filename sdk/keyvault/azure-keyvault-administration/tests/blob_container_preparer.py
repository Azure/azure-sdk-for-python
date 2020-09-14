# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime, timedelta

from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions
from devtools_testutils import AzureMgmtPreparer


class BlobContainerPreparer(AzureMgmtPreparer):
    def __init__(self, **kwargs):
        super(BlobContainerPreparer, self).__init__("container", 24, random_name_enabled=True, **kwargs)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            storage_account = kwargs.pop("storage_account")
            storage_account_key = kwargs.pop("storage_account_key")
            sas_token = generate_account_sas(
                account_name=storage_account.name,
                account_key=storage_account_key,
                resource_types=ResourceTypes(container=True, object=True),
                permission=AccountSasPermissions(
                    create=True, list=True, write=True, read=True, add=True, delete=True, delete_previous_version=True
                ),
                expiry=datetime.utcnow() + timedelta(minutes=5),
            )
            blob_client = BlobServiceClient(storage_account.primary_endpoints.blob, sas_token)
            container = blob_client.create_container(name)
            container_uri = storage_account.primary_endpoints.blob + container.container_name
            self.test_class_instance.scrubber.register_name_pair(sas_token, "redacted")
            self.test_class_instance.scrubber.register_name_pair(container_uri, "https://storage/container")
        else:
            sas_token = "fake-sas"
            container_uri = "https://storage/container"
        return {"container_uri": container_uri, "sas_token": sas_token}
