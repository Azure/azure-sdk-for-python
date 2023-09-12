"""
Close version to the C# version of Ted.

Notes:
- I find it more intuitive to have the "get_result" on the response that takes the "receipt", than the opposite
- "delete" has exactly the same signature than on the ContainerClient, which simplifies learning for customers
"""

# Customer's experience
from azure.storage.blob import BlobServiceClient

service = BlobServiceClient.from_connection_string(conn_str="my_connection_string")

batch_client = service.get_batch_client()

delete0_receipt = batch_client.delete_blob("container0", "blob0")
delete1_receipt = batch_client.delete_blob("container1", "blob1")
delete2_receipt = batch_client.delete_blob("container2", "blob2", delete_snapshots="include")

response = batch_client.send(
    enable_logging = True # Whatever usually kwargs available
)
raw_response = response.get_raw_response()

delete0_result = response.get_value(delete0_receipt)
# or
delete0_result = response.get_results()[delete0_receipt]


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
        **kwargs
    ):
        ...
