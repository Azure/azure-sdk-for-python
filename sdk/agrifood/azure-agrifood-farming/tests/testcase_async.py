
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import random
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.agrifood.farming import FarmBeatsClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

class TestFarmBeats(AzureRecordedTestCase):

    def create_client(self, agrifood_endpoint):
        credential = self.get_credential(FarmBeatsClient)
        return self.create_client_from_credential(
            FarmBeatsClient,
            endpoint=agrifood_endpoint,
            credential=credential,
        )
