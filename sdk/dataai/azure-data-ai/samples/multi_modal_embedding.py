# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Embed a document, a query and a document image with the multimodal embedding operation.

Set AZURE_DATA_AI_ENDPOINT. To embed an image, also set:

- AZURE_DATA_AI_IMAGE_URL: the image's Azure Blob Storage URL, without a query string.
- AZURE_DATA_AI_IMAGE_SAS: a user delegation SAS for that blob: read-only, https-only, valid for about 15 minutes
  and signed by the identity this sample signs in with. The package README shows how to make one.

A SAS is a credential: don't print, log or store it.
"""

import base64
import hashlib
import json
import os
import struct
import urllib.request

from azure.data.ai import InferenceClient
from azure.data.ai.models import (
    EmbeddingWarningCode,
    MultimodalDenseAndMultiVectorEmbedding,
    MultimodalDenseEmbedding,
    EmbeddingResult,
    MultimodalEmbeddingUsage,
    MultimodalMultiVectorEmbedding,
)
from azure.identity import DefaultAzureCredential


def embed_text(client: InferenceClient) -> None:
    # A request has at most one text or query item.
    result = client.get_embeddings(
        model="microsoft-embedding-1-large",
        inputs=[
            {
                "id": "doc-1",
                "kind": "text",
                "content": "Invoice terms: net 30, 2% discount if paid within 10 days.",
            }
        ],
        dimensions=1536,
    )
    item = result.data[0]
    if isinstance(item, MultimodalDenseEmbedding) and isinstance(item.embedding, list):
        print(f"{result.model}: {item.id}, {len(item.embedding)} dimensions")
    if isinstance(result.usage, MultimodalEmbeddingUsage):
        print(f"  usage: {result.usage.text_tokens} text tokens")
    # Text over the model's token limit is embedded from its start and reported here, not rejected.
    for warning in result.warnings or []:
        if warning.code == EmbeddingWarningCode.INPUT_TRUNCATED:
            print(f"  inputs[{warning.index}]: embedded {warning.tokens} of {warning.input_tokens} tokens")


def embed_query_dense_and_multi(client: InferenceClient) -> None:
    item = client.get_embeddings(
        model="microsoft-embedding-1-large",
        inputs=[{"id": "query-1", "kind": "query", "content": "When is the invoice due?"}],
        vector_kind="dense_multi",
    ).data[0]
    if isinstance(item, MultimodalDenseAndMultiVectorEmbedding) and isinstance(item.embedding, list):
        rows, dims = item.shape
        print(f"  {item.id}: a {len(item.embedding)}-dimension vector and {rows} vectors of {dims}")


def embed_blob_image(client: InferenceClient, url: str, sas_token: str) -> None:
    page = client.get_embeddings(
        model="microsoft-embedding-1-large",
        inputs=[{"id": "page-1", "kind": "image", "url": url, "sasToken": sas_token}],
        vector_kind="multi",
        encoding_format="base64",
        delivery="inline",
    ).data[0]
    if isinstance(page, MultimodalMultiVectorEmbedding) and isinstance(page.multi_embedding, str):
        rows, dims = page.shape
        # Base64 vectors are little-endian values of `outputDataKind` (float16 for multi-vectors), row-major in `shape`.
        values = struct.unpack(f"<{rows * dims}e", base64.b64decode(page.multi_embedding))
        print(f"  {page.id}: {page.width}x{page.height} {page.format}, {rows} vectors of {dims}")
        print(f"  first vector starts {values[:3]}")


def embed_blob_image_by_link(client: InferenceClient, url: str, sas_token: str) -> None:
    output = client.get_embeddings(
        model="microsoft-embedding-1-large",
        inputs=[{"id": "page-1", "kind": "image", "url": url, "sasToken": sas_token}],
        delivery="link",
    ).output
    if output is None:
        return
    # The link is url plus a read-only SAS for this one file, valid until expires_at; any HTTP client can read it.
    with urllib.request.urlopen(f"{output.url}?{output.sas_token}") as response:
        data = response.read()
    if len(data) != output.size_in_bytes or hashlib.sha256(data).hexdigest() != output.sha256:
        raise ValueError("The result file doesn't match output.size_in_bytes and output.sha256.")
    results = EmbeddingResult(json.loads(data))
    print(
        f"  result link: {output.record_count} records, {output.size_in_bytes} bytes, valid until {output.expires_at}"
    )
    print(f"  {results.data[0].id}: {results.data[0].kind} vectors")


def main() -> None:
    endpoint = os.environ["AZURE_DATA_AI_ENDPOINT"]
    image_url = os.environ.get("AZURE_DATA_AI_IMAGE_URL")
    image_sas = os.environ.get("AZURE_DATA_AI_IMAGE_SAS")

    with DefaultAzureCredential() as credential:
        with InferenceClient(endpoint=endpoint, credential=credential) as client:
            embed_text(client)
            embed_query_dense_and_multi(client)
            if image_url and image_sas:
                embed_blob_image(client, image_url, image_sas)
                embed_blob_image_by_link(client, image_url, image_sas)


if __name__ == "__main__":
    main()
