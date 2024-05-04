# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Florence image Embeddings wrapper."""

import base64
import uuid
import logging
from typing import List

import requests

logger = logging.getLogger(__name__)


class FlorenceEmbedder:
    """Florence Embedding API client wrapper."""

    def __init__(self, embedding_uri: str, api_key: str):
        """Initialize a Florence Embedding client."""
        self.embedding_uri = embedding_uri
        self.api_key = api_key

    def embed_images(self, images_base64: List[str], **kwargs) -> List[List[float]]:
        """Computes images embeddings using Florence model."""
        embeddings = []
        for image_base64 in images_base64:
            image_bytes = base64.decodebytes(bytes(image_base64, "utf-8"))
            embedded = self._embed_image(image_bytes)
            embeddings.append(embedded)
        return embeddings

    def _embed_image(self, image_bytes):
        try:
            res = requests.post(
                url=self.embedding_uri,
                data=image_bytes,
                headers={
                    "Content-Type": "application/octet-stream",
                    "apim-request-id": str(uuid.uuid4()),
                    "Ocp-Apim-Subscription-Key": self.api_key,
                },
            )

            res.raise_for_status()
            response_body = res.json()
            return response_body["vector"]

        except requests.exceptions.RequestException as e:
            logger.error(f"failed to call vision vectorize API. Details {e}")
            raise Exception(f"failed to call vision vectorize API. Details {e}") from e

        except Exception as e:
            logger.error(f"failed to call vision vectorize API. Details {e}")
            raise Exception(f"failed to call vision vectorize API with the Exception {e}") from e
