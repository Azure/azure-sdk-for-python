# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Faiss based Vector Index using a file based DocumentStore."""
import json
import os
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Tuple, Union

import numpy as np
from azure.ai.resources._index._docstore import FileBasedDocstore
from azure.ai.resources._index._documents import Document
from azure.ai.resources._index._utils.logging import get_logger

logger = get_logger("indexes.faiss")


def import_faiss_or_so_help_me() -> ModuleType:
    """Import faiss if available, otherwise raise error."""
    try:
        if os.getenv("FAISS_NO_AVX2", "false").lower() == "true":
            from faiss import swigfaiss as faiss
        else:
            import faiss
    except ImportError as e:
        raise ImportError(
            "Could not import faiss python package. "
            "Please install it with `pip install faiss-gpu` (for CUDA supported GPU) "
            "or `pip install faiss-cpu` (depending on Python version)."
        ) from e
    return faiss


class FaissAndDocStore:
    """Faiss based VectorStore using a file based DocumentStore."""

    docstore: FileBasedDocstore
    index: Any
    query_embed: Callable[[str], List[float]]
    index_to_doc_id: Dict[str, str]

    def __init__(
        self,
        query_embed: Callable[[str], List[float]],
        index: Any,
        docstore: FileBasedDocstore,
        index_to_doc_id: Dict[str, str]
    ):
        """Initialize FaissAndDocStore."""
        self.query_embed = query_embed
        self.index = index
        self.docstore = docstore
        self.index_to_doc_id = index_to_doc_id

    def similarity_search_with_score_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """
        Return docs most similar to query.

        Args:
        ----
            embedding: Embedding vector to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            kwargs: kwargs to be passed to similarity search. Can include:
                score_threshold: Optional, a floating point value between 0 to 1 to
                    filter the resulting set of retrieved docs

        Returns:
        -------
            List of documents most similar to the query text and L2 distance
            in float for each. Lower score represents more similarity.
        """
        vector = np.array([embedding], dtype=np.float32)
        scores, indices = self.index.search(vector, k)
        docs = []
        for j, i in enumerate(indices[0]):
            if i == -1:
                # This happens when not enough docs are returned.
                continue
            _id = self.index_to_doc_id[str(i)]
            doc = self.docstore.search(_id)
            if not isinstance(doc, Document):
                raise ValueError(f"Could not find document for id {_id}, got {doc}")
            docs.append((doc, scores[0][j]))

        score_threshold = kwargs.get("score_threshold")
        if score_threshold is not None:
            docs = [
                (doc, similarity)
                for doc, similarity in docs
                if similarity > score_threshold
            ]
        return docs[:k]

    def similarity_search_with_score(self, query: str, k: int = 8, **kwargs: Any) -> List[Tuple[Document, float]]:
        """
        Return docs most similar to query.

        Args:
        ----
            query: Text to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.

        Returns:
        -------
            List of documents most similar to the query text with
            L2 distance in float. Lower score represents more similarity.
        """
        embedding = self.query_embed(query)
        docs = self.similarity_search_with_score_by_vector(embedding, k, **kwargs)
        return docs

    def similarity_search_by_vector(self, embedding: List[float], k: int = 8, **kwargs) -> List[Document]:
        """
        Return docs most similar to embedding vector.

        Args:
        ----
            embedding: Embedding to look up documents similar to.
            k: Number of Documents to return.

        Returns:
        -------
            List of Documents most similar to the embedding.
        """
        docs_and_scores = self.similarity_search_with_score_by_vector(embedding, k, **kwargs)
        return [doc for doc, _ in docs_and_scores]

    def similarity_search(self, query: str, k: int = 8, **kwargs) -> List[Document]:
        """
        Return docs most similar to query.

        Args:
        ----
            query: Text to look up documents similar to.
            k: Number of Documents to return.

        Returns:
        -------
            List of Documents most similar to the query.
        """
        docs_and_scores = self.similarity_search_with_score(query, k, **kwargs)
        return [doc for doc, _ in docs_and_scores]

    def save(self, output_path: Union[str, Path]):
        """Write index and docstore to output_path."""
        output_path_obj = Path(output_path)
        output_path_obj.mkdir(exist_ok=True, parents=True)

        faiss = import_faiss_or_so_help_me()
        faiss.write_index(self.index, str(output_path_obj / "index.faiss"))

        self.docstore.save(str(output_path_obj / "docstore"))

        with (output_path_obj / "index_to_doc_id.json").open("w") as f:
            json.dump(self.index_to_doc_id, f)

    def save_local(self, output_path: str):
        """Same as save, alias to match langchain.vectorstores.FAISS."""
        return self.save(output_path)

    @classmethod
    def load(cls, input_path: str, query_embed: Callable[[str], List[float]]) -> "FaissAndDocStore":
        """Read index and docstore from input_path."""
        import tempfile

        from fsspec.core import url_to_fs

        logger.info(f"Loading FaissAndDocStore from: {input_path}")
        fs, uri = url_to_fs(input_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            fs.download(f"{uri.rstrip('/')}/index.faiss", str(tmpdir))
            faiss = import_faiss_or_so_help_me()
            index = faiss.read_index(f"{tmpdir.rstrip('/')}/index.faiss")

        with fs.open(f"{uri.rstrip('/')}/index_to_doc_id.json", "r") as f:
            index_to_doc_id = json.load(f)

        docstore = FileBasedDocstore.load(f"{input_path.rstrip('/')}/docstore")

        return cls(query_embed, index, docstore, index_to_doc_id)
