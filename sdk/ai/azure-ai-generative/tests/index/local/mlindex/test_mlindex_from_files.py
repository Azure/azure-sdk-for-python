import logging

from azure.ai.generative.index import MLIndex

logger = logging.getLogger(__name__)


def test_local_docs_to_aoai_mlindex(aoai_connection, acs_connection, test_data_dir):
    output_path = test_data_dir / "local_mlindex" / "incremental_many_docs_acs_aoai_index"

    # Process data into FAISS Index using HuggingFace embeddings
    generated_mlindex = MLIndex.from_files(
        source_uri=test_data_dir / "documents" / "incremental_many_docs" / "first_run",
        source_glob="**/*",
        chunk_size=200,
        embeddings_model="azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002",
        embeddings_connection=aoai_connection,
        embeddings_container="./.embeddings_cache/incremental_many_docs_aoai_acs",
        index_type="acs",
        index_connection=acs_connection,
        index_config={
            "index_name": "incremental_many_docs_aoai_acs"
        },
        output_path=output_path
    )

    loaded_mlindex = MLIndex(output_path)

    # Query documents, use with inferencing framework
    # total_num_docs = generated_mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Generated Index {generated_mlindex.name} has {total_num_docs} docs.")
    generated_index = generated_mlindex.as_langchain_vectorstore()
    generated_docs = generated_index.similarity_search("Topic in my data.", k=5)

    # total_num_docs = loaded_mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Loaded Index {loaded_mlindex.name} has {total_num_docs} docs.")
    loaded_index = loaded_mlindex.as_langchain_vectorstore()
    loaded_docs = loaded_index.similarity_search("Topic in my data.", k=5)

    # Take a look at those chunked docs
    import json

    for i, gen_doc in enumerate(generated_docs):
        logger.info(f"Generated doc {i}: {json.dumps({**gen_doc.metadata}, indent=2)}")
        logger.debug(json.dumps({"content": gen_doc.page_content}, indent=2))
        logger.info(f"Loaded doc {i}: {json.dumps({**loaded_docs[i].metadata}, indent=2)}")
        logger.debug(json.dumps({"content": loaded_docs[i].page_content}, indent=2))


def test_local_docs_to_faiss_mlindex(test_data_dir):
    output_path = test_data_dir / "local_mlindex" / "incremental_many_docs_faiss_mpnet_index"

    # Process data into FAISS Index using HuggingFace embeddings
    generated_mlindex = MLIndex.from_files(
        source_uri=test_data_dir / "documents" / "incremental_many_docs" / "first_run",
        source_glob="**/*",
        chunk_size=200,
        #embeddings_model=sentence_transformers.SentenceTransformer('sentence-transformers/all-mpnet-base-v2'),
        embeddings_model="hugging_face://model/sentence-transformers/all-mpnet-base-v2",
        #embeddings_container="./.embeddings_cache/incremental_many_docs_faiss_mpnet",
        index_type="faiss",
        output_path=output_path
    )

    loaded_mlindex = MLIndex(output_path)

    # Query documents, use with inferencing framework
    # total_num_docs = generated_mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Generated Index {generated_mlindex.name} has {total_num_docs} docs.")
    generated_index = generated_mlindex.as_langchain_vectorstore()
    generated_docs = generated_index.similarity_search("Topic in my data.", k=5)

    # total_num_docs = loaded_mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Loaded Index {loaded_mlindex.name} has {total_num_docs} docs.")
    loaded_index = loaded_mlindex.as_langchain_vectorstore()
    loaded_docs = loaded_index.similarity_search("Topic in my data.", k=5)

    # Take a look at those chunked docs
    import json

    for i, gen_doc in enumerate(generated_docs):
        logger.info(f"Generated doc {i}: {json.dumps({**gen_doc.metadata}, indent=2)}")
        logger.debug(json.dumps({"content": gen_doc.page_content}, indent=2))
        logger.info(f"Loaded doc {i}: {json.dumps({**loaded_docs[i].metadata}, indent=2)}")
        logger.debug(json.dumps({"content": loaded_docs[i].page_content}, indent=2))


def test_langchain_docs_to_aoai_acs_mlindex(aoai_connection, acs_connection, test_data_dir):
    output_path = test_data_dir / "local_mlindex" / "langchain_acs_aoai_index"

    # https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/wikipedia.html
    from langchain.document_loaders import WikipediaLoader

    docs = WikipediaLoader(query="HUNTER X HUNTER", load_max_docs=10).load()
    len(docs)

    # Split docs using langchain
    from langchain.text_splitter import MarkdownTextSplitter

    split_docs = MarkdownTextSplitter.from_tiktoken_encoder(chunk_size=1024).split_documents(docs)

    # Process data into FAISS Index using HuggingFace embeddings
    generated_mlindex = MLIndex.from_documents(
        documents=split_docs,
        embeddings_model="azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002",
        embeddings_connection=aoai_connection,
        embeddings_container="./.embeddings_cache/hunter_x_hunter_aoai_acs",
        index_type="acs",
        index_connection=acs_connection,
        index_config={
            "index_name": "hunter_x_hunter_aoai_acs"
        },
        output_path=output_path,
    )

    loaded_mlindex = MLIndex(output_path)

    # Query documents, use with inferencing framework
    # total_num_docs = generated_mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Generated Index {generated_mlindex.name} has {total_num_docs} docs.")
    generated_index = generated_mlindex.as_langchain_vectorstore()
    generated_docs = generated_index.similarity_search("Topic in my data.", k=5)

    # total_num_docs = loaded_mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Loaded Index {loaded_mlindex.name} has {total_num_docs} docs.")
    loaded_index = loaded_mlindex.as_langchain_vectorstore()
    loaded_docs = loaded_index.similarity_search("Topic in my data.", k=5)

    # Take a look at those chunked docs
    import json

    for i, gen_doc in enumerate(generated_docs):
        logger.info(f"Generated doc {i}: {json.dumps({**gen_doc.metadata}, indent=2)}")
        logger.debug(json.dumps({"content": gen_doc.page_content}, indent=2))
        logger.info(f"Loaded doc {i}: {json.dumps({**loaded_docs[i].metadata}, indent=2)}")
        logger.debug(json.dumps({"content": loaded_docs[i].page_content}, indent=2))
