# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import base64
import json
import logging
import pathlib
import time
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pkg_resources
import yaml
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
)
from azure.ai.ml.entities._indexes.documents import (
    Document,
    StaticDocument,
)
from azure.ai.ml.entities._indexes.embeddings import EmbeddingsContainer
from azure.ai.ml.entities._indexes.mlindex import MLIndex
from azure.ai.ml.entities._indexes.utils.connections import (
    get_connection_by_id_v2,
    get_metadata_from_connection,
    get_target_from_connection,
    workspace_connection_to_credential,
)
from azure.ai.ml.entities._indexes.utils.logging import (
    _logger_factory,
    enable_appinsights_logging,
    enable_stdout_logging,
    get_logger,
    safe_mlflow_start_run,
    track_activity,
)
from packaging import version as pkg_version

logger = get_logger("image_embed_index_and_register")

_azure_logger = logging.getLogger("azure.core.pipeline")
_azure_logger.setLevel(logging.WARNING)


def get_field_mappings():
    field_mappings = {"filename": "filepath", "title": "description", "embedding": "image_vector"}
    return field_mappings


def read_images_into_documents(input_path: Iterator[pathlib.Path]) -> Iterator[Document]:
    metadata_files = input_path.rglob("**/*metadata*.json")
    for metadata_file in metadata_files:
        logger.info(f"==== loading metadata file {metadata_file}")
        with open(metadata_file) as f:
            data = json.load(f)
            for item in data:
                image_path = (input_path / item["image_blob_path"]).resolve()
                image_description = item["description"]
                logger.info(f"==== Reading image file {input_path}")
                with open(image_path, "rb") as im:
                    image_bytes = im.read()
                    converted_string = base64.b64encode(image_bytes)
                    base64_string = converted_string.decode()
                    image_metadata = dict()
                    image_metadata["description"] = image_description
                    image_metadata["id"] = str(uuid.uuid4())
                    image_metadata["filepath"] = item["image_blob_path"]
                    yield StaticDocument(base64_string, image_metadata)


def create_acs_index(acs_connection_id, index_name) -> SearchClient:
    acs_conn = get_connection_by_id_v2(acs_connection_id)
    search_endpoint = get_target_from_connection(acs_conn)
    acs_credentials = workspace_connection_to_credential(acs_conn)

    logger.info(f"Ensuring search index {index_name} exists")
    index_client = SearchIndexClient(endpoint=search_endpoint, credential=AzureKeyCredential(acs_credentials.key))
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, filterable=True, sortable=True, key=True),
        SearchableField(name="description", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="filepath", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="last_updated", type=SearchFieldDataType.String, filterable=True, IsSortable=True),
        SearchField(
            name="image_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            hidden=True,
            searchable=True,
            vector_search_configuration="image_vector_config",
            vector_search_dimensions=1024,
        ),
    ]
    index = SearchIndex(name=index_name, fields=fields)
    index.vector_search = _get_embedding_index_field()
    try:
        logger.info(f"Deleting the existing index {index_name}")
        index_client.delete_index(index_name)
        logger.info(f"Deleted the existing index {index_name} successfully.")
        logger.info(f"Creating the index {index_name}")
        index_client.create_index(index)
        logger.info(f"Created the index {index_name} successfully.")
    except Exception as ex:
        logger.error(f"An exception occured while creating index {index_name}. Details {ex}")
        raise

    return SearchClient(
        endpoint=search_endpoint, index_name=index_name, credential=AzureKeyCredential(acs_credentials.key)
    )


def _get_embedding_index_field():
    acs_pkg_version = pkg_resources.get_distribution("azure-search-documents").version
    current_version = pkg_version.parse(acs_pkg_version)
    if current_version >= pkg_version.parse("11.4.0b8"):
        from azure.search.documents.indexes.models import HnswVectorSearchAlgorithmConfiguration, VectorSearch

        vector_search_field = VectorSearch(
            algorithm_configurations=[
                HnswVectorSearchAlgorithmConfiguration(
                    name="image_vector_config",
                    parameters={"m": 4, "efConstruction": 400, "efSearch": 500, "metric": "cosine"},
                )
            ]
        )
    elif current_version >= pkg_version.parse("11.4.0b4"):
        from azure.search.documents.indexes.models import VectorSearch, VectorSearchAlgorithmConfiguration

        vector_search_field = VectorSearch(
            algorithm_configurations=[
                VectorSearchAlgorithmConfiguration(
                    name="image_vector_config",
                    kind="hnsw",
                    hnsw_parameters={"m": 4, "efConstruction": 400, "efSearch": 500, "metric": "cosine"},
                )
            ]
        )
    else:
        raise RuntimeError(
            f"azure-search-documents version {acs_pkg_version} is not supported when using embeddings. Please upgrade to 11.4.0b4 or later."
        )
    return vector_search_field


