import os
from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient
from azure.maps.search._generated.models import ReverseGeocodingBatchRequestItem, ReverseGeocodingBatchRequestBody

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY", "your subscription key")

def reverse_geocode_batch():
    maps_search_client = MapsSearchClient(credential=AzureKeyCredential(subscription_key))

    coordinates1 = ReverseGeocodingBatchRequestItem(coordinates=[-122.138679, 47.630356])
    coordinates2 = ReverseGeocodingBatchRequestItem(coordinates=[-122.138679, 47.630356])
    reverse_geocode_batch_request = ReverseGeocodingBatchRequestBody(batch_items=[coordinates1, coordinates2])

    result = maps_search_client.get_reverse_geocoding_batch(reverse_geocode_batch_request)

    if result.batch_items and len(result.batch_items) > 0:
        features = result.batch_items[0].features
        if features and len(features) > 0:
            props = features[0].properties
            if props and props.address:
                print(props.address.formatted_address)
            else:
                print("Address 1 is None")
        else:
            print("No features available for item 1")

        features = result.batch_items[1].features
        if features and len(features) > 0:
            props = features[0].properties
            if props and props.address:
                print(props.address.formatted_address)
            else:
                print("Address 2 is None")
        else:
            print("No features available for item 2")
    else:
        print("No batch items found")

if __name__ == '__main__':
   reverse_geocode_batch()
