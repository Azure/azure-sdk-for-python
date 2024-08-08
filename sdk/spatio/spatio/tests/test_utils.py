import os
import json

def create_collection(aopc_client, collection_id):
    createoperations = aopc_client.create_operations_collections
    curr_dirr =  os.path.dirname(__file__)
    collection_file =os.path.join(curr_dirr, "data", "collection.json")
    with open(collection_file) as f:
        stac_collection = json.load(f)
    stac_collection["id"] = collection_id
    stac_collection["title"] = collection_id
    collection = createoperations.collection_api_collections_post(stac_collection)
    return collection

def delete_collection(aopc_client, collection_id):
    delete_operations = aopc_client.delete_operations
    delete_operations.collection_api_collections_collection_id_delete(collection_id)