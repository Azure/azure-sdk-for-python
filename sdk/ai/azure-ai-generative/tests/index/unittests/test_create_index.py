import logging
from pathlib import Path

import pytest
from azure.ai.generative.index._embeddings import EmbeddingsContainer
from azure.ai.resources._index._indexes.faiss import FaissAndDocStore
from azure.ai.generative.index._mlindex import MLIndex
from langchain.vectorstores import FAISS

logger = logging.getLogger(__name__)

@pytest.mark.skip(reason="couldn't connect to huggingface error")
@pytest.mark.parametrize("faiss_engine_and_folder", [
    ("langchain.vectorstores.FAISS", "langchain_faiss"),
    ("azure.ai.resources._index._indexes.faiss.FaissAndDocStore", "azureml_rag_faiss")
])
def test_create_faiss(test_data_dir: Path, faiss_engine_and_folder: str):
    embedded_documents = (test_data_dir / "embedded_documents" / "hugging_face").resolve()
    logger.info(embedded_documents)
    engine, index_dir = faiss_engine_and_folder
    faiss_index_dir =  test_data_dir / "faiss_mlindex" / index_dir

    emb = EmbeddingsContainer.load("second_run", str(embedded_documents))
    emb.write_as_faiss_mlindex(faiss_index_dir, engine=engine)
    mlindex = MLIndex(str(faiss_index_dir))

    assert mlindex.index_config["kind"] == "faiss"
    assert mlindex.embeddings_config["kind"] == "hugging_face"

    embeddings = mlindex.get_langchain_embeddings()

    if engine == "langchain.vectorstores.FAISS":
        faiss = FAISS.load_local(str(faiss_index_dir), embeddings.embed_query)
    elif engine == "azure.ai.resources._index._indexes.faiss.FaissAndDocStore":
        faiss = FaissAndDocStore.load(str(faiss_index_dir), embeddings.embed_query)
    else:
        raise ValueError(f"Unknown engine: {engine}")

    docs = faiss.similarity_search("SDK v2", k=1)

    assert len(docs) == 1
    assert docs[0].metadata["source"]["filename"] == "tutorials_README.md"

    index = mlindex.as_langchain_vectorstore()
    docs = index.similarity_search("SDK v2", k=1)

    assert len(docs) == 1
    assert docs[0].metadata["source"]["filename"] == "tutorials_README.md"
