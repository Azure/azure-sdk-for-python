import io
import logging
from contextlib import redirect_stdout

from azure.ai.generative import AIClient
from azure.ai.generative.operations._index_data_source import ACSSource, GitSource, IndexDataSource, LocalSource
from azure.ai.generative.operations._acs_output_config import ACSOutputConfig

logger = logging.getLogger(__name__)


def wait_for_job(ml_client, job, stream_run_output=False):
    if stream_run_output:
        ml_client.jobs.stream(job.name)
    else:
        logger.info("Redirecting stdout while streaming Job output.")
        # TODO: Write to file?
        job_output = io.StringIO()
        with redirect_stdout(job_output):
            ml_client.jobs.stream(job.name)
        logger.info("Job finished streaming.")


def test_rust_book_git_to_acs_build_on_cloud(ai_client, ml_client, test_data_dir, aoai_connection, acs_connection, acs_temp_index, experiment_name, stream_run_output):
    git_config = GitSource(git_url="https://github.com/rust-lang/book.git",
                                            git_branch_name="main",
                                            git_connection_id="")
    
    index_output_config = ACSOutputConfig(
        acs_index_name=acs_temp_index,
        acs_connection_id=acs_connection.id,
    )

    index_job = ai_client.build_ml_index_on_cloud(
        output_index_name=acs_temp_index,
        vector_store="acs",
        embeddings_model="text-embedding-ada-002",
        aoai_connection_id=aoai_connection.id,
        data_source_url="https://github.com/rust-lang/book/blob/main",
        input_source=git_config,
        acs_config=index_output_config
    )

    # Wait for it to finish
    wait_for_job(ml_client, index_job, stream_run_output)

    # Check the created asset, it is a folder on storage containing an MLIndex yaml file
    mlindex_docs_index_asset = ml_client.data.get(acs_temp_index, label="latest")

    # Try it out with langchain by loading the MLIndex asset using the azure-ai-generative SDK
    from azure.ai.generative.index import MLIndex

    mlindex = MLIndex(mlindex_docs_index_asset)

    # total_num_docs = mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Index {mlindex.name} has {total_num_docs} docs.")
    index = mlindex.as_langchain_vectorstore()

    docs = index.similarity_search("Why are Rust enums so cool?", k=5)

    # Take a look at those chunked docs
    import json

    for doc in docs:
        logger.info(json.dumps({"content": doc.page_content, **doc.metadata}, indent=2))


def test_local_files_to_acs_build_on_cloud(ai_client, ml_client, test_data_dir, aoai_connection, acs_connection, acs_temp_index, experiment_name, stream_run_output):
    local_config = LocalSource(input_data=test_data_dir / "documents" / "incremental_many_docs" / "first_run")

    index_output_config = ACSOutputConfig(
        acs_index_name=acs_temp_index,
        acs_connection_id=acs_connection.id,
    )

    index_job = ai_client.build_ml_index_on_cloud(
        output_index_name=acs_temp_index,
        vector_store="acs",
        embeddings_model="text-embedding-ada-002",
        aoai_connection_id=aoai_connection.id,
        data_source_url="https://github.com/rust-lang/book/blob/main",
        input_source=local_config,
        acs_config=index_output_config
    )

    # Wait for it to finish
    wait_for_job(ml_client, index_job, stream_run_output)

    # Check the created asset, it is a folder on storage containing an MLIndex yaml file
    mlindex_docs_index_asset = ml_client.data.get(acs_temp_index, label="latest")

    # Try it out with langchain by loading the MLIndex asset using the azure-ai-generative SDK
    from azure.ai.generative.index import MLIndex

    mlindex = MLIndex(mlindex_docs_index_asset)

    # total_num_docs = mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Index {mlindex.name} has {total_num_docs} docs.")
    index = mlindex.as_langchain_vectorstore()

    docs = index.similarity_search("Why are Rust enums so cool?", k=5)

    # Take a look at those chunked docs
    import json

    for doc in docs:
        logger.info(json.dumps({"content": doc.page_content, **doc.metadata}, indent=2))


