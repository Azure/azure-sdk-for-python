"""
Version with a prepare and no explicit batch client

Notes:
- Moving from regular delete to prepare_delete is JUST adding the "prepare_" prefix.
- Raw response should be accessible with the "cls" callback, as Python guidelines suggests
"""

# Customer's experience
from azure.storage.blob import BlobServiceClient

service = BlobServiceClient.from_connection_string(conn_str="my_connection_string")

delete0_receipt = service.prepare_delete_blob("container0", "blob0")
delete1_receipt = service.prepare_delete_blob("container1", "blob1")
delete2_receipt = service.prepare_delete_blob("container2", "blob2", delete_snapshots="include")
delete3_receipt = service.get_container_client("container3").prepare_delete_blob("blob3")

# Unwrap your *args as necessary, kwargs still available for pipeline/policies options
response = service.batch(
    delete0_receipt,
    delete1_receipt,
    delete2_receipt,
    enable_logging = True # Whatever usually kwargs available
)

failed_responses = {
    key: r for key, r in response.items()
    if r.status_code != 204
}
failed_queries = [
    key for key, r in response.items()
    if r.status_code != 204
]
response_2 = service.batch(
    *failed_queries
)
all_responses = response.values()


# SDK code
class BlobServiceClient:
    def batch(
        *args: BatchRequest,
        **kwargs: Any,
    ) -> Dict[BatchRequest, Response[T]]:
        ...

class BatchClient:
    def delete_blob(
        container,              # type: str
        blob,                   # type: str
        delete_snapshots=None,  # type: Optional[str]
        **kwargs                # 'if_modified_since', etc.
    ):
        ...

    def send(
        throw_failures = True,  # type: bool
    ):
        ...
