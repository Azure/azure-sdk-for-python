"""
Example: Using truststore.SSLContext with Azure SDK for Python (Sync and Async)

This sample demonstrates how to use `truststore.SSLContext` directly to leverage
operating system certificate stores when working with Azure SDK for Python.

Unlike `truststore.inject_into_ssl()` which globally patches the ssl module,
this approach gives you more control over which connections use system certificates
by creating custom transport sessions with a truststore-based SSLContext.

Requirements:
    pip install truststore azure-identity azure-storage-blob aiohttp requests
"""

import ssl
import asyncio
import truststore
import requests
import aiohttp
from requests.adapters import HTTPAdapter

from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
from azure.core.pipeline.transport import RequestsTransport, AioHttpTransport


# =============================================================================
# Helper: Custom HTTPAdapter for requests
# =============================================================================

class TruststoreHTTPAdapter(HTTPAdapter):
    """Custom HTTPAdapter that uses truststore.SSLContext for SSL verification."""
    
    def __init__(self, ssl_context, **kwargs):
        self._ssl_context = ssl_context
        super().__init__(**kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self._ssl_context
        return super().init_poolmanager(*args, **kwargs)


# =============================================================================
# Synchronous Example
# =============================================================================

def sync_blob_storage_with_ssl_context():
    """Synchronous Azure Blob Storage using truststore.SSLContext directly.
    
    This approach gives you more control over the SSL context configuration
    without globally injecting truststore into ssl module.
    """
    
    account_url = "https://<your-storage-account>.blob.core.windows.net"
    
    # Create SSLContext using truststore (uses system certificate stores)
    ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    
    # Create a session with truststore adapter
    session = requests.Session()
    adapter = TruststoreHTTPAdapter(ssl_context)
    session.mount("https://", adapter)
    
    # Create transport with the custom session
    transport = RequestsTransport(session=session, session_owner=False)
    
    with transport:
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=credential,
            transport=transport,
        )
        
        print("=== Sync Blob Storage with SSLContext ===")
        for container in blob_service_client.list_containers():
            print(f"Container: {container['name']}")
        
        blob_service_client.close()
        credential.close()
    
    session.close()  # Close the session manually since session_owner=False


# =============================================================================
# Asynchronous Example
# =============================================================================

async def async_blob_storage_with_ssl_context():
    """Asynchronous Azure Blob Storage using truststore.SSLContext directly.
    
    This approach gives you more control over the SSL context configuration
    without globally injecting truststore into ssl module.
    """
    
    account_url = "https://<your-storage-account>.blob.core.windows.net"
    
    # Create SSLContext using truststore (uses system certificate stores)
    ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    
    # Create a TCPConnector with our truststore SSLContext
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    session = aiohttp.ClientSession(connector=connector)
    
    # Create transport with the custom session
    transport = AioHttpTransport(session=session, session_owner=False)
    
    async with transport:
        credential = AsyncDefaultAzureCredential()
        blob_service_client = AsyncBlobServiceClient(
            account_url=account_url,
            credential=credential,
            transport=transport,
        )
        
        print("=== Async Blob Storage with SSLContext ===")
        async for container in blob_service_client.list_containers():
            print(f"Container: {container['name']}")
        
        await blob_service_client.close()
        await credential.close()
    
    await session.close()  # Close the session manually since session_owner=False


if __name__ == "__main__":
    sync_blob_storage_with_ssl_context()
    asyncio.run(async_blob_storage_with_ssl_context())
