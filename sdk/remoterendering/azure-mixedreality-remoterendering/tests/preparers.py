
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import functools
from devtools_testutils import PowerShellPreparer, AzureMgmtPreparer
from azure.core.credentials import AzureKeyCredential

ENABLE_LOGGER = os.getenv('ENABLE_LOGGER', "False")

RemoteRenderingPreparer = functools.partial(
    PowerShellPreparer, 'remoterendering',
    remoterendering_arr_service_endpoint="https://remoterendering.eastus.mixedreality.azure.com",
    remoterendering_arr_account_domain="eastus.mixedreality.azure.com",
    remoterendering_arr_account_id="70a8e4d2-816a-4d03-a800-aeb20126ae51",
    remoterendering_arr_account_key="fakeZmFrZV9hY29jdW50X2tleQ==",
    remoterendering_arr_storage_account_name="arrstorageaccount",
    remoterendering_arr_blob_container_name="test",
    remoterendering_storage_endpoint_suffix="core.windows.net",
    remoterendering_arr_sas_token="sv=2015-04-05&sr=c&se=2122-03-10T16%3A13%3A40.0000000Z&sp=rwl&sig=fakeSig"
)


class RemoteRendererClientPreparer(AzureMgmtPreparer):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        super(RemoteRendererClientPreparer, self).__init__(
            name_prefix='',
            random_name_length=42,
        )
        self.client_kwargs = client_kwargs
        self.client_cls = client_cls

    def create_resource(self, name, **kwargs):
        polling_interval = 5
        if self.is_live:
            remoterendering_arr_service_endpoint = os.environ["REMOTERENDERING_ARR_SERVICE_ENDPOINT"]
            remoterendering_arr_account_id = os.environ["REMOTERENDERING_ARR_ACCOUNT_ID"]
            remoterendering_arr_account_domain = os.environ["REMOTERENDERING_ARR_ACCOUNT_DOMAIN"]
            remoterendering_arr_account_key = os.environ["REMOTERENDERING_ARR_ACCOUNT_KEY"]
        else:
            remoterendering_arr_service_endpoint = "https://remoterendering.eastus.mixedreality.azure.com"
            remoterendering_arr_account_id = "70a8e4d2-816a-4d03-a800-aeb20126ae51"
            remoterendering_arr_account_domain = "eastus.mixedreality.azure.com"
            remoterendering_arr_account_key = "ZmFrZV9hY2NvdW50X2tleQ=="  # this is a fake key BASE64 fake_account_key
            polling_interval = 0

        key_credential = AzureKeyCredential(remoterendering_arr_account_key)
        client = self.client_cls(
            endpoint=remoterendering_arr_service_endpoint,
            account_id=remoterendering_arr_account_id,
            account_domain=remoterendering_arr_account_domain,
            credential=key_credential, polling_interval=polling_interval)

        kwargs.update({"client": client})
        return kwargs
