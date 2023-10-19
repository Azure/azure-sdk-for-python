import base64
import json
import logging
import shutil
from pathlib import Path

import azure
from azureml.rag.tasks.crack_and_chunk_and_embed_and_index import crack_and_chunk_and_embed_and_index
from azureml.rag.utils.logging import ActivityLoggerAdapter

logger = logging.getLogger(__name__)


def test_local_docs_to_aoai_mlindex(aoai_connection, acs_connection, test_data_dir, acs_temp_index):
    test_set = "incremental_many_docs"
    output_path = test_data_dir / "crack_and_chunk_and_embed_and_index" / f"{test_set}_open_ai_acs_index"

    embeddings_cache = f"./.embeddings_cache/{test_set}_aoai_acs"
    shutil.rmtree(Path(embeddings_cache), ignore_errors=True)
    #embeddings_model = "hugging_face://model/sentence-transformers/all-mpnet-base-v2"
    embeddings_model = "azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002"

    generated_mlindex = crack_and_chunk_and_embed_and_index(
        logger,
        ActivityLoggerAdapter(logger, {}),
        source_uri=test_data_dir / "documents" / test_set / "first_run",
        source_glob="**/*",
        chunk_size=200,
        embeddings_model=embeddings_model,
        embeddings_connection=aoai_connection["id"],
        embeddings_cache=embeddings_cache,
        index_type="acs",
        index_connection=acs_connection["id"],
        index_config={
            "index_name": acs_temp_index,
            # TODO: Indicates that documents found in supplied embeddings_cache will be considered to be already indexed.
            # So when pushing docs to index referenced docs will be skipped.
            "sync_index": True
        },
        output_path=output_path
    )

    generated_index = generated_mlindex.as_langchain_vectorstore()
    generated_docs = generated_index.similarity_search("What is Baby Shark?", k=5)

    for i, gen_doc in enumerate(generated_docs):
        logger.info(f"Generated doc {i}: {json.dumps({**gen_doc.metadata}, indent=2)}")
        logger.info(json.dumps({"content": gen_doc.page_content}, indent=2))

    # Incremental update
    generated_mlindex = crack_and_chunk_and_embed_and_index(
        logger,
        ActivityLoggerAdapter(logger, {}),
        source_uri=test_data_dir / "documents" / test_set / "second_run",
        source_glob="**/*",
        chunk_size=200,
        embeddings_model=embeddings_model,
        embeddings_connection=aoai_connection["id"],
        embeddings_cache=embeddings_cache,
        index_type="acs",
        index_connection=acs_connection["id"],
        index_config={
            "index_name": acs_temp_index,
            # TODO: Indicates that documents found in supplied embeddings_cache will be considered to be already indexed.
            # So when pushing docs to index referenced docs will be skipped.
            "sync_index": True
        },
        output_path=output_path
    )

    generated_index = generated_mlindex.as_langchain_vectorstore()
    generated_docs = generated_index.similarity_search("What is Baby Shark?", k=5)

    for i, gen_doc in enumerate(generated_docs):
        logger.info(f"Generated doc {i}: {json.dumps({**gen_doc.metadata}, indent=2)}")
        logger.info(json.dumps({"content": gen_doc.page_content}, indent=2))

        # Incremental update
    generated_mlindex = crack_and_chunk_and_embed_and_index(
        logger,
        ActivityLoggerAdapter(logger, {}),
        source_uri=test_data_dir / "documents" / test_set / "third_run",
        source_glob="**/*",
        chunk_size=200,
        embeddings_model=embeddings_model,
        embeddings_connection=aoai_connection["id"],
        embeddings_cache=embeddings_cache,
        index_type="acs",
        index_connection=acs_connection["id"],
        index_config={
            "index_name": acs_temp_index,
            # TODO: Indicates that documents found in supplied embeddings_cache will be considered to be already indexed.
            # So when pushing docs to index referenced docs will be skipped.
            "sync_index": True
        },
        output_path=output_path
    )

    generated_index = generated_mlindex.as_langchain_vectorstore()
    generated_docs = generated_index.similarity_search("What is Baby Shark?", k=5)

    for i, gen_doc in enumerate(generated_docs):
        logger.info(f"Generated doc {i}: {json.dumps({**gen_doc.metadata}, indent=2)}")
        logger.info(json.dumps({"content": gen_doc.page_content}, indent=2))

    # Check second_run doc removed after third_run
    new_baby_shark_doc_id = base64.urlsafe_b64encode("plain_text/baby_shark_draft.md6".encode("utf-8")).decode("utf-8")
    old_baby_shark_doc_id = base64.urlsafe_b64encode("plain_text/in_progress/baby_shark_draft.md0".encode("utf-8")).decode("utf-8")
    search_client = generated_mlindex.as_native_index_client()
    doc = search_client.get_document(key=new_baby_shark_doc_id, selected_fields=[
        # Exclude 'content_vector_open_ai' cause it's just a bunch of floats and not useful to look at.
        "id", "content", "sourcepage", "sourcefile", "title", "meta_json_string"
    ])
    logger.info(f"New baby shark doc: {json.dumps(doc, indent=2)}")
    old_doc = None
    try:
        old_doc = search_client.get_document(key=old_baby_shark_doc_id)
    except azure.core.exceptions.ResourceNotFoundError:
        logger.info("Old baby shark doc not found, as expected")
    except Exception:
        raise

    if old_doc is not None:
        raise RuntimeError(f"Found old baby shark doc when it should have been deleted: {json.dumps(old_doc, indent=2)}")
