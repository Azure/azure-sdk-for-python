
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import random
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import Boundary, Polygon
from azure.core.exceptions import HttpResponseError

class FarmBeatsTest(AzureTestCase):

    def create_client(self, farmbeats_endpoint):
        credential = self.get_credential(FarmBeatsClient)
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

    def create_boundary_if_not_exist(self, client, farmbeats_farmer_id, farmbeats_boundary_id):
        try:
            return client.boundaries.get(farmer_id=farmbeats_farmer_id, boundary_id=farmbeats_boundary_id)
        except HttpResponseError:
            return client.boundaries.create_or_update(
                farmer_id=farmbeats_farmer_id,
                boundary_id=farmbeats_boundary_id,
                body=Boundary(
                    description="Created by SDK",
                    geometry=Polygon(
                        coordinates=[
                            [
                                [73.70457172393799, 20.545385304358106],
                                [73.70457172393799, 20.545385304358106],
                                [73.70448589324951, 20.542411534243367],
                                [73.70877742767334, 20.541688176010233],
                                [73.71023654937744, 20.545083911372505],
                                [73.70663166046143, 20.546992723579137],
                                [73.70457172393799, 20.545385304358106],
                            ]
                        ]
                    )
                )
            )

    def delete_boundary(self, client, farmbeats_farmer_id, farmbeats_boundary_id):
        client.boundaries.delete(farmer_id=farmbeats_farmer_id, boundary_id=farmbeats_boundary_id)

FarmBeatsPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "farmbeats",
    farmbeats_endpoint="https://fakeAccount.farmbeats.azure.net",
    farmbeats_farmer_id="fake-farmer",
    farmbeats_boundary_id="fake-boundary",
    farmbeats_job_id_prefix="fake-job",
)