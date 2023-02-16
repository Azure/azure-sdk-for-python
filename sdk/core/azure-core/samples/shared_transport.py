# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
import os
from azure.core.pipeline.transport import RequestsTransport
from azure.storage.blob import BlobServiceClient

account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
account_url = "https://{}.blob.core.windows.net".format(account_name)
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def shared_transport():
    # [START shared_transport]
    shared_transport = RequestsTransport()
    with shared_transport:
        blob_service_client1 = BlobServiceClient.from_connection_string(
            connection_string,
            transport=shared_transport,
            session_owner=False)
        blob_service_client2 = BlobServiceClient.from_connection_string(
            connection_string,
            transport=shared_transport,
            session_owner=False)
        account_info = blob_service_client1.get_account_information()
        print(account_info)
        service_properties = blob_service_client2.get_service_properties()
        print(service_properties)
    # [END shared_transport]


def shared_transport_with_pooling():
    # [START shared_transport_with_pooling]
    import requests
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    shared_transport = RequestsTransport(session=session)
    with shared_transport:
        blob_service_client1 = BlobServiceClient.from_connection_string(
            connection_string,
            transport=shared_transport,
            session_owner=False)
        blob_service_client2 = BlobServiceClient.from_connection_string(
            connection_string,
            transport=shared_transport,
            session_owner=False)
        account_info = blob_service_client1.get_account_information()
        print(account_info)
        service_properties = blob_service_client2.get_service_properties()
        print(service_properties)
    # [END shared_transport_with_pooling]
