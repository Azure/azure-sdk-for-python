import logging
from pathlib import Path

import pytest
from azure.ai.generative.index._mlindex import MLIndex

logger = logging.getLogger(__name__)

@pytest.mark.skip(reason="couldn't connect to huggingface error")
@pytest.mark.parametrize("sub_dir", [
    "langchain_faiss",
    "azureml_rag_faiss"
])
def test_load_faiss(test_data_dir: Path, sub_dir: str):
    local_faiss_mlindex = (test_data_dir / "faiss_mlindex" / sub_dir).resolve()
    logger.info(local_faiss_mlindex)

    mlindex = MLIndex(str(local_faiss_mlindex))

    assert mlindex.index_config["kind"] == "faiss"
    assert mlindex.embeddings_config["kind"] == "hugging_face"

    langchain_retriever = mlindex.as_langchain_retriever()

    docs = langchain_retriever.get_relevant_documents("SDK v2")
    assert len(docs) == 4
    logger.info(docs)
    assert docs[0].metadata["source"]["filename"] == "tutorials_README.md"