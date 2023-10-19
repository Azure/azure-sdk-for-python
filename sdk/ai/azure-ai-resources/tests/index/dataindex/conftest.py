import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def _dataindex_custom_components(component_source, crack_and_chunk_component_local, generate_embeddings_component_local, crack_and_chunk_and_embed_component_local, update_acs_index_component_local, create_faiss_index_component_local, register_mlindex_asset_component_local): # TODO: Use registry name arg
    # Use local components for testing
    from azureml.rag._dataindex.constants._component import LLMRAGComponentUri

    if component_source == "dev":
        logger.info("DataIndex components using dev fixtures")

        LLMRAGComponentUri.LLM_RAG_CRACK_AND_CHUNK = crack_and_chunk_component_local
        LLMRAGComponentUri.LLM_RAG_GENERATE_EMBEDDINGS = generate_embeddings_component_local
        LLMRAGComponentUri.LLM_RAG_CRACK_AND_CHUNK_AND_EMBED = crack_and_chunk_and_embed_component_local
        LLMRAGComponentUri.LLM_RAG_UPDATE_ACS_INDEX = update_acs_index_component_local
        LLMRAGComponentUri.LLM_RAG_CREATE_FAISS_INDEX = create_faiss_index_component_local
        LLMRAGComponentUri.LLM_RAG_REGISTER_MLINDEX_ASSET = register_mlindex_asset_component_local
    elif component_source.startswith("file://"):
        file_path = component_source.split("file://")[1]

        logger.info(f"DataIndex components using local path: {file_path}")

        LLMRAGComponentUri.LLM_RAG_CRACK_AND_CHUNK = f"{file_path}/crack_and_chunk/spec.yaml"
        LLMRAGComponentUri.LLM_RAG_GENERATE_EMBEDDINGS = f"{file_path}/generate_embedding/spec.yamls"
        LLMRAGComponentUri.LLM_RAG_CRACK_AND_CHUNK_AND_EMBED = f"{file_path}/crack_and_chunk_and_embed/spec.yaml"
        LLMRAGComponentUri.LLM_RAG_UPDATE_ACS_INDEX = f"{file_path}/update_acs_index/spec.yaml"
        LLMRAGComponentUri.LLM_RAG_CREATE_FAISS_INDEX = f"{file_path}/create_faiss_index/spec.yaml"
        LLMRAGComponentUri.LLM_RAG_REGISTER_MLINDEX_ASSET = f"{file_path}/register_mlindex_asset/spec.yaml"
    elif component_source.startswith("registry"):
        registry = component_source.split(":")[1]

        logger.info(f"DataIndex components using registry: {registry}")

        LLMRAGComponentUri.LLM_RAG_CRACK_AND_CHUNK = f"azureml://registries/{registry}/components/llm_rag_crack_and_chunk/labels/default"
        LLMRAGComponentUri.LLM_RAG_GENERATE_EMBEDDINGS = f"azureml://registries/{registry}/components/llm_rag_generate_embeddings/labels/default"
        LLMRAGComponentUri.LLM_RAG_CRACK_AND_CHUNK_AND_EMBED = f"azureml://registries/{registry}/components/llm_rag_crack_and_chunk_and_embed/labels/default"
        LLMRAGComponentUri.LLM_RAG_UPDATE_ACS_INDEX = f"azureml://registries/{registry}/components/llm_rag_update_acs_index/labels/default"
        LLMRAGComponentUri.LLM_RAG_CREATE_FAISS_INDEX = f"azureml://registries/{registry}/components/llm_rag_create_faiss_index/labels/default"
        LLMRAGComponentUri.LLM_RAG_REGISTER_MLINDEX_ASSET = f"azureml://registries/{registry}/components/llm_rag_register_mlindex_asset/labels/default"