def image_embed_index(args, logger):
    input_path = Path(args.get("input_path"))
    florence_connection_id = args.get("embedding_connection_id")
    acs_connection_id = args.get("acs_connection_id")
    index_name = args.get("search_index_name")
    output_path = Path(args.get("output_path"))

    logger.info(f"reading florence connection parameters for connection for {florence_connection_id}")
    florence_connection_args = get_florence_connection_args_from_id(florence_connection_id)

    logger.info("reading all images...")
    image_docs = read_images_into_documents(input_path)

    embeddings = EmbeddingsContainer.from_uri(florence_connection_args["api_base"], **florence_connection_args)

    logger.info("calling florence api to embed images")
    embeddings.embed(image_docs)

    search_client = create_acs_index(acs_connection_id=acs_connection_id, index_name=index_name)

    # get MLIndex to ACS field mapping
    field_mappings = get_field_mappings()

    logger.info(f"populating the index {index_name}")
    for doc_id, doc in embeddings._document_embeddings.items():
        image_doc = dict()
        image_doc["id"] = doc_id
        image_doc[field_mappings["title"]] = doc.metadata["description"]
        image_doc[field_mappings["filename"]] = doc.metadata["filepath"]
        image_doc["last_updated"] = str(datetime.now())
        # image_vector
        image_doc[field_mappings["embedding"]] = doc.get_embeddings()
        logger.info(f'uploading image {image_doc["filepath"]}')
        search_client.upload_documents([image_doc])
        logger.info(f'uploaded image {image_doc["filepath"]}')

    logger.info(f"all images uploaded to the index {index_name}")
    search_client.close()

    logger.info("Writing MLIndex yaml")
    mlindex_config = get_ml_index_config(
        acs_connection_id=acs_connection_id, index_name=index_name, embeddings=embeddings
    )

    logger.info(f"Saving MLIndex to the path: {output_path}/MLIndex")
    if output_path is not None:
        output = Path(output_path)
        output.mkdir(parents=True, exist_ok=True)
        with open(output / "MLIndex", "w") as f:
            yaml.dump(mlindex_config, f)

    mlindex = MLIndex(uri=output_path, mlindex_config=mlindex_config)
    logger.info("Image embedding task successfuly completed")
    return mlindex


def get_florence_connection_args_from_id(florence_conn_id: str):
    florence_conn = get_connection_by_id_v2(florence_conn_id)
    florence_credentials = workspace_connection_to_credential(florence_conn)
    florence_metadata = get_metadata_from_connection(florence_conn)

    florence_connection_args = {}
    florence_connection_args["is_florence"] = True
    florence_connection_args["api_key"] = florence_credentials.key
    florence_connection_args["api-version"] = florence_metadata["api-version"]
    florence_connection_args["model-version"] = florence_metadata["model-version"]
    florence_connection_args["connection"] = {"id": florence_conn["id"]}
    florence_connection_args["api_base"] = (
        f"{florence_metadata['endpoint']}?api-version={florence_metadata['api-version']}&model-version={florence_metadata['model-version']}"
    )

    return florence_connection_args


def get_ml_index_config(acs_connection_id: str, index_name: str, embeddings: EmbeddingsContainer) -> dict:
    field_mappings = get_field_mappings()
    acs_conn = get_connection_by_id_v2(acs_connection_id)

    acs_connection_args = {}
    acs_connection_args["connection_type"] = "workspace_connection"
    acs_connection_args["connection"] = {"id": acs_connection_id}
    mlindex_config = {"embeddings": embeddings.get_metadata()}
    mlindex_config["index"] = {
        "kind": "acs",
        "engine": "azure-sdk",
        "index": index_name,
        "api_version": acs_conn.metadata["ApiVersion"],
        "field_mapping": field_mappings,
        "semantic_configuration_name": "azureml-default",
    }
    mlindex_config["index"] = {**mlindex_config["index"], **acs_connection_args}
    mlindex_config["index"]["endpoint"] = acs_conn.target
    return mlindex_config


def main_wrapper(args, logger):
    with track_activity(logger, "image_embed_index") as activity_logger, safe_mlflow_start_run(logger=logger):
        try:
            image_embed_index(args, logger)
        except Exception:
            activity_logger.error(
                f"image_embed_index failed with exception: {traceback.format_exc()}"
            )  # activity_logger doesn't log traceback
            raise


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--input_path", type=str, required=True)
    parser.add_argument("--embedding_connection_id", type=str, required=True)
    parser.add_argument("--acs_connection_id", type=str, required=True)
    parser.add_argument("--search_index_name", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument(
        "--verbosity",
        type=int,
        default=1,
        help="Defaults to 1, which will log aggregate information about documents and IDs of deleted documents. 2 will log all document_ids as they are processed.",
    )
    args = parser.parse_args()

    print("\n".join(f"{k}={v}" for k, v in vars(args).items()))

    enable_stdout_logging()
    enable_appinsights_logging()

    try:
        main_wrapper(vars(args), logger)
    finally:
        if _logger_factory.appinsights:
            _logger_factory.appinsights.flush()
            time.sleep(5)
