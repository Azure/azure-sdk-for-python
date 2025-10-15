# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: planetarycomputer_stac_specification.py

DESCRIPTION:
    This sample demonstrates STAC API conformance, catalog operations, and item management:
    - Checking API conformance
    - Getting the landing page
    - Searching collections
    - Searching and querying items with filters, bounding boxes, temporal ranges
    - Working with queryables
    - Creating, updating, and deleting STAC items

USAGE:
    python planetarycomputer_stac_specification.py

    Set the environment variable AZURE_PLANETARY_COMPUTER_ENDPOINT with your endpoint URL.
    Set the environment variable AZURE_COLLECTION_ID with your collection ID (default: sentinel-2-l2a).
"""

import os
import json
import time
from azure.planetarycomputer import PlanetaryComputerClient
from azure.identity import DefaultAzureCredential
from azure.planetarycomputer.models import (
    StacSearchParameters,
    FilterLanguage,
    StacSearchSortingDirection,
    StacSortExtension,
    StacItem,
)

import logging
from azure.core.pipeline.policies import HttpLoggingPolicy

# Enable HTTP request/response logging
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO)


def get_landing_page(client):
    """Get the STAC landing page."""
    landing_page = client.stac.get_stac_landing_page()

    for link in landing_page.links[:5]:  # Show first 5 links
        logging.info(f"  - {link.rel}: {link.href}")


def search_collections(client):
    """Search and list STAC collections."""
    collections = client.stac.list_collections()

    # Show first few collections
    for collection in collections.collections[:3]:
        if collection.description:
            desc = collection.description[:100] + "..." if len(collection.description) > 100 else collection.description
            logging.info(f"  - {collection.id}: {desc}")


def search_items(client, collection_id):
    """Search STAC items with filters and sorting."""
    # Create Search using StacSearchParameters
    search_post_request = StacSearchParameters(
        collections=[collection_id],
        bounding_box=[-9.5, 36.0, 3.3, 43.8],
        date_time="2023-01-01T00:00:00Z/2023-12-31T23:59:59Z",
        filter_lang=FilterLanguage.CQL2_JSON,
        filter={"op": "<=", "args": [{"property": "eo:cloud_cover"}, 10]},
        limit=1,
        sort_by=[StacSortExtension(direction=StacSearchSortingDirection.ASC, field="eo:cloud_cover")],
    )

    # Create Search
    search_post_response = client.stac.search(body=search_post_request)
    logging.info(json.dumps(search_post_response.as_dict(), indent=2))

def get_sample_stac_item(collection_id: str, item_id: str) -> StacItem:
    return StacItem(
    {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": item_id,
        "collection": collection_id,
        "properties": {
            "created": "2023-10-05T11:21:59.792759Z",
            "providers": [
                {
                    "name": "ESA",
                    "roles": ["producer", "processor", "licensor"],
                    "url": "https://earth.esa.int/web/guest/home",
                }
            ],
            "platform": "sentinel-2a",
            "constellation": "sentinel-2",
            "instruments": ["msi"],
            "eo:cloud_cover": 0.0025,
            "sat:orbit_state": "descending",
            "sat:relative_orbit": 94,
            "proj:epsg": 32630,
            "proj:centroid": {"lat": 40.09169, "lon": -4.29998},
            "mgrs:utm_zone": 30,
            "mgrs:latitude_band": "T",
            "mgrs:grid_square": "UK",
            "view:sun_azimuth": 143.685102918987,
            "view:sun_elevation": 59.1339844077876,
            "s2:product_uri": "S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE",
            "s2:generation_time": "2023-08-16T17:16:02.000000Z",
            "s2:processing_baseline": "5.09",
            "s2:product_type": "S2MSI2A",
            "s2:datatake_id": "GS2A_20230816T105631_042562_N05.09",
            "s2:datatake_type": "INS-NOBS",
            "s2:datastrip_id": "S2A_OPER_MSI_L2A_DS_2APS_20230816T171602_S20230816T110544_N05.09",
            "s2:granule_id": "S2A_OPER_MSI_L2A_TL_2APS_20230816T171602_A042562_T30TUK_N05.09",
            "s2:mgrs_tile": "30TUK",
            "s2:reflectance_conversion_factor": 0.974056617778896,
            "s2:degraded_msi_data_percentage": 0.0314,
            "s2:nodata_pixel_percentage": 63.907039,
            "s2:saturated_defective_pixel_percentage": 0.0,
            "s2:dark_features_percentage": 0.0132,
            "s2:cloud_shadow_percentage": 0.0,
            "s2:vegetation_percentage": 11.828032,
            "s2:not_vegetated_percentage": 87.793595,
            "s2:water_percentage": 0.306992,
            "s2:unclassified_percentage": 0.055679,
            "s2:medium_proba_clouds_percentage": 0.000754,
            "s2:high_proba_clouds_percentage": 0.000129,
            "s2:thin_cirrus_percentage": 0.001618,
            "s2:snow_ice_percentage": 0.0,
            "datetime": "2023-08-16T10:56:31.024Z",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [-4.673798, 39.647784],
                    [-4.051453, 39.656847],
                    [-4.066803, 40.645928],
                    [-4.372314, 40.641388],
                    [-4.411957, 40.514249],
                    [-4.457062, 40.367156],
                    [-4.502228, 40.220191],
                    [-4.54715, 40.073268],
                    [-4.5914, 39.926187],
                    [-4.635101, 39.77895],
                    [-4.673798, 39.647784],
                ]
            ],
        },
        "links": [
            {
                "rel": "license",
                "href": "https://sentinel.esa.int/documents/247904/690755/Sentinel_Data_Legal_Notice",
            },
            {
                "rel": "self",
                "href": "./S2A_MSIL2A_20230816T105631_R094_T30TUK_20230816T171602.xml",
                "type": "application/json",
            },
            {"rel": "parent", "href": "../sentinel2.json", "type": "application/json"},
            {"rel": "root", "href": "../sentinel2.json", "type": "application/json"},
            {
                "rel": "collection",
                "href": "../sentinel2.json",
                "type": "application/json",
            },
        ],
        "assets": {
            "blue": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R10m/T30TUK_20230816T105631_B02_10m.jp2",
                "type": "image/jp2",
                "title": "Blue (band 2) - 10m",
                "view:azimuth": 103.214484410443,
                "view:incidence_angle": 10.1629755066291,
                "eo:bands": [
                    {
                        "center_wavelength": 0.49,
                        "common_name": "blue",
                        "description": "Blue (band 2)",
                        "full_width_half_max": 0.098,
                        "name": "blue",
                    }
                ],
                "gsd": 10,
                "proj:shape": [10980, 10980],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [10.0, 0.0, 300000.0, 0.0, -10.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 10,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "green": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R10m/T30TUK_20230816T105631_B03_10m.jp2",
                "type": "image/jp2",
                "title": "Green (band 3) - 10m",
                "view:azimuth": 103.488678247608,
                "view:incidence_angle": 10.1808964701359,
                "eo:bands": [
                    {
                        "center_wavelength": 0.56,
                        "common_name": "green",
                        "description": "Green (band 3)",
                        "full_width_half_max": 0.045,
                        "name": "green",
                    }
                ],
                "gsd": 10,
                "proj:shape": [10980, 10980],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [10.0, 0.0, 300000.0, 0.0, -10.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 10,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "red": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R10m/T30TUK_20230816T105631_B04_10m.jp2",
                "type": "image/jp2",
                "title": "Red (band 4) - 10m",
                "view:azimuth": 103.736028079286,
                "view:incidence_angle": 10.204345016995,
                "eo:bands": [
                    {
                        "center_wavelength": 0.665,
                        "common_name": "red",
                        "description": "Red (band 4)",
                        "full_width_half_max": 0.038,
                        "name": "red",
                    }
                ],
                "gsd": 10,
                "proj:shape": [10980, 10980],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [10.0, 0.0, 300000.0, 0.0, -10.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 10,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "nir": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R10m/T30TUK_20230816T105631_B08_10m.jp2",
                "type": "image/jp2",
                "title": "NIR 1 (band 8) - 10m",
                "view:azimuth": 103.351825854992,
                "view:incidence_angle": 10.170938895596,
                "eo:bands": [
                    {
                        "center_wavelength": 0.842,
                        "common_name": "nir",
                        "description": "NIR 1 (band 8)",
                        "full_width_half_max": 0.145,
                        "name": "nir",
                    }
                ],
                "gsd": 10,
                "proj:shape": [10980, 10980],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [10.0, 0.0, 300000.0, 0.0, -10.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 10,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "visual": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R10m/T30TUK_20230816T105631_TCI_10m.jp2",
                "type": "image/jp2",
                "title": "True color image",
                "eo:bands": [
                    {
                        "center_wavelength": 0.665,
                        "common_name": "red",
                        "description": "Red (band 4)",
                        "full_width_half_max": 0.038,
                        "name": "red",
                    },
                    {
                        "center_wavelength": 0.56,
                        "common_name": "green",
                        "description": "Green (band 3)",
                        "full_width_half_max": 0.045,
                        "name": "green",
                    },
                    {
                        "center_wavelength": 0.49,
                        "common_name": "blue",
                        "description": "Blue (band 2)",
                        "full_width_half_max": 0.098,
                        "name": "blue",
                    },
                ],
                "gsd": 10,
                "proj:shape": [10980, 10980],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [10.0, 0.0, 300000.0, 0.0, -10.0, 4500000.0],
                "roles": ["visual"],
            },
            "aot_10m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R10m/T30TUK_20230816T105631_AOT_10m.jp2",
                "type": "image/jp2",
                "title": "Aerosol optical thickness (AOT)",
                "gsd": 10,
                "proj:shape": [10980, 10980],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [10.0, 0.0, 300000.0, 0.0, -10.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 10,
                        "scale": 0.001,
                        "offset": 0,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "wvp_10m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R10m/T30TUK_20230816T105631_WVP_10m.jp2",
                "type": "image/jp2",
                "title": "Water vapour (WVP)",
                "gsd": 10,
                "proj:shape": [10980, 10980],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [10.0, 0.0, 300000.0, 0.0, -10.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 10,
                        "unit": "cm",
                        "scale": 0.001,
                        "offset": 0,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "coastal_20m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_B01_20m.jp2",
                "type": "image/jp2",
                "title": "Coastal aerosol (band 1) - 20m",
                "view:azimuth": 104.444143831092,
                "view:incidence_angle": 10.3020133875849,
                "eo:bands": [
                    {
                        "center_wavelength": 0.443,
                        "common_name": "coastal",
                        "description": "Coastal aerosol (band 1)",
                        "full_width_half_max": 0.027,
                        "name": "coastal",
                    }
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "blue_20m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_B02_20m.jp2",
                "type": "image/jp2",
                "title": "Blue (band 2) - 20m",
                "view:azimuth": 103.214484410443,
                "view:incidence_angle": 10.1629755066291,
                "eo:bands": [
                    {
                        "center_wavelength": 0.49,
                        "common_name": "blue",
                        "description": "Blue (band 2)",
                        "full_width_half_max": 0.098,
                        "name": "blue",
                    }
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "green_20m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_B03_20m.jp2",
                "type": "image/jp2",
                "title": "Green (band 3) - 20m",
                "view:azimuth": 103.488678247608,
                "view:incidence_angle": 10.1808964701359,
                "eo:bands": [
                    {
                        "center_wavelength": 0.56,
                        "common_name": "green",
                        "description": "Green (band 3)",
                        "full_width_half_max": 0.045,
                        "name": "green",
                    }
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "red_20m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_B04_20m.jp2",
                "type": "image/jp2",
                "title": "Red (band 4) - 20m",
                "view:azimuth": 103.736028079286,
                "view:incidence_angle": 10.204345016995,
                "eo:bands": [
                    {
                        "center_wavelength": 0.665,
                        "common_name": "red",
                        "description": "Red (band 4)",
                        "full_width_half_max": 0.038,
                        "name": "red",
                    }
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "rededge1": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_B05_20m.jp2",
                "type": "image/jp2",
                "title": "Red edge 1 (band 5) - 20m",
                "view:azimuth": 103.877356128242,
                "view:incidence_angle": 10.2199137519271,
                "eo:bands": [
                    {
                        "center_wavelength": 0.704,
                        "common_name": "rededge",
                        "description": "Red edge 1 (band 5)",
                        "full_width_half_max": 0.019,
                        "name": "rededge1",
                    }
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "rededge2": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_B06_20m.jp2",
                "type": "image/jp2",
                "title": "Red edge 2 (band 6) - 20m",
                "view:azimuth": 104.040657605888,
                "view:incidence_angle": 10.2353974815048,
                "eo:bands": [
                    {
                        "center_wavelength": 0.74,
                        "common_name": "rededge",
                        "description": "Red edge 2 (band 6)",
                        "full_width_half_max": 0.018,
                        "name": "rededge2",
                    }
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "rededge3": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_B07_20m.jp2",
                "type": "image/jp2",
                "title": "Red edge 3 (band 7) - 20m",
                "view:azimuth": 104.182455368728,
                "view:incidence_angle": 10.2548958426358,
                "eo:bands": [
                    {
                        "center_wavelength": 0.783,
                        "common_name": "rededge",
                        "description": "Red edge 3 (band 7)",
                        "full_width_half_max": 0.028,
                        "name": "rededge3",
                    }
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "nir08": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_B8A_20m.jp2",
                "type": "image/jp2",
                "title": "NIR 2 (band 8A) - 20m",
                "view:azimuth": 104.353434373817,
                "view:incidence_angle": 10.2742195940777,
                "eo:bands": [
                    {
                        "center_wavelength": 0.865,
                        "common_name": "nir08",
                        "description": "NIR 2 (band 8A)",
                        "full_width_half_max": 0.033,
                        "name": "nir08",
                    }
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "swir16": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_B11_20m.jp2",
                "type": "image/jp2",
                "title": "SWIR 1 (band 11) - 20m",
                "view:azimuth": 104.096322495401,
                "view:incidence_angle": 10.1822287274623,
                "eo:bands": [
                    {
                        "center_wavelength": 1.61,
                        "common_name": "swir16",
                        "description": "SWIR 1 (band 11)",
                        "full_width_half_max": 0.143,
                        "name": "swir16",
                    }
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "swir22": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_B12_20m.jp2",
                "type": "image/jp2",
                "title": "SWIR 2 (band 12) - 20m",
                "view:azimuth": 104.427915655737,
                "view:incidence_angle": 10.2313283097348,
                "eo:bands": [
                    {
                        "center_wavelength": 2.19,
                        "common_name": "swir22",
                        "description": "SWIR 2 (band 12)",
                        "full_width_half_max": 0.242,
                        "name": "swir22",
                    }
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "visual_20m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_TCI_20m.jp2",
                "type": "image/jp2",
                "title": "True color image",
                "eo:bands": [
                    {
                        "center_wavelength": 0.665,
                        "common_name": "red",
                        "description": "Red (band 4)",
                        "full_width_half_max": 0.038,
                        "name": "red",
                    },
                    {
                        "center_wavelength": 0.56,
                        "common_name": "green",
                        "description": "Green (band 3)",
                        "full_width_half_max": 0.045,
                        "name": "green",
                    },
                    {
                        "center_wavelength": 0.49,
                        "common_name": "blue",
                        "description": "Blue (band 2)",
                        "full_width_half_max": 0.098,
                        "name": "blue",
                    },
                ],
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "roles": ["visual"],
            },
            "aot": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_AOT_20m.jp2",
                "type": "image/jp2",
                "title": "Aerosol optical thickness (AOT)",
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "scale": 0.001,
                        "offset": 0,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "wvp": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_WVP_20m.jp2",
                "type": "image/jp2",
                "title": "Water vapour (WVP)",
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 20,
                        "unit": "cm",
                        "scale": 0.001,
                        "offset": 0,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "scl": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R20m/T30TUK_20230816T105631_SCL_20m.jp2",
                "type": "image/jp2",
                "title": "Scene classification map (SCL)",
                "gsd": 20,
                "proj:shape": [5490, 5490],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [20.0, 0.0, 300000.0, 0.0, -20.0, 4500000.0],
                "raster:bands": [
                    {"nodata": 0, "data_type": "uint8", "spatial_resolution": 20}
                ],
                "roles": ["data", "reflectance"],
            },
            "coastal": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B01_60m.jp2",
                "type": "image/jp2",
                "title": "Coastal aerosol (band 1) - 60m",
                "view:azimuth": 104.444143831092,
                "view:incidence_angle": 10.3020133875849,
                "eo:bands": [
                    {
                        "center_wavelength": 0.443,
                        "common_name": "coastal",
                        "description": "Coastal aerosol (band 1)",
                        "full_width_half_max": 0.027,
                        "name": "coastal",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "blue_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B02_60m.jp2",
                "type": "image/jp2",
                "title": "Blue (band 2) - 60m",
                "view:azimuth": 103.214484410443,
                "view:incidence_angle": 10.1629755066291,
                "eo:bands": [
                    {
                        "center_wavelength": 0.49,
                        "common_name": "blue",
                        "description": "Blue (band 2)",
                        "full_width_half_max": 0.098,
                        "name": "blue",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "green_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B03_60m.jp2",
                "type": "image/jp2",
                "title": "Green (band 3) - 60m",
                "view:azimuth": 103.488678247608,
                "view:incidence_angle": 10.1808964701359,
                "eo:bands": [
                    {
                        "center_wavelength": 0.56,
                        "common_name": "green",
                        "description": "Green (band 3)",
                        "full_width_half_max": 0.045,
                        "name": "green",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "red_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B04_60m.jp2",
                "type": "image/jp2",
                "title": "Red (band 4) - 60m",
                "view:azimuth": 103.736028079286,
                "view:incidence_angle": 10.204345016995,
                "eo:bands": [
                    {
                        "center_wavelength": 0.665,
                        "common_name": "red",
                        "description": "Red (band 4)",
                        "full_width_half_max": 0.038,
                        "name": "red",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "rededge1_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B05_60m.jp2",
                "type": "image/jp2",
                "title": "Red edge 1 (band 5) - 60m",
                "view:azimuth": 103.877356128242,
                "view:incidence_angle": 10.2199137519271,
                "eo:bands": [
                    {
                        "center_wavelength": 0.704,
                        "common_name": "rededge",
                        "description": "Red edge 1 (band 5)",
                        "full_width_half_max": 0.019,
                        "name": "rededge1",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "rededge2_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B06_60m.jp2",
                "type": "image/jp2",
                "title": "Red edge 2 (band 6) - 60m",
                "view:azimuth": 104.040657605888,
                "view:incidence_angle": 10.2353974815048,
                "eo:bands": [
                    {
                        "center_wavelength": 0.74,
                        "common_name": "rededge",
                        "description": "Red edge 2 (band 6)",
                        "full_width_half_max": 0.018,
                        "name": "rededge2",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "rededge3_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B07_60m.jp2",
                "type": "image/jp2",
                "title": "Red edge 3 (band 7) - 60m",
                "view:azimuth": 104.182455368728,
                "view:incidence_angle": 10.2548958426358,
                "eo:bands": [
                    {
                        "center_wavelength": 0.783,
                        "common_name": "rededge",
                        "description": "Red edge 3 (band 7)",
                        "full_width_half_max": 0.028,
                        "name": "rededge3",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "nir08_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B8A_60m.jp2",
                "type": "image/jp2",
                "title": "NIR 2 (band 8A) - 60m",
                "view:azimuth": 104.353434373817,
                "view:incidence_angle": 10.2742195940777,
                "eo:bands": [
                    {
                        "center_wavelength": 0.865,
                        "common_name": "nir08",
                        "description": "NIR 2 (band 8A)",
                        "full_width_half_max": 0.033,
                        "name": "nir08",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "nir09": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B09_60m.jp2",
                "type": "image/jp2",
                "title": "NIR 3 (band 9) - 60m",
                "view:azimuth": 104.575775654248,
                "view:incidence_angle": 10.3278655991222,
                "eo:bands": [
                    {
                        "center_wavelength": 0.945,
                        "common_name": "nir09",
                        "description": "NIR 3 (band 9)",
                        "full_width_half_max": 0.026,
                        "name": "nir09",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "swir16_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B11_60m.jp2",
                "type": "image/jp2",
                "title": "SWIR 1 (band 11) - 60m",
                "view:azimuth": 104.096322495401,
                "view:incidence_angle": 10.1822287274623,
                "eo:bands": [
                    {
                        "center_wavelength": 1.61,
                        "common_name": "swir16",
                        "description": "SWIR 1 (band 11)",
                        "full_width_half_max": 0.143,
                        "name": "swir16",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "swir22_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_B12_60m.jp2",
                "type": "image/jp2",
                "title": "SWIR 2 (band 12) - 60m",
                "view:azimuth": 104.427915655737,
                "view:incidence_angle": 10.2313283097348,
                "eo:bands": [
                    {
                        "center_wavelength": 2.19,
                        "common_name": "swir22",
                        "description": "SWIR 2 (band 12)",
                        "full_width_half_max": 0.242,
                        "name": "swir22",
                    }
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.0001,
                        "offset": -0.1,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "visual_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_TCI_60m.jp2",
                "type": "image/jp2",
                "title": "True color image",
                "eo:bands": [
                    {
                        "center_wavelength": 0.665,
                        "common_name": "red",
                        "description": "Red (band 4)",
                        "full_width_half_max": 0.038,
                        "name": "red",
                    },
                    {
                        "center_wavelength": 0.56,
                        "common_name": "green",
                        "description": "Green (band 3)",
                        "full_width_half_max": 0.045,
                        "name": "green",
                    },
                    {
                        "center_wavelength": 0.49,
                        "common_name": "blue",
                        "description": "Blue (band 2)",
                        "full_width_half_max": 0.098,
                        "name": "blue",
                    },
                ],
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "roles": ["visual"],
            },
            "aot_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_AOT_60m.jp2",
                "type": "image/jp2",
                "title": "Aerosol optical thickness (AOT)",
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "scale": 0.001,
                        "offset": 0,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "wvp_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_WVP_60m.jp2",
                "type": "image/jp2",
                "title": "Water vapour (WVP)",
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {
                        "nodata": 0,
                        "data_type": "uint16",
                        "bits_per_sample": 15,
                        "spatial_resolution": 60,
                        "unit": "cm",
                        "scale": 0.001,
                        "offset": 0,
                    }
                ],
                "roles": ["data", "reflectance"],
            },
            "scl_60m": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/IMG_DATA/R60m/T30TUK_20230816T105631_SCL_60m.jp2",
                "type": "image/jp2",
                "title": "Scene classification map (SCL)",
                "gsd": 60,
                "proj:shape": [1830, 1830],
                "proj:bbox": [300000.0, 4390200.0, 409800.0, 4500000.0],
                "proj:transform": [60.0, 0.0, 300000.0, 0.0, -60.0, 4500000.0],
                "raster:bands": [
                    {"nodata": 0, "data_type": "uint8", "spatial_resolution": 60}
                ],
                "roles": ["data", "reflectance"],
            },
            "safe_manifest": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/manifest.safe",
                "type": "application/xml",
                "title": "SAFE manifest",
                "roles": ["metadata"],
            },
            "product_metadata": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/MTD_MSIL2A.xml",
                "type": "application/xml",
                "title": "Product metadata",
                "roles": ["metadata"],
            },
            "granule_metadata": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/MTD_TL.xml",
                "type": "application/xml",
                "title": "Granule metadata",
                "roles": ["metadata"],
            },
            "inspire_metadata": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/INSPIRE.xml",
                "type": "application/xml",
                "title": "INSPIRE metadata",
                "roles": ["metadata"],
            },
            "datastrip_metadata": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/DATASTRIP/DS_2APS_20230816T171602_S20230816T110544/MTD_DS.xml",
                "type": "application/xml",
                "title": "Datastrip metadata",
                "roles": ["metadata"],
            },
            "preview": {
                "href": "https://datazoo.blob.core.windows.net/sentinel2/S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602.SAFE/GRANULE/L2A_T30TUK_A042562_20230816T110544/QI_DATA/T30TUK_20230816T105631_PVI.jp2",
                "type": "image/jp2",
                "title": "Thumbnail",
                "roles": ["thumbnail"],
            },
        },
        "bbox": [-4.673798, 39.647784, -4.051453, 40.645928],
        "stac_extensions": [
            "https://stac-extensions.github.io/eo/v1.1.0/schema.json",
            "https://stac-extensions.github.io/raster/v1.1.0/schema.json",
            "https://stac-extensions.github.io/sat/v1.0.0/schema.json",
            "https://stac-extensions.github.io/projection/v1.1.0/schema.json",
            "https://stac-extensions.github.io/mgrs/v1.0.0/schema.json",
            "https://stac-extensions.github.io/view/v1.0.0/schema.json",
        ],
    })


def create_stac_item(client, collection_id, item_id):
    """Create a STAC item."""
    stac_item = get_sample_stac_item(collection_id, item_id)
    stac_item_get_items_response = client.stac.list_items(collection_id=collection_id)

    if any(item.id == stac_item.id for item in stac_item_get_items_response.features):
        logging.info(f"Item {stac_item.id} already exists. Deleting it before creating a new one.")
        client.stac.begin_delete_item(collection_id=collection_id, item_id=stac_item.id, polling=True).result()
        logging.info(f"Deleted item {stac_item.id}. Proceeding to create a new one.")
        time.sleep(15)
    else:
        logging.info(f"Item {stac_item.id} does not exist. Proceeding to create it.")

    stac_item.collection = collection_id

    stac_item_create_response = client.stac.begin_create_item(collection_id=collection_id, body=stac_item, polling=True)

    stac_item_create_response.result()
    logging.info(f"Created item {stac_item.id}")


def update_stac_item(client, collection_id, item_id):
    """Update a STAC item."""
    stac_item = get_sample_stac_item(collection_id, item_id)
    stac_item.properties["platform"] = "sentinel-2abcd"

    stac_item_create_or_update_response = client.stac.begin_update_item(
        collection_id=collection_id, item_id=stac_item.id, body=stac_item, polling=True
    )

    stac_item_create_or_update_response.result()
    logging.info(f"Updated item {stac_item.id}, platform: {stac_item.properties['platform']}")


def get_collection(client, collection_id):
    """Get a STAC collection."""
    collection = client.stac.get_collection(collection_id=collection_id)
    logging.info(f"Retrieved collection: {collection.id}")


def query_items(client, collection_id):
    """Query items using CQL2 filters."""
    # Query with filter
    query_options = StacSearchParameters(
        collections=[collection_id],
        filter_lang=FilterLanguage.CQL2_JSON,
        filter={"op": "<", "args": [{"property": "eo:cloud_cover"}, 10]},
        limit=5,
    )

    query_results = client.stac.search(body=query_options)
    if query_results.features:
        for item in query_results.features:
            if item.properties and item.properties.date_time:
                logging.info(f"  - {item.id}: {item.properties.date_time}")

    # Sorted query
    sorted_options = StacSearchParameters(
        collections=[collection_id],
        sort_by=[StacSortExtension(field="eo:cloud_cover", direction=StacSearchSortingDirection.ASC)],
        limit=3,
    )

    sorted_results = client.stac.search(body=sorted_options)

    if sorted_results.features:
        for item in sorted_results.features:
            if item.properties and item.properties.date_time:
                logging.info(f"  - {item.id}: {item.properties.date_time}")


def get_queryables(client, collection_id):
    """Get queryable properties for a collection."""
    queryables = client.stac.list_collection_queryables(collection_id=collection_id)
    properties = queryables.get("properties")

    if properties:
        for prop_name in list(properties.keys())[:10]:  # Show first 10
            logging.info(f"  - {prop_name}: {properties[prop_name].get('description', '')}")


def main():
    # Get configuration from environment
    endpoint = os.environ.get("AZURE_PLANETARY_COMPUTER_ENDPOINT")
    collection_id = os.environ.get("AZURE_COLLECTION_ID", "sentinel-2-l2a")
    item_id = os.environ.get("AZURE_ITEM_ID", "S2A_MSIL2A_20230816T105631_N0509_R094_T30TUK_20230816T171602")

    if not endpoint:
        raise ValueError("AZURE_PLANETARY_COMPUTER_ENDPOINT environment variable must be set")

    # Create client
    credential = DefaultAzureCredential()
    client = PlanetaryComputerClient(endpoint=endpoint, credential=credential, logging_enable=False)

    # Execute STAC specification operations
    get_landing_page(client)
    search_collections(client)
    search_items(client, collection_id)
    query_items(client, collection_id)
    get_queryables(client, collection_id)

    # Execute STAC item operations
    create_stac_item(client, collection_id, item_id)
    update_stac_item(client, collection_id, item_id)
    get_collection(client, collection_id)


if __name__ == "__main__":
    main()
