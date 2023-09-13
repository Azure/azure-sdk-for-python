"""
Version with a prepare and no explicit batch client

Notes:
- Moving from regular delete to prepare_delete is JUST adding the "prepare_" prefix.
- Raw response should be accessible with the "cls" callback, as Python guidelines suggests
"""
from typing import Dict

# Customer's experience
from azure.storage.blob import BlobServiceClient

service = BlobServiceClient.from_connection_string(conn_str="my_connection_string")

# Here, "delete_blob" is on the container client right now, so that's more natural this way
# I verified with Anna that the "get_container_client" is free of overhead

delete0_receipt = service.get_container_client("container0").prepare_delete_blob("blob0")
delete1_receipt = service.get_container_client("container1").prepare_delete_blob("blob1")
delete2_receipt = service.get_container_client("container2").prepare_delete_blob("blob2", delete_snapshots="include")

# Alternative design, but less intuitive to me
# Zen of Python: There should be one-- and preferably only one --obvious way to do it.
delete0_receipt = service.prepare_delete_blob("container0", "blob0")

# Unwrap your *args as necessary, kwargs still available for pipeline/policies options
response = service.batch(
    delete0_receipt,
    delete1_receipt,
    delete2_receipt,
    enable_logging = True # Whatever usually kwargs available
)  # Dict[BatchRequest, Response[T]]

# Get your failed responses as dict
failed_responses = {
    key: r for key, r in response.items()
    if r.status_code != 204
}
# Get your failed responses as array
failed_queries = [
    key for key, r in response.items()
    if r.status_code != 204
]
# Re-inject them
response_2 = service.batch(
    *failed_queries
)
# Get all response as array using "values()" builtin method
all_responses = response.values()


# SDK code
class BlobServiceClient:
    def batch(
        *args: BatchRequest,
        **kwargs: Any,
    ) -> Dict[BatchRequest, Response[T]]:
        ...

class ContainerClient:
    def prepare_delete_blob(
        container,              # type: str
        blob,                   # type: str
        delete_snapshots=None,  # type: Optional[str]
        **kwargs                # 'if_modified_since', etc.
    ):  # type: BatchRequest
        ...
