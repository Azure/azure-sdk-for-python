# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Index stores for uploading and deleting documents."""

import base64
import json
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, List, Optional

from azure.core import CaseInsensitiveEnumMeta
from azure.ai.ml.entities._indexes.utils.logging import get_logger

if TYPE_CHECKING:
    from azure.search.documents import SearchClient
    from pinecone import Index
    from pymilvus import MilvusClient
    from pymongo.collection import Collection


INDEX_DELETE_FAILURE_MESSAGE_PREFIX = "Failed to delete"
INDEX_UPLOAD_FAILURE_MESSAGE_PREFIX = "Failed to upload"


class IndexStoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """IndexStoreType."""

    ACS = "ACS"
    PINECONE = "Pinecone"
    MILVUS = "Milvus"
    AZURE_COSMOS_MONGO_VCORE = "AzureCosmosMongoVcore"


logger = get_logger(__name__)


class IndexStore(ABC):
    """
    An index store used for uploading and deleting documents.

    This class should not be instantiated directly. Instead, use one of its subclasses.
    """

    def __init__(self, type: IndexStoreType):
        """Initialize the IndexStore."""
        self._type = type

    @property
    def type(self) -> IndexStoreType:
        """The type of the index."""
        return self._type

    @abstractmethod
    def delete_documents(self, documents: List[Any]):
        """
        Delete documents from the index.

        Raises
        ------
            `RuntimeError` if all documents are not deleted from the index.

        """
        pass

    @abstractmethod
    def upload_documents(self, documents: List[Any]):
        """
        Upload documents to the index.

        Raises
        ------
            `RuntimeError` if all documents are not uploaded to the index.

        """
        pass

    @abstractmethod
    def create_delete_payload_from_document_id(self, document_id: str) -> Any:
        """Given a document ID, construct a payload used to delete the corresponding document from the index."""
        pass

    @abstractmethod
    def create_upload_payload_from_embedded_document(
        self,
        field_mappings: dict,
        document_id: str,
        document_source_info: dict = {},
        document_data: Optional[str] = None,
        document_embeddings: Optional[List[float]] = None,
        document_metadata: Optional[dict] = None,
    ) -> Any:
        """Given info about an EmbeddedDocument, construct a payload used to upload the document to the index."""
        pass


