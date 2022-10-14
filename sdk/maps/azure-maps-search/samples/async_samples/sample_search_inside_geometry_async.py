# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_search_inside_geometry_async.py
DESCRIPTION:
    This sample demonstrates how to perform search inside geometry by given target such as `pizza` and multiple different geometry as input, which include GeoJson object and geo_interface property from other existing packages such as shapely.
USAGE:
    python sample_search_inside_geometry_async.py

    Set the environment variables with your own values before running the sample:
    - AZURE_SUBSCRIPTION_KEY - your subscription key
"""
import asyncio
import os

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")


async def search_inside_geometry():
    from azure.core.credentials import AzureKeyCredential
    from azure.maps.search import MapsSearchClient

    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))


    geo_json_obj1 = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-122.143035,47.653536],
                        [-122.187164,47.617556],
                        [-122.114981,47.570599],
                        [-122.132756,47.654009],
                        [-122.143035,47.653536]
                        ]]
                },
                "properties": {}
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-122.126986,47.639754]
                },
                "properties": {
                    "subType": "Circle",
                    "radius": 100
                }
            }
        ]
    }

    geo_json_obj2= {
        'type': 'Polygon',
        'coordinates': [
            [[-122.43576049804686, 37.7524152343544],
             [-122.43301391601562, 37.70660472542312],
             [-122.36434936523438, 37.712059855877314],
             [-122.43576049804686, 37.7524152343544]]
        ]
    }

    # This is the mock results we can get from 3rd party package `Shapely`
    #
    # from shapely.geometry import Polygon
    #
    # data = Polygon([
    #     [-122.43576049804686, 37.7524152343544],
    #     [-122.43301391601562, 37.70660472542312],
    #     [-122.36434936523438, 37.712059855877314],
    #     [-122.43576049804686, 37.7524152343544]
    # ]).__geo_interface__
    #
    geo_obj_interface = {
        'type': 'Polygon',
        'coordinates': ((
            (-122.43576049804686, 37.7524152343544),
            (-122.43301391601562, 37.70660472542312),
            (-122.36434936523438, 37.712059855877314),
            (-122.43576049804686, 37.7524152343544)),
        )
    }

    result1 = maps_search_client.search_inside_geometry(
        query="pizza",
        geometry=geo_json_obj1
    )
    print("Search inside geometry with standard GeoJson obejct as input, FeatureCollection:")
    print(result1.__dict__)

    print("Result 2 and result 3 should be the same: ")
    print("__________________________________________")
    result2 = maps_search_client.search_inside_geometry(
        query="pizza",
        geometry=geo_json_obj2
    )
    print("Search inside geometry with standard GeoJson object as input, Polygon as result 2:")
    print(result2.__dict__)
    print(f'Id of the first result item of result 2: {result2.results[0].id}')

    result3 = maps_search_client.search_inside_geometry(
        query="pizza",
        geometry=geo_obj_interface
    )
    print("Search inside geometry with Polygon from third party library `shapely` with geo_interface as result 3:")
    print(result2.__dict__)
    print(f'Id of the first result item of result 3: {result3.results[0].id}')


if __name__ == '__main__':
    asyncio.run(search_inside_geometry())