# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import base64
from io import BytesIO
from itertools import chain
import json
from dataclasses import dataclass, field
import os
from random import randint
import re
import time
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    TypedDict,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
    overload,
    Literal
)

from openai import RateLimitError
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai_messages_token_helper import build_messages, get_token_limit

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.transport import HttpTransport

from azure.search.documents.models import (
    QueryCaptionResult,
    QueryType,
    VectorizedQuery,
    VectorQuery,
)
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
    VectorSearchVectorizer,
)

from .._resources._resource_map import *
from .._resources._client_settings import ClientSettings
from ._textsplitter import SentenceTextSplitter, SimpleTextSplitter
from ._parser import DocumentAnalysisParser, JsonParser, TextParser, LocalPdfParser
from ._storage import StorageFile


@dataclass
class Document:
    id: Optional[str]
    content: Optional[str]
    embedding: Optional[List[float]]
    source_page: Optional[str]
    source_file: Optional[str]
    captions: List[str]
    score: Optional[float] = None
    reranker_score: Optional[float] = None
    fields: Dict[str, str] = field(default_factory=dict)

Tokenizer = Callable[[str], List[int]]


class ExtraArgs(TypedDict, total=False):
    dimensions: int


def _filename_to_id(filename):
    filename_ascii = re.sub("[^0-9a-zA-Z_-]", "_", filename)
    filename_hash = base64.b16encode(filename.encode("utf-8")).decode("ascii")
    return f"file-{filename_ascii}-{filename_hash}"


def _sourcepage_from_file_page(filename, page: int = 0) -> str:
    if os.path.splitext(filename)[1].lower() == ".pdf":
        return f"{os.path.basename(filename)}#page={page + 1}"
    else:
        return os.path.basename(filename)


def _nonewlines(s: Optional[str]) -> str:
    s = s or ""
    return s.replace("\n", " ").replace("\r", " ")


