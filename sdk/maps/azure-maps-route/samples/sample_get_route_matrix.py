# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_route_matrix.py
DESCRIPTION:
    This sample demonstrates how to perform get route matrix result with given request object.
USAGE:
    python sample_get_route_matrix.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")


def get_route_matrix():
    # [START get_route_matrix]
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.route import MapsRouteClient

    maps_route_client = MapsRouteClient(credential=AzureKeyCredential(subscription_key))

    request_obj = {
        "origins": {
            "type": "MultiPoint",
            "coordinates": [
                [
                    4.85106,
                    52.36006
                ],
                [
                    4.85056,
                    52.36187
                ]
            ]
        },
        "destinations": {
            "type": "MultiPoint",
            "coordinates": [
                [
                    4.85003,
                    52.36241
                ],
                [
                    13.42937,
                    52.50931
                ]
            ]
        }
    }

    result = maps_route_client.get_route_matrix(query=request_obj)

    print("Get Route Matrix with given request object:")
    print(result.summary)
    # [END get_route_matrix]

if __name__ == '__main__':
    get_route_matrix()