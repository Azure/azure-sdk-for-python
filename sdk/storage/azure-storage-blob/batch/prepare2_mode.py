"""
Version with a prepare and no explicit batch client

Notes:
- Moving from regular delete to delete is JUST adding the "" prefix.
- Raw response should be accessible with the "cls" callback, as Python guidelines suggests
"""
from typing import Dict

# Customer's experience
from azure.storage.blob import BlobServiceClient

batch_client = BlobBatchClient.from_connection_string(conn_str="my_connection_string")

# You can prepare a request even if you don't have credentials. Connection string can even be optional
# Zen of Python: There should be one-- and preferably only one --obvious way to do it.

delete0_request = batch_client.delete_blob("container0", "blob0")
delete1_request = batch_client.delete_blob("container1", "blob1")
delete2_request = batch_client.delete_blob("container2", "blob2")

# Unwrap your *args as necessary, kwargs still available for pipeline/policies options
service.batch(
    delete0_request,
    delete1_request,
    delete2_request,
    enable_logging = True # Whatever usually kwargs available
)  # None

# We can get the result directly from here
delete0_response = delete0_request.get_result()


# Alternative writting if you want to get requests and response as array
requests = []
requests.append(batch_client.delete_blob("container0", "blob0"))
requests.append(batch_client.delete_blob("container1", "blob1"))
requests.append(batch_client.delete_blob("container2", "blob2"))

service.batch(
    *requets
    enable_logging = True # Whatever usually kwargs available
)  # None

responses = [r.get_result() for r in requests]


# SDK code
class BlobServiceClient:
    def batch(
        *args: BatchRequest,
        **kwargs: Any,
    ) -> None:
        ...

class ContainerClient:
    def delete_blob(
        container,              # type: str
        blob,                   # type: str
        delete_snapshots=None,  # type: Optional[str]
        **kwargs                # 'if_modified_since', etc.
    ):  # type: BatchRequest
        ...