class CloudMachineDocumentIndex:
    file_splitters: Mapping[str, Callable[[List[Tuple[int, int, str]]], Generator[Tuple[int, str], None, None]]]
    file_parsers: Mapping[str, Callable[[IO], Generator[Tuple[int, int, str], None, None]]]
    
    SUPPORTED_BATCH_MODEL = {
        "text-embedding-ada-002": {"token_limit": 8100, "max_batch_size": 16},
        "text-embedding-3-small": {"token_limit": 8100, "max_batch_size": 16},
        "text-embedding-3-large": {"token_limit": 8100, "max_batch_size": 16},
    }
    SUPPORTED_DIMENSIONS_MODEL = {
        "text-embedding-ada-002": False,
        "text-embedding-3-small": True,
        "text-embedding-3-large": True,
    }

    _NO_RESPONSE = "0"

    _SEARCH_QUERY_PROMPT = """Below is a history of the conversation so far, and a new question asked by the user that needs to be answered by searching in a knowledge base.
    You have access to Azure AI Search index with many documents.
    Generate a search query based on the conversation and the new question.
    Do not include cited source filenames and document names e.g info.txt or doc.pdf in the search query terms.
    Do not include any text inside [] or <<>> in the search query terms.
    Do not include any special characters like '+'.
    If the question is not in English, translate the question to English before generating the search query.
    If you cannot generate a search query, return just the number 0.
    """

    def __init__(
            self,
            *,
            search: ClientSettings[SearchIndexClient],
            documentai: Optional[ClientSettings[DocumentIntelligenceClient]] = None,
            openai: Optional[ClientSettings[AzureOpenAI]] = None,
            transport: Optional[HttpTransport] = None,
    ):
        self._documentai = documentai
        self._search = search
        self._openai = openai
        self._fields: List[Union[str, dict]] = search.get('document_index_fields', [])
        self._index_client: SearchIndexClient = self._search.client(transport=transport)
        self._search_client: SearchClient = self._index_client.get_search_client(self.index_name)
        self._supports_vectorization = False
        try:
            self._embeddings = self._openai.client(
                client_options={'azure_deployment': self.embeddings_deployment}
            )
            self.embeddings_model
        except RuntimeError as e:
            self._embeddings = None

        sentence_text_splitter = SentenceTextSplitter()
        self.file_splitters = {
            ".pdf": sentence_text_splitter,
            ".html": sentence_text_splitter,
            ".json": SimpleTextSplitter(),
            ".docx": sentence_text_splitter,
            ".pptx": sentence_text_splitter,
            ".xlsx": sentence_text_splitter,
            ".png": sentence_text_splitter,
            ".jpg": sentence_text_splitter,
            ".jpeg": sentence_text_splitter,
            ".tiff": sentence_text_splitter,
            ".bmp": sentence_text_splitter,
            ".heic": sentence_text_splitter,
            ".md": sentence_text_splitter,
            ".txt": sentence_text_splitter,
        }
        self.file_parsers = {
            ".json": JsonParser(),
            ".md": TextParser(),
            ".txt": TextParser(),
        }
        try:
            self._docs_client = self._documentai.client(transport=transport)
            doc_int_parser = DocumentAnalysisParser(self._docs_client)
            self.file_parsers.update(
                {
                    ".pdf": doc_int_parser,
                    ".html": doc_int_parser,
                    ".docx": doc_int_parser,
                    ".pptx": doc_int_parser,
                    ".xlsx": doc_int_parser,
                    ".png": doc_int_parser,
                    ".jpg": doc_int_parser,
                    ".jpeg": doc_int_parser,
                    ".tiff": doc_int_parser,
                    ".bmp": doc_int_parser,
                    ".heic": doc_int_parser,
                }
            )
        except (RuntimeError, AttributeError):
            self._docs_client = None
            self.file_parsers.update(
                {
                    ".pdf": LocalPdfParser()
                }
            )

    @property
    def index_name(self) -> str:
        return self._search.get('document_index_name', 'documentembeddingindex')
    
    @property
    def search_analyzer_name(self) -> str:
        return self._search.get('analyzer_name', 'en.microsoft')

    @property
    def vectorized_search(self) -> bool:
        if self._supports_vectorization:
            return self._search.get('disable_vectorization', self._supports_vectorization)
        return False

    @property
    def semantic_search(self) -> Optional[str]:
        try:
            # first check is semantic search supported
            self._search.get('semantic_ranker')
        except RuntimeError:
            return None
        return self._search.get('semantic_config', 'default')

    @property
    def embeddings_deployment(self) -> str:
        return self._openai.get('embeddings_deployment')

    @property
    def embeddings_model(self) -> Optional[str]:
        return self._openai.get('embeddings_model')
    
    @property
    def embeddings_dimensions(self) -> Optional[int]:
        value = None
        if self.SUPPORTED_DIMENSIONS_MODEL.get(self.embeddings_model, False):
            value = self._openai.get('embeddings_dimensions', 1536)
        return value

    @property
    def search_tool(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_sources",
                "description": "Retrieve sources from the Azure AI Search index",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "Query string to retrieve documents from Azure Search",
                        }
                    },
                    "required": ["search_query"],
                },
            },
        }

    def build_search_query_messages(
            self,
            chat_model: str,
            user_query: str,
            *,
            past_messages: Optional[List[Dict[str, Any]]] = None,
            tools: Optional[List[Dict[str, Any]]] = None,
            few_shots: Optional[List[Dict[str, Any]]] = None,
            response_token_limit: int = 100
    ) -> List[ChatCompletionMessageParam]:
        tools = tools or []
        if self.search_tool not in tools:
            tools.append(self.search_tool)
        return build_messages(
            model=chat_model,
            system_prompt=self._SEARCH_QUERY_PROMPT,
            tools=tools,
            few_shots=few_shots or [],
            past_messages=past_messages or [],
            new_user_content="Generate search query for: " + user_query,
            max_tokens=get_token_limit(chat_model) - response_token_limit,
        )

    def extract_search_query(self, chat_completion: 'ChatCompletion', user_query: str) -> Optional[str]:
        response_message = chat_completion.choices[0].message
        if response_message.tool_calls:
            for tool in response_message.tool_calls:
                if tool.type != "function":
                    continue
                function = tool.function
                if function.name == "search_sources":
                    arg = json.loads(function.arguments)
                    search_query = arg.get("search_query", self._NO_RESPONSE)
                    if search_query != self._NO_RESPONSE:
                        return search_query
        elif query_text := response_message.content:
            if query_text.strip() != self._NO_RESPONSE:
                return query_text
        return user_query

    @overload
    def prepare_file(
        self,
        file: Union[StorageFile[IO], IO],
        *,
        filename: Optional[str] = None,
        parser: Optional[Callable[[IO], Generator[Tuple[int, int, str], None, None]]] = None,
        splitter: Optional[Callable[[List[Tuple[int, int, str]]], Generator[Tuple[int, str], None, None]]] = None,
    ) -> List[Tuple[int, str]]:
        ...
    @overload
    def prepare_file(
        self,
        file: Union[StorageFile[IO], IO],
        *,
        filename: Optional[str] = None,
        parser: Optional[Callable[[IO], Generator[Tuple[int, int, str], None, None]]] = None,
        splitter: Optional[Callable[[List[Tuple[int, int, str]]], Generator[Tuple[int, str], None, None]]] = None,
        embedding_batching: Union[str, Tuple[Union[Tokenizer, str, Literal['gpt2', 'r50k_base', 'p50k_base', 'p50k_edit', 'cl100k_base', 'o200k_base']], int, int]]
    ) -> List[List[Tuple[int, str]]]:
        ...
    def prepare_file(
        self,
        file: Union[StorageFile[IO], IO],
        *,
        filename: Optional[str] = None,
        parser: Optional[Callable[[IO], Generator[Tuple[int, int, str], None, None]]] = None,
        splitter: Optional[Callable[[List[Tuple[int, int, str]]], Generator[Tuple[int, str], None, None]]] = None,
        embedding_batching: Optional[Union[str, Tuple[Tokenizer, int, int]]] = None
    ) -> Union[List[List[Tuple[int, str]]], List[Tuple[int, str]]]:
        content = file.content if isinstance(file, StorageFile) else file
        all_content = content.read()
        new_stream = BytesIO(all_content)
        name = filename
        extension = ""
        if (not parser or not splitter):
            if not name:
                if hasattr(file, 'filename'):
                    name = file.filename
                else:
                    raise ValueError("Unable to determine filename.")
            extension = os.path.splitext(name)[1]
        try:
            parser = parser or self.file_parsers[extension]
            splitter = splitter or self.file_splitters[extension]
        except KeyError as e:
            raise TypeError(f"No parser or splitter found for file '{name}' with extension: '{extension}'") from e
        parts = list(splitter(list(parser(new_stream))))
        if embedding_batching:
            return self._split_parts_into_batches(embedding_batching, parts)
        return parts

    def _create_index(self):
        vectorizers = []
        # if self.vectorized_search:
        #     from azure.search.documents.indexes.models import AzureOpenAIVectorizer, AzureOpenAIVectorizerParameters
        #     vectorizers=[
        #         AzureOpenAIVectorizer(
        #             vectorizer_name=f"{self.index_name}-vectorizer",
        #             parameters=AzureOpenAIVectorizerParameters(
        #                 resource_url=self._openai.endpoint,
        #                 deployment_name=self.embeddings_deployment,
        #             ),
        #         ),
        #     ]
        fields = [
            (
                SimpleField(name="id", type="Edm.String", key=True)
                if not self.vectorized_search
                else SearchField(
                    name="id",
                    type="Edm.String",
                    key=True,
                    sortable=True,
                    filterable=True,
                    facetable=True,
                    analyzer_name="keyword",
                )
            ),
            SearchableField(
                name="content",
                type="Edm.String",
                analyzer_name=self.search_analyzer_name,
            ),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                hidden=False,
                searchable=True,
                filterable=False,
                sortable=False,
                facetable=False,
                vector_search_dimensions=self.embeddings_dimensions or 1536,
                vector_search_profile_name="embedding_config",
            ),
            SimpleField(
                name="sourcepage",
                type="Edm.String",
                filterable=True,
                facetable=True,
            ),
            SimpleField(
                name="sourcefile",
                type="Edm.String",
                filterable=True,
                facetable=True,
            ),
            SimpleField(
                name="storageUrl",
                type="Edm.String",
                filterable=True,
                facetable=False,
            ),
        ]
        for field in self._fields:
            if isinstance(field, str):
                fields.append(SimpleField(name=field, type="Edm.String", filterable=True, facetable=True))
            else:
                fields.append(SearchField.from_dict(field))
        if self.vectorized_search:
            fields.append(SearchableField(name="parent_id", type="Edm.String", filterable=True))

        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="hnsw_config",
                        parameters=HnswParameters(metric="cosine"),
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        name="embedding_config",
                        algorithm_configuration_name="hnsw_config",
                        #vectorizer=f"{self.index_name}-vectorizer" if vectorizers else None,
                    ),
                ],
                vectorizers=vectorizers,
            )
        )
        if self.semantic_search:
            index.semantic_search = SemanticSearch(
                configurations=[
                    SemanticConfiguration(
                        name=self.semantic_search,
                        prioritized_fields=SemanticPrioritizedFields(
                            title_field=None, content_fields=[SemanticField(field_name="content")]
                        ),
                    )
                ]
            )

        self._index_client.create_index(index)

    def _get_tokenizer(
            self,
            *,
            model_name: Optional[str] = None,
            encoding: Optional[str] = None
    ) -> Callable[..., List[int]]:
        try:
            import tiktoken
            if model_name:
                encoder = tiktoken.encoding_for_model(model_name)
            elif encoding:
                encoder = tiktoken.get_encoding(encoding)
            return encoder.encode
        except KeyError as e:
            raise ValueError(
                f"Model {model_name} is not supported with batch embedding operations, try passing in custom tokenizer."
            ) from e
        except ImportError as e:
            raise ImportError("Automatic tokenizer detection requires installing the 'tiktoken' lib.") from e

    def _split_parts_into_batches(
            self,
            batching: Union[str, Tuple[Union[Tokenizer, str, Literal['gpt2', 'r50k_base', 'p50k_base', 'p50k_edit', 'cl100k_base', 'o200k_base']], int, int]],
            parts: List[Tuple[int, str]]
    ) -> List[List[Tuple[int, str]]]:
        if isinstance(batching, str):
            batch_info = self.SUPPORTED_BATCH_MODEL.get(batching)
            if not batch_info:
                raise ValueError(
                    f"Model {batching} is not supported with batch embedding operations"
                )
            tokenizer = self._get_tokenizer(model_name=batching)
            batch_token_limit = batch_info["token_limit"]
            batch_max_size = batch_info["max_batch_size"]
        else:
            tokenizer = batching[0]
            if isinstance(tokenizer, str):
                tokenizer = self._get_tokenizer(encoding=tokenizer)
            batch_token_limit = batching[1]
            batch_max_size = batching[2]

        batches: List[List[Tuple[int, str]]] = []
        batch: List[Tuple[int, str]] = []
        batch_token_length = 0
        for part in parts:
            text_token_length = len(tokenizer(part[1]))
            if batch_token_length + text_token_length >= batch_token_limit and len(batch) > 0:
                batches.append(batch)
                batch = []
                batch_token_length = 0

            batch.append(part)
            batch_token_length = batch_token_length + text_token_length
            if len(batch) == batch_max_size:
                batches.append(batch)
                batch = []
                batch_token_length = 0

        if len(batch) > 0:
            batches.append(batch)
        return batches

    def _create_embedding_batch(self, batches: List[List[Tuple[int, str]]]) -> List[List[float]]:
        embeddings = []
        kwargs = {}
        if self.embeddings_dimensions:
            kwargs = {'dimensions': self.embeddings_dimensions}
        for batch in batches:
            for attempt in range(15):
                try:
                    inputs = [part[1] for part in batch]
                    emb_response = self._embeddings.embeddings.create(
                        model=self.embeddings_model, input=inputs, **kwargs
                    )
                    embeddings.extend([data.embedding for data in emb_response.data])
                    break
                except RateLimitError:
                    if attempt == 14:
                        raise
                    sleep_time = randint(15, 60)
                    time.sleep(sleep_time)
        return embeddings

    def _create_embedding_single(self, parts: List[Tuple[int, str]]) -> List[List[float]]:
        embeddings = []
        kwargs = {}
        if self.embeddings_dimensions:
            kwargs = {'dimensions': self.embeddings_dimensions}
        for part in parts:
            for attempt in range(15):
                try:
                    emb_response = self._embeddings.embeddings.create(
                        model=self.embeddings_model, input=part[1], **kwargs
                    )
                    embeddings.append(emb_response.data[0].embedding)
                except RateLimitError:
                    if attempt == 14:
                        raise
                    sleep_time = randint(15, 60)
                    time.sleep(sleep_time)
        return embeddings

    def get_sources(
        self,
        results: List[Document],
        *,
        use_captions: bool = False,
    ) -> List[str]:
        if use_captions:
            return [
                (self.get_citation((document)))
                + ": "
                + _nonewlines(" . ".join(document.captions))
                for document in results
            ]
        else:
            return [
                (self.get_citation((document))) + ": " + _nonewlines(document.content)
                for document in results
            ]

    def get_citation(self, document: Document) -> str:
        source_page = document.source_page or ""
        path, ext = os.path.splitext(source_page)
        if ext.lower() == ".pdf":
            page_idx = path.rfind("-")
            page_number = int(path[page_idx + 1 :])
            return f"{path[:page_idx]}.pdf#page={page_number}"
        return source_page

    @overload
    def add_file(
        self,
        *,
        filename: str,
        parts: Iterable[Tuple[int, str]],
        embeddings: Optional[List[List[float]]] = None,
        url: Optional[str] = None,
        fields: Optional[Dict[str, str]] = None
    ) -> None:
        ...
    @overload
    def add_file(
        self,
        *,
        file: Union[IO, StorageFile[IO]],
        filename: Optional[str] = None,
        url: Optional[str] = None,
        fields: Optional[Dict[str, str]] = None
    ) -> None:
        ...    
    def add_file(
        self,
        *,
        filename: Optional[str] = None,
        file: Optional[Union[IO, StorageFile[IO]]] = None,
        parts: Optional[List[Tuple[int, str]]] = None,
        embeddings: Optional[List[List[float]]] = None,
        url: Optional[str] = None,
        fields: Optional[Dict[str, str]] = None
    ) -> None:
        MAX_BATCH_SIZE = 1000
        if file:
            if not filename:
                if hasattr(file, 'filename'):
                    filename = file.filename
                else:
                    raise ValueError("Unable to determine filename.")
            if self._embeddings:
                if self.embeddings_model in self.SUPPORTED_BATCH_MODEL and not self._openai.get('disable_batch', False):
                    parts = self.prepare_file(file, filename=filename, embedding_batching=self.embeddings_model)
                    embeddings = self._create_embedding_batch(parts)
                    parts = chain(*parts)
                else:
                    parts = self.prepare_file(file, filename=filename)
                    embeddings = self._create_embedding_single(parts)
            else:
                parts = self.prepare_file(file, filename=filename)
        parts = list(parts)
        if embeddings and len(embeddings) != len(parts):
            raise ValueError(f"Emeddings (len={len(embeddings)}) do not match file parts (len={len(parts)}).")
        parts = list(zip(parts, embeddings or (None for _ in range(len(parts)))))
        section_batches = [parts[i : i + MAX_BATCH_SIZE] for i in range(0, len(parts), MAX_BATCH_SIZE)]

        def _build_document(section_index: int, batch_index: int, section: Tuple[Tuple[int, str], Optional[List[float]]]) -> Dict:
            section_data, section_embeddings = section
            document = {
                "id": f"{_filename_to_id(filename)}-page-{section_index + batch_index * MAX_BATCH_SIZE}",
                "content": section_data[1],
                "sourcepage": (
                    _sourcepage_from_file_page(
                        filename=filename,
                        page=section_data[0],
                    )
                ),
                "sourcefile": os.path.basename(filename),
            }
            if url:
                document["storageUrl"] = url
            if section_embeddings:
                document["embedding"] = section_embeddings
            if fields:
                document.update(fields)
            return document

        for batch_index, batch in enumerate(section_batches):
            documents = [
                _build_document(batch_index, section_index, section)
                for section_index, section in enumerate(batch)
            ]
            search_client = self._index_client.get_search_client(self.index_name)
            try:
                print(f"Uploading {len(documents)} documents to index")
                results = search_client.upload_documents(documents)
                if not all([r.succeeded for r in results]):
                    raise Exception("Document didn't successfully index", results)
            except ResourceNotFoundError as e:
                if f"The index '{self.index_name}' for service" in str(e):
                    self._create_index()
                    search_client.upload_documents(documents)
                else:
                    raise

    def remove_all(self) -> None:
        if not self._search_client:
            self._search_client = self._index_client.get_search_client(self.index_name)
        while True:
            max_results = 1000
            try:
                result = self._search_client.search(
                    search_text="", top=max_results, include_total_count=True
                )
            except ResourceNotFoundError as e:
                if f"The index '{self.index_name}' for service" in str(e):
                    print("Index not found. Skipping")
                    break
            result_count = result.get_count()
            if result_count == 0:
                break
            documents_to_remove = [{"id": d["id"]} for d in result]
            if len(documents_to_remove) == 0:
                if result_count < max_results:
                    break
                else:
                    continue
            self._search_client.delete_documents(documents_to_remove)
            # It can take a few seconds for search results to reflect changes, so wait a bit
            time.sleep(2)

    def remove_file(self, file: Union[str, StorageFile]) -> None:
        filename = file.filename if isinstance(file, StorageFile) else file
        if not self._search_client:
            self._search_client = self._index_client.get_search_client(self.index_name)
        while True:
            # Replace ' with '' to escape the single quote for the filter
            # https://learn.microsoft.com/azure/search/query-odata-filter-orderby-syntax#escaping-special-characters-in-string-constants
            path_for_filter = os.path.basename(filename).replace("'", "''")
            filter = f"sourcefile eq '{path_for_filter}'"
            max_results = 1000
            try:
                result = self._search_client.search(
                    search_text="", filter=filter, top=max_results, include_total_count=True
                )
                result_count = result.get_count()
            except ResourceNotFoundError as e:
                if f"The index '{self.index_name}' for service" in str(e):
                    print("Index not found. Skipping")
                    break
            if result_count == 0:
                break
            documents_to_remove = [{"id": d["id"]} for d in result]
            if len(documents_to_remove) == 0:
                if result_count < max_results:
                    break
                else:
                    continue
            self._search_client.delete_documents(documents_to_remove)
            
            # It can take a few seconds for search results to reflect changes, so wait a bit
            time.sleep(2)

    def search(
        self,
        *,
        top: int = 3,
        query: Optional[str] = None,
        filter: Optional[str] = None,
        semantic_search: bool = True,
        vectors: List[VectorQuery] = None,
        embedding: List[float] = None,
        **kwargs
    ) -> List[Document]:
        if not self._search_client:
            self._search_client = self._index_client.get_search_client(self.index_name)
        search_text = query or ""
        search_vectors = vectors or []
        if self._embeddings and query and not embedding:
            dimensions_args = {}
            if self.embeddings_dimensions:
                dimensions_args = {'dimensions': self.embeddings_dimensions}
            embedding_result = self._embeddings.embeddings.create(
                model=self.embeddings_model,
                input=query,
                **dimensions_args,
            )
            embedding = embedding_result.data[0].embedding

        if embedding:
            from azure.search.documents.models import VectorizedQuery
            search_vectors.append(VectorizedQuery(vector=embedding, k_nearest_neighbors=50, fields="embedding"))
        if semantic_search:
            if not self.semantic_search:
                raise ValueError("Semantic search not supported.")
            results = self._search_client.search(
                search_text=search_text,
                filter=filter,
                top=top,
                query_caption="extractive",
                query_caption_highlight_enabled=False,
                vector_queries=search_vectors,
                query_type=QueryType.SEMANTIC,
                query_language=self._search.get('query_language', None),
                query_speller=self._search.get('query_speller', None),
                semantic_configuration_name=self.semantic_search,
                semantic_query=query,
                **kwargs
            )
        else:
            results = self._search_client.search(
                search_text=search_text,
                filter=filter,
                top=top,
                vector_queries=search_vectors,
                **kwargs
            )
        documents = []
        for document in results:
            doc = Document(
                id=document.pop("id"),
                content=document.pop("content"),
                embedding=document.pop("embedding"),
                source_page=document.pop("sourcepage"),
                source_file=document.pop("sourcefile"),
                captions=[c.text for c in document.pop("@search.captions", [])],
                score=document.pop("@search.score", 0),
                reranker_score=document.pop("@search.reranker_score", 0),
            )
            other_fields = {k: v for k, v in document.items() if not k.startswith("@")}
            doc.fields = other_fields
            documents.append(doc)
        return documents

    def _get_sources_content(
        self, results: List[Document], use_semantic_captions: bool, use_image_citation: bool
    ) -> list[str]:
        if use_semantic_captions:
            return [
                (self._get_citation((doc.source_page or ""), use_image_citation))
                + ": "
                + _nonewlines(" . ".join(doc.captions or []))
                for doc in results
            ]
        else:
            return [
                (self._get_citation((doc.source_page or ""), use_image_citation)) + ": " + _nonewlines(doc.content or "")
                for doc in results
            ]

    def _get_citation(self, sourcepage: str, use_image_citation: bool) -> str:
        if use_image_citation:
            return sourcepage
        else:
            path, ext = os.path.splitext(sourcepage)
            if ext.lower() == ".png":
                page_idx = path.rfind("-")
                page_number = int(path[page_idx + 1 :])
                return f"{path[:page_idx]}.pdf#page={page_number}"

            return sourcepage

    def close(self) -> None:
        if self._docs_client:
            self._docs_client.close()
        if self._index_client:
            self._index_client.close()
        if self._embeddings:
            self._embeddings.close()
