from unittest.mock import _patch_dict, patch
from uuid import uuid4

from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline.transport.pyodide import PyodideTransport
from azure.storage.blob.aio import BlobClient, BlobServiceClient

# pylint: disable=import-error
from async_testing import AsyncTestSuite


class PyodideTransportIntegrationTestSuite(AsyncTestSuite):
    """Integration tests for the Pyodide transport."""

    text_analytics_client: TextAnalyticsClient
    blob_service_client: BlobServiceClient

    def __init__(
        self,
        text_analytics_key: str,
        text_analytics_endpoint: str,
        blob_service_key: str,
        blob_service_endpoint: str,
    ):
        self.text_analytics_client = TextAnalyticsClient(
            endpoint=text_analytics_endpoint,
            credential=AzureKeyCredential(text_analytics_key),
            transport=PyodideTransport(),
        )
        self.blob_service_client = BlobServiceClient(
            blob_service_endpoint, blob_service_key, transport=PyodideTransport()
        )

    async def test_decompress_generator(self):
        """Test that we can decompress streams properly."""
        url = "data/hello-world.gz"
        request = HttpRequest(method="GET", url=url)
        transport = PyodideTransport()
        response = await transport.send(request, stream_response=True)
        response.headers["enc"] = "deflate"
        data = b"".join([x async for x in response.iter_bytes()])
        assert data == b"hello world\n"

        response = await transport.send(request, stream_response=True)
        data = b"".join([x async for x in response.iter_raw()])
        assert data != b"hello world\n"

        response = await transport.send(request, stream_response=True)
        data = b"".join([x async for x in response.iter_bytes()])
        assert data != b"hello world\n"

        response = await transport.send(request, stream_response=True)
        response.headers["enc"] = "deflate"
        data = b"".join([x async for x in response.iter_bytes()])
        assert data == b"hello world\n"


    async def test_sentiment_analysis(self):
        """Test that sentiment analysis works."""
        results = await self.text_analytics_client.analyze_sentiment(
            ["good great amazing"]
        )
        assert len(results) == 1
        result = results[0]
        assert result.sentiment == "positive"
        assert result.confidence_scores.positive > 0.98
        assert result.confidence_scores.neutral < 0.02
        assert result.confidence_scores.negative < 0.02

    async def test_storage(self):
        """Test that we can upload and download from blob storage"""
        account_name = uuid4().hex
        container_client = await self.blob_service_client.create_container(account_name)
        blob_name = uuid4().hex
        blob_data = b"012345"
        try:
            assert await container_client.exists()
            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(blob_data)

            # make a new client so we don't have cached data
            blob_client = BlobClient(
                account_url=self.blob_service_client.url,
                container_name=container_client.container_name,
                blob_name=blob_name,
                credential=container_client.credential,
                max_single_get_size=1,
                max_chunk_get_size=1,
                transport=PyodideTransport(),
            )
            assert await blob_client.exists()
            downloader = await blob_client.download_blob()
            i = 0
            async for chunk in downloader.chunks():
                assert chunk == bytes(str(i), "utf-8")
                i += 1
            assert i == len(blob_data)

        except Exception:
            await container_client.delete_container()
            raise
        else:
            await container_client.delete_container()