class AzureCognitiveSearchStore(IndexStore):
    """An Azure Cognitive Search index store used for uploading and deleting documents."""

    def __init__(self, search_client: "SearchClient", include_embeddings: bool = True):
        """Initialize the AzureCognitiveSearchStore."""
        super().__init__(IndexStoreType.ACS)
        self._search_client = search_client
        self._include_embeddings = include_embeddings

    def delete_documents(self, documents: List[Any]):
        """
        Delete documents from the index.

        Raises
        ------
            `RuntimeError` if all documents are not deleted from the index.

        """
        start_time = time.time()
        results = self._search_client.delete_documents(documents)
        logger.info(
            f"[{self.__class__.__name__}][{self.delete_documents.__name__}] First delete result: {vars(results[0])}"
        )

        failed = self._process_results(results, start_time, self.delete_documents.__name__)

        if len(failed) > 0:
            logger.info(
                f"[{self.__class__.__name__}][{self.delete_documents.__name__}] Retrying {len(failed)} documents"
            )
            failed_ids = [fail["key"] for fail in failed]
            results = self._search_client.delete_documents([doc for doc in documents if doc["id"] in failed_ids])
            failed = self._process_results(results, start_time, self.delete_documents.__name__)

        if len(failed) > 0:
            raise RuntimeError(f"{INDEX_DELETE_FAILURE_MESSAGE_PREFIX} {len(failed)} documents")

    def upload_documents(self, documents: List[Any]):
        """
        Upload documents to the index.

        Raises
        ------
            `RuntimeError` if all documents are not uploaded to the index.

        """
        start_time = time.time()
        results = self._search_client.upload_documents(documents)
        failed = self._process_results(results, start_time, self.upload_documents.__name__)

        if len(failed) > 0:
            logger.info(
                f"[{self.__class__.__name__}][{self.upload_documents.__name__}] Retrying {len(failed)} documents"
            )
            failed_ids = [fail["key"] for fail in failed]
            results = self._search_client.upload_documents([doc for doc in documents if doc["id"] in failed_ids])
            failed = self._process_results(results, start_time, self.upload_documents.__name__)

        if len(failed) > 0:
            raise RuntimeError(f"{INDEX_UPLOAD_FAILURE_MESSAGE_PREFIX} {len(failed)} documents")

    def create_delete_payload_from_document_id(self, document_id: str) -> Any:
        """Given a document ID, construct a payload used to delete the corresponding document from the index."""
        return {"id": base64.urlsafe_b64encode(document_id.encode("utf-8")).decode("utf-8")}

    def create_upload_payload_from_embedded_document(
        self,
        field_mappings: dict,
        document_id: str,
        document_source_info: dict = {},
        document_data: Optional[str] = None,
        document_embeddings: Optional[List[float]] = None,
        document_metadata: Optional[dict] = None,
    ) -> Any:
        """Given info about an EmbeddedDocument, construct a payload used to upload the document to the index."""
        if (
            document_data is None
            or (document_embeddings is None and self._include_embeddings)
            or document_metadata is None
        ):
            raise ValueError("One or more of document data, embeddings, metadata is missing")

        doc_source = document_source_info

        doc_id_encoded = base64.urlsafe_b64encode(document_id.encode("utf-8")).decode("utf-8")
        acs_doc = {
            "@search.action": "mergeOrUpload",
            "id": doc_id_encoded,
            field_mappings["content"]: document_data,
        }
        if "url" in field_mappings:
            acs_doc[field_mappings["url"]] = doc_source.get("url", "")
        if "filename" in field_mappings:
            acs_doc[field_mappings["filename"]] = doc_source.get("filename", "")
        if "title" in field_mappings:
            acs_doc[field_mappings["title"]] = doc_source.get("title", document_metadata.get("title", ""))
        if "metadata" in field_mappings:
            acs_doc[field_mappings["metadata"]] = json.dumps(document_metadata)

        if self._include_embeddings:
            acs_doc[field_mappings["embedding"]] = document_embeddings

        return acs_doc

    def _process_results(self, results, start_time, operation_name):
        succeeded = []
        failed = []
        for r in results:
            if isinstance(r, dict):
                if r["status"] is False:
                    failed.append(r)
                else:
                    succeeded.append(r)
            else:
                if r.succeeded:
                    succeeded.append(r)
                else:
                    failed.append(r)

        duration = time.time() - start_time
        logger.info(
            f"[{self.__class__.__name__}][{operation_name}] Processed {len(succeeded)} documents in {duration:.4f} seconds, {len(failed)} failed"
        )

        if len(failed) > 0:
            for r in failed:
                error = r["errorMessage"] if isinstance(r, dict) else r.error_message
                logger.error(f"[{self.__class__.__name__}][{operation_name}] Failed document reason: {error}")
            return failed

        return []


