
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import random
import functools
from azure.identity import ClientSecretCredential
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.farmbeats import FarmBeatsClient
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class FarmBeatsTest(AzureTestCase):

    def create_client(self, farmbeats_endpoint):
        credential = ClientSecretCredential(
            tenant_id=os.environ["FARMBEATS_TENANT_ID"],
            client_id=os.environ["FARMBEATS_CLIENT_ID"],
            client_secret=os.environ["FARMBEATS_CLIENT_SECRET"],
            authority=os.environ["FARMBEATS_AUTHORITY"],
        )
        return self.create_client_from_credential(
            FarmBeatsClient,
            endpoint=farmbeats_endpoint,
            credential=credential,
        )

    def generate_random_name(self, name):

        if self.is_live:
            created_name = "{}-{}".format(name, random.randint(0, 1000))
            self.scrubber.register_name_pair(name, created_name)
            return created_name
        return name

FarmBeatsPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "farmbeats",
    farmbeats_endpoint="https://fakeAccount.farmbeats.azure.net",
    farmbeats_farmer_id="fake-farmer",
    farmbeats_boundary_id="fake-boundary",
    farmbeats_job_id_prefix="fake-job",
)