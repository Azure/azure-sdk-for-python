import json
from io import BytesIO
import requests
from azure.planetarycomputer import MicrosoftPlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

# Setup
credential = DefaultAzureCredential()
endpoint = "https://test-accessibility.h5d5a9crhnc8deaz.uksouth.geocatalog.spatio.azure.com"
client = MicrosoftPlanetaryComputerProClient(endpoint=endpoint, credential=credential)

collection_id = "tutorial-collection-20250527170217"
thumbnail_url = "https://ai4edatasetspublicassets.blob.core.windows.net/assets/pc_thumbnails/sentinel-2.png"

# Define thumbnail asset metadata
data_str = json.dumps({
    "key": "thumbnail",
    "href": thumbnail_url,
    "type": "image/png",
    "roles": ["thumbnail"],
    "title": "Sentinel-2 preview"
})

# Download thumbnail
thumbnail_bytes = BytesIO(requests.get(thumbnail_url).content)
thumbnail_tuple = ("thumbnail.png", thumbnail_bytes)

# Upload using correct client group
try:
    client.stac_collection_assets.create_or_replace(
        collection_id=collection_id, body={
            "data": json.loads(data_str),
            "file": thumbnail_tuple
        })
    client.stac_items.begin_create(
        collection_id=collection_id,
        body={
            "id": "thumbnail-item",
            "type": "Feature",
            "stac_version": "1.0.0",
            "stac_extensions": ["https://stac-extensions.github.io/thumbnail/v1.0.0/schema.json"],
            "properties": {
                "title": "Thumbnail Item",
                "description": "An item containing a thumbnail asset"
            },
            "geometry": None,
            "bbox": None,
            "links": [],
            "assets": {
                "thumbnail": {
                    "href": f"{endpoint}/collections/{collection_id}/assets/thumbnail",
                    "type": "image/png",
                    "roles": ["thumbnail"]
                }
            }
        }
    ).result()
except Exception as e:
    print("❌ Failed to upload thumbnail:", e)