class AzureCosmosMongoVcoreStore(IndexStore):
    """An Azure Cosmos Mongo vCore index store used for uploading and deleting documents."""

    def __init__(self, mongo_collection: "Collection"):
        """Initialize the AzureCosmosMongoVcoreStore."""
        super().__init__(IndexStoreType.AZURE_COSMOS_MONGO_VCORE)
        self._mongo_collection = mongo_collection

    def delete_documents(self, documents: List[Any]):
        """
        Delete documents from the index.

        Raises
        ------
            `RuntimeError` if all documents are not deleted from the index.

        """
        start_time = time.time()
        results = self._mongo_collection.bulk_write(documents)

        encountered_write_errors = (
            len(results.bulk_api_result.get("writeErrors", []))
            + len(results.bulk_api_result.get("writeConcernErrors", []))
        ) > 0
        deleted_count = results.deleted_count
        total_count = len(documents)
        failed_deleted_count = total_count - deleted_count
        if not encountered_write_errors and failed_deleted_count > 0:
            logger.info(
                f"[{self.__class__.__name__}][{self.delete_documents.__name__}] "
                f"Failed to delete {failed_deleted_count} documents but there were no write errors, assuming these documents were duplicates and treating "
                f"as if though all {total_count} documents were successfully deleted."
            )
            deleted_count = total_count
            failed_deleted_count = 0

        duration = time.time() - start_time
        logger.info(
            f"[{self.__class__.__name__}][{self.delete_documents.__name__}] Deleted {deleted_count} documents in {duration:.4f} seconds."
        )
        logger.info(
            f"[{self.__class__.__name__}][{self.delete_documents.__name__}] Full bulk write result: {results.bulk_api_result}"
        )

        if failed_deleted_count > 0:
            raise RuntimeError(f"{INDEX_DELETE_FAILURE_MESSAGE_PREFIX} {failed_deleted_count} documents")

    def upload_documents(self, documents: List[Any]):
        """
        Upload documents to the index.

        Raises
        ------
            `RuntimeError` if all documents are not uploaded to the index.

        """
        start_time = time.time()
        results = self._mongo_collection.bulk_write(documents)

        encountered_write_errors = (
            len(results.bulk_api_result.get("writeErrors", []))
            + len(results.bulk_api_result.get("writeConcernErrors", []))
        ) > 0
        uploaded_count = results.upserted_count + results.modified_count
        total_count = len(documents)
        failed_uploaded_count = total_count - uploaded_count
        matched_count = results.matched_count

        # This means all documents were already in the collection AND did not need to be modified
        if not encountered_write_errors and uploaded_count == 0 and matched_count == total_count:
            logger.info(
                f"[{self.__class__.__name__}][{self.upload_documents.__name__}] "
                f"No documents were upserted or modified and there were no write errors, assuming this means they were already in the collection "
                f"and did not need to be modified (ie, no new updates), treating as if though all {total_count} documents were successfully uploaded."
            )
            uploaded_count = total_count
            failed_uploaded_count = 0

        duration = time.time() - start_time
        logger.info(
            f"[{self.__class__.__name__}][{self.upload_documents.__name__}] Uploaded {uploaded_count} documents in {duration:.4f} seconds."
        )
        logger.info(
            f"[{self.__class__.__name__}][{self.upload_documents.__name__}] Full bulk write result: {results.bulk_api_result}"
        )

        if failed_uploaded_count > 0:
            raise RuntimeError(f"{INDEX_UPLOAD_FAILURE_MESSAGE_PREFIX} {failed_uploaded_count} documents")

    def create_delete_payload_from_document_id(self, document_id: str) -> Any:
        """Given a document ID, construct a payload used to delete the corresponding document from the index."""
        from pymongo import DeleteOne

        return DeleteOne({"_id": base64.urlsafe_b64encode(document_id.encode("utf-8")).decode("utf-8")})

    def create_upload_payload_from_embedded_document(
        self,
        field_mappings: dict,
        document_id: str,
        document_source_info: dict = {},
        document_data: Optional[str] = None,
        document_embeddings: Optional[List[float]] = None,
        document_metadata: Optional[dict] = None,
    ) -> Any:
        """Given info about an EmbeddedDocument, construct a payload used to upload the document to the index."""
        if document_data is None or document_embeddings is None or document_metadata is None:
            raise ValueError("One or more of document data, embeddings, metadata is missing")

        doc_source = document_source_info

        doc_id_encoded = base64.urlsafe_b64encode(document_id.encode("utf-8")).decode("utf-8")
        azure_cosmos_mongo_vcore_doc = {
            "_id": doc_id_encoded,
            field_mappings["embedding"]: document_embeddings,
            field_mappings["content"]: document_data,
        }
        if "url" in field_mappings:
            azure_cosmos_mongo_vcore_doc[field_mappings["url"]] = doc_source.get("url", "")
        if "filename" in field_mappings:
            azure_cosmos_mongo_vcore_doc[field_mappings["filename"]] = doc_source.get("filename", "")
        if "title" in field_mappings:
            azure_cosmos_mongo_vcore_doc[field_mappings["title"]] = doc_source.get(
                "title", document_metadata.get("title", "")
            )
        if "metadata" in field_mappings:
            azure_cosmos_mongo_vcore_doc[field_mappings["metadata"]] = json.dumps(document_metadata)

        from pymongo import UpdateOne

        return UpdateOne({"_id": doc_id_encoded}, {"$set": azure_cosmos_mongo_vcore_doc}, upsert=True)


