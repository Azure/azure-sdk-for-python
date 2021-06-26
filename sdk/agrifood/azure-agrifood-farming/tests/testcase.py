
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
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

class FarmBeatsTest(AzureTestCase):

    def create_client(self, agrifood_endpoint):
        credential = self.get_credential(FarmBeatsClient)
        return self.create_client_from_credential(
            FarmBeatsClient,
            endpoint=agrifood_endpoint,
            credential=credential,
        )

    def generate_random_name(self, name):

        if self.is_live:
            created_name = "{}-{}".format(name, random.randint(0, 100000))
            self.scrubber.register_name_pair(created_name, name)
            return created_name
        return name

    def create_boundary_if_not_exist(self, client, farmer_id, boundary_id):
        try:
            return client.boundaries.get(farmer_id=farmer_id, boundary_id=boundary_id)
        except HttpResponseError:
            return self.create_boundary(client=client, farmer_id=farmer_id, boundary_id=boundary_id)

    def create_boundary(self, client, farmer_id, boundary_id):
        try:
            return client.boundaries.create_or_update(
                farmer_id=farmer_id,
                boundary_id=boundary_id,
                boundary=Boundary(
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
        except Exception as e:
            print("!!! Unhandlable error in boundary creation")
            print(e)
            print(dir(e))
            print(e.response.body())
            print(e.status_code)

    def delete_boundary(self, client, farmer_id, boundary_id):
        client.boundaries.delete(farmer_id=farmer_id, boundary_id=boundary_id)

FarmBeatsPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "agrifood",
    agrifood_endpoint="https://fakeAccount.farmbeats.azure.net"
)
