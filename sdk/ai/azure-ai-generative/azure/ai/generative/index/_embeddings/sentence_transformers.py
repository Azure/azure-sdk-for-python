# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""SentenceTransformer based Embeddings."""

from dataclasses import dataclass, field
from typing import Any, Dict, List

DEFAULT_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"


@dataclass
class SentenceTransformerEmbeddings:
    """
    HuggingFace sentence_transformers embedding models.

    To use, you should have the ``sentence_transformers`` python package installed.

    Example:
    -------
        .. code-block:: python

            from langchain.embeddings import HuggingFaceEmbeddings

            model_name = "sentence-transformers/all-mpnet-base-v2"
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': False}
            hf = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
    """

    client: Any
    """Key word arguments to pass to the model."""
    encode_kwargs: Dict[str, Any] = field(default_factory=dict)
    """Key word arguments to pass when calling the `encode` method of the model."""
    multi_process: bool = False
    """Run encode() on multiple GPUs."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Compute doc embeddings using a HuggingFace transformer model.

        Args:
        ----
            texts: The list of texts to embed.

        Returns:
        -------
            List of embeddings, one for each text.
        """
        import sentence_transformers

        texts = [x.replace("\n", " ") for x in texts]
        if self.multi_process:
            pool = self.client.start_multi_process_pool()
            embeddings = self.client.encode_multi_process(texts, pool)
            sentence_transformers.SentenceTransformer.stop_multi_process_pool(pool)
        else:
            embeddings = self.client.encode(texts, **self.encode_kwargs)

        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Compute query embeddings using a HuggingFace transformer model.

        Args:
        ----
            text: The text to embed.

        Returns:
        -------
            Embeddings for the text.
        """
        return self.embed_documents([text])[0]