class MilvusStore(IndexStore):
    """A Milvus index store used for uploading and deleting documents."""

    def __init__(self, milvus_client: "MilvusClient", collection_name: str):
        """Initialize the MilvusStore."""
        super().__init__(IndexStoreType.MILVUS)
        self._milvus_client = milvus_client
        self._collection_name = collection_name

    def delete_documents(self, documents: List[Any]):
        """
        Delete documents from the index.

        Raises
        ------
            `RuntimeError` if all documents are not deleted from the index.

        """
        start_time = time.time()

        try:
            self._milvus_client.delete(self._collection_name, documents)
        except Exception as e:
            logger.error(
                f"Failed to delete documents from Milvus index due to: {e!s}",
                exc_info=True,
                extra={"exception": str(e)},
            )
            raise RuntimeError(f"{INDEX_DELETE_FAILURE_MESSAGE_PREFIX} documents due to: {e!s}")

        duration = time.time() - start_time
        logger.info(
            f"[{self.__class__.__name__}][{self.delete_documents.__name__}] Deleted {len(documents)} documents in {duration:.4f} seconds."
        )

    def upload_documents(self, documents: List[Any]):
        """
        Upload documents to the index.

        Raises
        ------
            `RuntimeError` if all documents are not uploaded to the index.

        """
        start_time = time.time()
        results = self._milvus_client.insert(self._collection_name, documents)
        self._milvus_client.flush(self._collection_name)

        duration = time.time() - start_time
        logger.info(
            f"[{self.__class__.__name__}][{self.upload_documents.__name__}] Uploaded {len(results)} documents in {duration:.4f} seconds."
        )

        failed_uploaded_count = len(documents) - len(results)
        if failed_uploaded_count > 0:
            raise RuntimeError(f"{INDEX_UPLOAD_FAILURE_MESSAGE_PREFIX} {failed_uploaded_count} documents")

    def create_delete_payload_from_document_id(self, document_id: str) -> Any:
        """Given a document ID, construct a payload used to delete the corresponding document from the index."""
        return base64.urlsafe_b64encode(document_id.encode("utf-8")).decode("utf-8")

    def create_upload_payload_from_embedded_document(
        self,
        field_mappings: dict,
        document_id: str,
        document_source_info: dict = {},
        document_data: Optional[str] = None,
        document_embeddings: Optional[List[float]] = None,
        document_metadata: Optional[dict] = None,
    ) -> Any:
        """Given info about an EmbeddedDocument, construct a payload used to upload the document to the index."""
        if document_data is None or document_embeddings is None or document_metadata is None:
            raise ValueError("One or more of document data, embeddings, metadata is missing")

        doc_source = document_source_info

        doc_id_encoded = base64.urlsafe_b64encode(document_id.encode("utf-8")).decode("utf-8")
        milvus_doc = {
            "id": doc_id_encoded,
            field_mappings["embedding"]: document_embeddings,
            field_mappings["content"]: document_data,
        }
        if "url" in field_mappings:
            milvus_doc[field_mappings["url"]] = doc_source.get("url", "")
        if "filename" in field_mappings:
            milvus_doc[field_mappings["filename"]] = doc_source.get("filename", "")
        if "title" in field_mappings:
            milvus_doc[field_mappings["title"]] = doc_source.get("title", document_metadata.get("title", ""))
        if "metadata" in field_mappings:
            milvus_doc[field_mappings["metadata"]] = json.dumps(document_metadata)

        return milvus_doc


