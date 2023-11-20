# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

class DataIndexComponentUri(object):
    DATA_INDEX_COG_SEARCH = "azureml://registries/azureml/components/llm_ingest_dataset_to_acs_basic/labels/default"
    DATA_INDEX_FAISS = "azureml://registries/azureml/components/llm_ingest_dataset_to_faiss_basic/labels/default"

    @staticmethod
    def with_registry(component_uri: str, registry_name: str) -> str:
        return component_uri.replace("azureml://registries/azureml", f"azureml://registries/{registry_name}")


class LLMRAGComponentUri(object):
    LLM_RAG_CRACK_AND_CHUNK = "azureml://registries/azureml/components/llm_rag_crack_and_chunk/labels/default"
    LLM_RAG_GENERATE_EMBEDDINGS = "azureml://registries/azureml/components/llm_rag_generate_embeddings/labels/default"
    LLM_RAG_CRACK_AND_CHUNK_AND_EMBED = (
        "azureml://registries/azureml/components/llm_rag_crack_and_chunk_and_embed/labels/default"
    )
    LLM_RAG_UPDATE_ACS_INDEX = "azureml://registries/azureml/components/llm_rag_update_acs_index/labels/default"
    LLM_RAG_CREATE_FAISS_INDEX = "azureml://registries/azureml/components/llm_rag_create_faiss_index/labels/default"
    LLM_RAG_REGISTER_MLINDEX_ASSET = (
        "azureml://registries/azureml/components/llm_rag_register_mlindex_asset/labels/default"
    )
    LLM_RAG_VALIDATE_DEPLOYMENTS = "azureml://registries/azureml/components/llm_rag_validate_deployments/labels/default"
    LLM_RAG_CREATE_PROMPTFLOW = "azureml://registries/azureml/components/llm_rag_create_promptflow/labels/default"
