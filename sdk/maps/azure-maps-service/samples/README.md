---
page_type: sample
languages:
  - python
products:
  - azure
  - maps-service
urlFragment: maps-service-samples
---

# Maps Service API client library for Python Samples

The following are code samples that show common scenario operations with the Azure Maps Service API client library.

* [alias.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/alias.py) - Azure Maps Alias Samples:
  * Creates alias
  * Assign a `creator_data_item` to an alias
  * Get details of an alias
  * List aliases
  * Delete an alias

* [data.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/data.py) - Azure Maps Data Samples:
  * Upload a file
  * Update an existing file
  * Get status of an upload
  * Download a file
  * List files
  * Delete a file

* [conversion.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/conversion.py) - Azure Maps Conversion Samples:
  * Convert an existing file
  * Get a converted data
  * List conversions
  * Delete a conversion data

* [dataset.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/dataset.py) - Azure Maps Dataset Samples:
  * Create dataset from converted data
  * List datasets
  * Get a dataset
  * Delete a dataset

* [elevation.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/elevation.py) - Azure Maps Elevation Samples:
  * Get data for Bounding Box
  * Get data for Points
  * Get data for Polyline
  * Get data for Multiple Points
  * Get data for Long Polyline

* [featurestate.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/featurestate.py) - Azure Maps Feature State Samples:
  * Create stateset
  * List statesets
  * Get statesets by id
  * Get states from stateset by id and feature
  * Update stateset by id
  * Update state by id and feature
  * Delete state by id and feature
  * Detelete stateset by id

* [geolocation.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/geolocation.py) - Azure Maps Geolocation Samples:
  * Get location by ip

* [mobility.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/mobility.py) - Azure Maps Mobility Samples:
  * Get Metro Area Info
  * Get Metro Area
  * Get Nearby Transit
  * Get Real Time Arrivals
  * Get Transit Route
  * Get Transit Itinerary
  * Get Transit Line Info
  * Get Transit Stop Info

* [render.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/render.py) - Azure Maps Render Samples:
  * Get Copyright Caption
  * Get Copyright for Tile
  * Get Copyright for World
  * Get Copyright from Bounding Box
  * Get Map Imagery Tile
  * Get Map State Tile
  * Get Map Static Image
  * Get Map Tile for V2
  * Get Map Tile for V1

* [route.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/route.py) - Azure Maps Route Samples:
  * Get Route Directions
  * Get Route Range
  * Post Route Directions with Request Body
  * Post Route Directions Batch with Request Body
  * Post Route Matrix with Request Body

* [search.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/search.py) - Azure Maps Search Samples:
  * Get Search Address
  * Get Search Address Reverse
  * Get Search Address Reverse Cross Street
  * Get Search Address Structured
  * Get Search Fuzzy
  * Get Search POI
  * Get Search POI Category
  * Get Search POI Category Tree
  * Get Search Polygon
  * Post Search Address Batch
  * Post Search Address Reverse Batch
  * Post Search Fuzzy Batch
  * Post Search Inside Geometry

* [spatial.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/spatial.py) - Azure Maps Spatial Samples:
  * Get Buffer
  * Get Closest Point
  * Get Geofence
  * Get Great Circle Distance
  * Get Point In Polygon
  * Post Buffer
  * Post Closest Point
  * Post Geofence
  * Post Point In Polygon

* [tileset.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/tileset.py) - Azure Maps Tileset Samples:
  * Create Tileset
  * Delete Tileset
  * Get Tileset
  * List Tilesets

* [timezone.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/timezone.py) - Azure Maps Timezone Samples:
  * Get Timezone By Coordinate
  * Get Timezone By Id
  * Get Timezone Enum IANA
  * Get Timezone Enum Windows
  * Get Timezone IANA Version
  * Get Timezone Windows to IANA

* [traffic.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/traffic.py) - Azure Maps Traffic Samples:
  * Get Traffic Flow Segment
  * Get Traffic Flow Tile
  * Get Traffic Incident Detail
  * Get Traffic Incident Tile
  * Get Traffic Incident Viewport

* [weather.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/weather.py) - Azure Maps Weather Samples:
  * Get Current Conditions
  * Get Daily Forecast
  * Get Daily Indices
  * Get Hourly Forecast
  * Get Minute Forecast
  * Get Quarter Day Forecast
  * Get Severe Weather Alerts
  * Get Weather Along Route

* [wfs.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/maps/azure-maps-service/samples/wfs.py) - Azure Maps Web Feature Service Samples:
  * Delete Feature
  * Get Collection
  * Get Collection Definition
  * Get Collections
  * Get Conformance
  * Get Feature
  * Get Features
  * Get Landing Page

## Prerequisites
* Python 2.7 or 3.5.3+
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure Maps account](https://docs.microsoft.com/azure/azure-maps/how-to-manage-account-keys) to run these samples.

## Setup

1. Install the latest beta version of Azure Maps Service that the samples use:

```bash
pip install azure-maps-service
```

2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run. `SUBSCRIPTION_KEY` has to refer to your subscription key.
3. Follow the usage described in the file, e.g. `python alias.py`

## Next steps

Check out the [API reference documentation](https://aka.ms/azsdk-python-cosmos-ref) to learn more about what you can do with the Azure Maps Service API client library.