class PineconeStore(IndexStore):
    """A Pinecone index store used for uploading and deleting documents."""

    def __init__(self, pinecone_client: "Index"):
        """Initialize the PineconeStore."""
        super().__init__(IndexStoreType.PINECONE)
        self._pinecone_client = pinecone_client

    def delete_documents(self, documents: List[Any]):
        """
        Delete documents from the index.

        Raises
        ------
            `RuntimeError` if all documents are not deleted from the index.

        """
        start_time = time.time()
        results = self._pinecone_client.delete(documents)

        if results != {}:
            logger.error(
                f"Failed to delete documents from Pinecone index, full results: {json.dumps(results, indent=2)}",
                extra={"properties": {"results": {json.dumps(results, indent=2)}}},
            )
            raise RuntimeError(
                f"{INDEX_DELETE_FAILURE_MESSAGE_PREFIX} documents, full results: {json.dumps(results, indent=2)}"
            )

        duration = time.time() - start_time
        logger.info(
            f"[{self.__class__.__name__}][{self.delete_documents.__name__}] Deleted {len(documents)} documents in {duration:.4f} seconds."
        )

    def upload_documents(self, documents: List[Any]):
        """
        Upload documents to the index.

        Raises
        ------
            `RuntimeError` if all documents are not uploaded to the index.

        """
        start_time = time.time()
        results = self._pinecone_client.upsert(documents)

        upserted_count = results["upserted_count"]
        failed_upserted_count = len(documents) - upserted_count
        duration = time.time() - start_time
        logger.info(
            f"[{self.__class__.__name__}][{self.upload_documents.__name__}] Uploaded {upserted_count} documents in {duration:.4f} seconds."
        )

        if failed_upserted_count > 0:
            raise RuntimeError(f"{INDEX_UPLOAD_FAILURE_MESSAGE_PREFIX} {failed_upserted_count} documents")

    def create_delete_payload_from_document_id(self, document_id: str) -> Any:
        """Given a document ID, construct a payload used to delete the corresponding document from the index."""
        return base64.urlsafe_b64encode(document_id.encode("utf-8")).decode("utf-8")

    def create_upload_payload_from_embedded_document(
        self,
        field_mappings: dict,
        document_id: str,
        document_source_info: dict = {},
        document_data: Optional[str] = None,
        document_embeddings: Optional[List[float]] = None,
        document_metadata: Optional[dict] = None,
    ) -> Any:
        """Given info about an EmbeddedDocument, construct a payload used to upload the document to the index."""
        if document_data is None or document_embeddings is None or document_metadata is None:
            raise ValueError("One or more of document data, embeddings, metadata is missing")

        doc_source = document_source_info

        doc_id_encoded = base64.urlsafe_b64encode(document_id.encode("utf-8")).decode("utf-8")
        pinecone_doc = {"id": doc_id_encoded, "values": document_embeddings}

        pinecone_doc_metadata = {field_mappings["content"]: document_data}
        if "url" in field_mappings:
            pinecone_doc_metadata[field_mappings["url"]] = doc_source.get("url", "")
        if "filename" in field_mappings:
            pinecone_doc_metadata[field_mappings["filename"]] = doc_source.get("filename", "")
        if "title" in field_mappings:
            pinecone_doc_metadata[field_mappings["title"]] = doc_source.get("title", document_metadata.get("title", ""))
        if "metadata" in field_mappings:
            pinecone_doc_metadata[field_mappings["metadata"]] = json.dumps(document_metadata)

        # Metadata value must be a string, number, boolean or list of strings
        pinecone_doc["metadata"] = pinecone_doc_metadata

        return pinecone_doc
