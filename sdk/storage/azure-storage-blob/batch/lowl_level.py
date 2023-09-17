from azure.core.pipeline import MultiPartRequest, HTTPRequest
from azure.core.pipeline.policies import *
from azure.storage.blob import StorageServiceClient

batch_client = BlobBatchClient.from_connection_string(conn_str="my_connection_string")

async def send_multipart_stuff()

    model = MyComplxeXmlModel(
        id=42
    )
    model_bytes = model.serialize(is_xml=True)

    delete0 = HTTPRequest(
        method="DELETE",
        url="/container0/blob0",
    )
    delete0.set_xml_body(model)
    delete1 = HTTPRequest(
        method="DELETE",
        url="/container1/blob1"    
    )

    multi_part = HTTPRequest(
        method="POST",
        url="/batch"
    )
    multi_part.set_multipart_mixed_body(
        delete0,
        delete1
        policies=[
            UserAgentPolicy(),
            AsyncAuthentication(), # This guy contains co-routine on_request/on_response
            RetryPolicy(), # Will raise NoOp, not allowed in this context
        ],
    )

    list_of_responses = await batch_client.connection.send(
        multi_part,
    )

    delete0_response = list_of_responses[0]



# High level scenario

from azure.storage.blob import StorageServiceClient

batch_client = BlobBatchClient.from_connection_string(conn_str="my_connection_string")

container_client = batch_client.get_container_client("container0")
container_client.delete_blobs(
    "blob1",
    "blob2",
    "blob3",
    include_snapshots="all"
)