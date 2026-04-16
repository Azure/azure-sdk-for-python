"""
Test replace_collection returns HTTP 200 for both
creating a new collection and replacing an existing one.

Usage:
    python test_collection_status_code.py
"""

from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.planetarycomputer import PlanetaryComputerProClient

GEOCATALOG_ENDPOINT = "https://stablegeo.eebtfbh5h4bffxbf.uksouth.geocatalog.spatio.azure.com"
TEST_COLLECTION_ID = "test-status-code-check"


def capture_status_code(client, collection_id, body):
    """Call replace_collection and return (result, status_code)."""
    raw_response = None

    def capture_response(pipeline_response, deserialized, headers):
        nonlocal raw_response
        raw_response = pipeline_response.http_response
        return deserialized

    result = client.stac.replace_collection(
        collection_id=collection_id,
        body=body,
        cls=capture_response,
    )
    return result, raw_response.status_code


def main():
    credential = DefaultAzureCredential()
    client = PlanetaryComputerProClient(endpoint=GEOCATALOG_ENDPOINT, credential=credential)

    # Clean up any leftover from a previous run
    try:
        client.stac.get_collection(collection_id=TEST_COLLECTION_ID)
        print(f"Collection '{TEST_COLLECTION_ID}' already exists, deleting first...")
        client.stac.begin_delete_collection(collection_id=TEST_COLLECTION_ID).result()
        print("Deleted.")
    except ResourceNotFoundError:
        print(f"Collection '{TEST_COLLECTION_ID}' does not exist (good, starting clean).")

    # Minimal STAC collection body
    collection_body = {
        "id": TEST_COLLECTION_ID,
        "type": "Collection",
        "title": "Test Collection for Status Code Check",
        "description": "Temporary collection to verify HTTP status codes.",
        "license": "proprietary",
        "extent": {
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {"interval": [["2020-01-01T00:00:00Z", None]]},
        },
        "links": [],
    }

    # --- Test 1: CREATE (collection does not exist) ---
    print("\n--- Test 1: CREATE new collection ---")
    try:
        result, status_code = capture_status_code(client, TEST_COLLECTION_ID, collection_body)
        print(f"HTTP status code: {status_code}")
        print(f"Collection returned: {result['id']}")
        assert status_code == 200, f"Expected 200, got {status_code}"
        print("PASS: create (new) returned 200")
    except HttpResponseError as e:
        print(f"FAIL: HttpResponseError — status {e.status_code}, message: {e.message}")
        print("This may mean the service returned 201 for create, which the SDK does not accept.")

    # --- Test 2: REPLACE (collection already exists) ---
    print("\n--- Test 2: REPLACE existing collection ---")
    collection_body["description"] = "Updated description to test replace."
    try:
        result, status_code = capture_status_code(client, TEST_COLLECTION_ID, collection_body)
        print(f"HTTP status code: {status_code}")
        print(f"Collection returned: {result['id']}")
        assert status_code == 200, f"Expected 200, got {status_code}"
        print("PASS: replace (existing) returned 200")
    except HttpResponseError as e:
        print(f"FAIL: HttpResponseError — status {e.status_code}, message: {e.message}")

    # --- Cleanup ---
    print("\n--- Cleanup ---")
    try:
        client.stac.begin_delete_collection(collection_id=TEST_COLLECTION_ID).result()
        print(f"Deleted test collection '{TEST_COLLECTION_ID}'.")
    except Exception as e:
        print(f"Cleanup warning: {e}")


if __name__ == "__main__":
    main()
