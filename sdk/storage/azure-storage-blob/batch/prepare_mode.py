"""
Version with a prepare and no explicit batch client
"""

# Customer's experience
from azure.storage.blob import BlobServiceClient

service = BlobServiceClient.from_connection_string(conn_str="my_connection_string")

delete0_receipt = service.prepare_delete_blob("container0", "blob0")
delete1_receipt = service.prepare_delete_blob("container1", "blob1")
delete2_receipt = service.prepare_delete_blob("container2", "blob2", delete_snapshots="include")

# Unwrap your *args as necessary, kwargs still available for pipeline/policies options
response = service.batch(
    delete0_receipt,
    delete1_receipt,
    delete2_receipt,
    enable_logging = True # Whatever usually kwargs available
)

raw_response = response.get_raw_response()

delete0_result = response.get_value(delete0_receipt)


# SDK code
class BlobServiceClient:
    def get_batch_client() -> BatchClient:
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