def test_acs_to_mlindex_build_on_cloud(ai_client, ml_client, test_data_dir, aoai_connection, acs_connection, acs_temp_index, experiment_name, stream_run_output):
    local_config = LocalSource(input_data=test_data_dir / "documents" / "incremental_many_docs" / "first_run")

    index_output_config = ACSOutputConfig(
        acs_index_name=acs_temp_index,
        acs_connection_id=acs_connection.id,
    )

    index_job = ai_client.build_ml_index_on_cloud(
        output_index_name=acs_temp_index,
        vector_store="acs",
        embeddings_model="text-embedding-ada-002",
        aoai_connection_id=aoai_connection.id,
        data_source_url="https://github.com/rust-lang/book/blob/main",
        input_source=local_config,
        acs_config=index_output_config
    )

    # Wait for it to finish
    wait_for_job(ml_client, index_job, stream_run_output)

    # Check the created asset, it is a folder on storage containing an MLIndex yaml file
    mlindex_docs_index_asset = ml_client.data.get(acs_temp_index, label="latest")

    # Try it out with langchain by loading the MLIndex asset using the azure-ai-generative SDK
    from azure.ai.generative.index import MLIndex

    mlindex = MLIndex(mlindex_docs_index_asset)

    # total_num_docs = mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Index {mlindex.name} has {total_num_docs} docs.")
    index = mlindex.as_langchain_vectorstore()

    docs = index.similarity_search("Why are Rust enums so cool?", k=5)

    # Take a look at those chunked docs
    import json

    for doc in docs:
        logger.info(json.dumps({"content": doc.page_content, **doc.metadata}, indent=2))


    acs_source = ACSSource(
        acs_index_name=acs_temp_index,
        acs_connection_id=acs_connection.id,
        acs_content_key="content",
        acs_embedding_key="content_vector_open_ai",
        acs_title_key="title",
        acs_metadata_key="meta_json_string",
    )

    index_output_config = ACSOutputConfig(
        acs_index_name=acs_temp_index,
        acs_connection_id=acs_connection.id,
    )

    index = ai_client.build_ml_index_on_cloud(
        output_index_name=acs_temp_index,
        vector_store="acs",
        embeddings_model="text-embedding-ada-002",
        aoai_connection_id=aoai_connection.id,
        input_source=acs_source,
        acs_config=index_output_config
    )

    # # Check the created asset, it is a folder on storage containing an MLIndex yaml file
    # mlindex_docs_index_asset = ml_client.data.get(acs_temp_index, label="latest")

    # # Try it out with langchain by loading the MLIndex asset using the azure-ai-generative SDK
    # from azure.ai.generative.index import MLIndex

    # mlindex = MLIndex(mlindex_docs_index_asset)

    # # total_num_docs = mlindex.as_native_index_client().get_document_count()
    # # logger.info(f"Index {mlindex.name} has {total_num_docs} docs.")
    # index = mlindex.as_langchain_vectorstore()

    docs = index.query("Why are Rust enums so cool?")

    # Take a look at those chunked docs
    import json

    for doc in docs:
        logger.info(json.dumps({"content": doc.page_content, **doc.metadata}, indent=2))


def test_onelake_s3_to_acs_build_on_cloud(ai_client, ml_client, aoai_connection, acs_connection, acs_temp_index, experiment_name, stream_run_output):
    from azure.ai.ml import UserIdentityConfiguration

    # NOTE: You will need access to this specific resource to run this test, replace it with a Onelake resource you have access to
    remote_source = "abfss://9aa7b19e-c117-4a74-8654-cf1559ba9f4f@msit-onelake.dfs.fabric.microsoft.com/1606ee55-ec68-4658-8d6b-58bf8dd26636/Files/lupickup-test-s3"

    index_output_config = ACSOutputConfig(
        acs_index_name=acs_temp_index,
        acs_connection_id=acs_connection.id,
    )

    index_job = ai_client.build_ml_index_on_cloud(
        output_index_name=acs_temp_index,
        vector_store="acs",
        embeddings_model="text-embedding-ada-002",
        aoai_connection_id=aoai_connection.id,
        data_source_url="s3://lupickup-test",
        input_source=remote_source,
        acs_config=index_output_config,
        identity=UserIdentityConfiguration(),
    )

    # Wait for it to finish
    wait_for_job(ml_client, index_job, stream_run_output)

    # Check the created asset, it is a folder on storage containing an MLIndex yaml file
    mlindex_docs_index_asset = ml_client.data.get(acs_temp_index, label="latest")

    # Try it out with langchain by loading the MLIndex asset using the azure-ai-generative SDK
    from azure.ai.generative.index import MLIndex

    mlindex = MLIndex(mlindex_docs_index_asset)

    # total_num_docs = mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Index {mlindex.name} has {total_num_docs} docs.")
    index = mlindex.as_langchain_vectorstore()

    docs = index.similarity_search("How did the initial paper on RAG define it?", k=5)

    # Take a look at those chunked docs
    import json

    for doc in docs:
        logger.info(json.dumps({"content": doc.page_content, **doc.metadata}, indent=2))
