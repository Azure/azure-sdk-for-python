# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared helpers for sync live tests.

The goal: every live test reads as *what it verifies*, not *how it sets up*.
See ``_search_helpers_async.py`` for the async siblings.
"""

from __future__ import annotations

from copy import deepcopy
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Optional

from azure.core.exceptions import HttpResponseError
from azure.search.documents import IndexDocumentsBatch, SearchClient, SearchIndexingBufferedSender
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeSourceReference,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
    SearchSuggester,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)
from devtools_testutils import get_credential, recorded_by_proxy

from search_service_preparer import SearchEnvVarPreparer, search_decorator


KNOWLEDGE_BASE_DESCRIPTION = "Search knowledge base description"
KNOWLEDGE_SOURCE_DESCRIPTION = "Search knowledge source description"
SEARCH_RESOURCE_PREFIX = "search"
SEMANTIC_CONFIGURATION_NAME = "default"

HOTEL_DOCUMENT_COUNT = 10
LARGE_HOTEL_DOCUMENT_COUNT = 60
INDEXING_DELAY_SECONDS = 3
HOTEL_NAME = "Stay-Kay City Hotel"
REPLACEMENT_HOTEL_NAME = "Old Century Hotel"
MISSING_HOTEL_ID = "1003"
HOTEL_LOOKUP_FIELDS = ("HotelId", "HotelName", "Description")
HOTEL_SUGGESTER_NAME = "sg"
SEARCH_SELECT_FIELDS = ["HotelName", "Category", "Description"]
RESULT_METADATA_KEYS = {
    "@search.score",
    "@search.reranker_score",
    "@search.highlights",
    "@search.captions",
    "@search.document_debug_info",
    "@search.reranker_boosted_score",
}

_HOTEL_DOCUMENTS = [
    {
        "HotelId": "1",
        "HotelName": "Stay-Kay City Hotel",
        "Description": (
            "This classic hotel is fully-refurbished and ideally located on the main commercial artery "
            "of the city in the heart of New York."
        ),
        "Description_fr": "Hotel classique renove au coeur de New York.",
        "Category": "Boutique",
        "Tags": ["view", "air conditioning", "concierge"],
        "ParkingIncluded": False,
        "IsDeleted": False,
        "LastRenovationDate": "2015-01-18T00:00:00+00:00",
        "Rating": 3.6,
    },
    {
        "HotelId": "2",
        "HotelName": "Old Century Hotel",
        "Description": (
            "The hotel is situated in a nineteenth century plaza renovated to the highest architectural "
            "standards."
        ),
        "Description_fr": "Hotel situe dans une place du dix-neuvieme siecle.",
        "Category": "Boutique",
        "Tags": ["pool", "free wifi", "concierge"],
        "ParkingIncluded": False,
        "IsDeleted": False,
        "LastRenovationDate": "2018-04-12T00:00:00+00:00",
        "Rating": 3.6,
    },
    {
        "HotelId": "3",
        "HotelName": "By the Market Hotel",
        "Description": "Book now and save up to 30 percent at a central location with brand new rooms.",
        "Description_fr": "Reservation centrale avec chambres neuves.",
        "Category": "Budget",
        "Tags": ["coffee in lobby", "free wifi", "24-hour front desk service"],
        "ParkingIncluded": False,
        "IsDeleted": False,
        "LastRenovationDate": "2020-06-15T00:00:00+00:00",
        "Rating": 3.3,
    },
    {
        "HotelId": "4",
        "HotelName": "Economy Universe Motel",
        "Description": "Local family-run hotel in a busy downtown location with free WiFi.",
        "Description_fr": "Hotel familial au centre-ville avec WiFi gratuit.",
        "Category": "Budget",
        "Tags": ["coffee in lobby", "free wifi", "free parking"],
        "ParkingIncluded": True,
        "IsDeleted": False,
        "LastRenovationDate": "2016-09-20T00:00:00+00:00",
        "Rating": 2.9,
    },
    {
        "HotelId": "5",
        "HotelName": "Lion's Den Inn",
        "Description": "Full breakfast buffet, room upgrades, fast high speed WiFi, and updated corridors.",
        "Description_fr": "Petit dejeuner buffet et WiFi rapide.",
        "Category": "Budget",
        "Tags": ["laundry service", "free wifi", "restaurant"],
        "ParkingIncluded": True,
        "IsDeleted": False,
        "LastRenovationDate": "2021-02-10T00:00:00+00:00",
        "Rating": 3.9,
    },
    {
        "HotelId": "6",
        "HotelName": "Thunderbird Motel",
        "Description": "Clean, comfortable rooms at the lowest price with complimentary coffee and tea.",
        "Description_fr": "Chambres propres et confortables avec cafe et the.",
        "Category": "Budget",
        "Tags": ["coffee in lobby", "free parking", "free wifi"],
        "ParkingIncluded": True,
        "IsDeleted": False,
        "LastRenovationDate": "2019-11-01T00:00:00+00:00",
        "Rating": 4.4,
    },
    {
        "HotelId": "7",
        "HotelName": "Winter Panorama Resort",
        "Description": "Skiing, outdoor ice skating, sleigh rides, tubing, snow biking, and spa services.",
        "Description_fr": "Ski, patinage exterieur et services de spa.",
        "Category": "Resort and Spa",
        "Tags": ["restaurant", "bar", "pool"],
        "ParkingIncluded": True,
        "IsDeleted": False,
        "LastRenovationDate": "2022-12-01T00:00:00+00:00",
        "Rating": 4.5,
    },
    {
        "HotelId": "8",
        "HotelName": "Luxury Lion Resort",
        "Description": "Visit our downtown hotel for luxury accommodations, comfort, and free WiFi.",
        "Description_fr": "Hotel de luxe avec confort et WiFi gratuit.",
        "Category": "Luxury",
        "Tags": ["bar", "concierge", "restaurant"],
        "ParkingIncluded": False,
        "IsDeleted": False,
        "LastRenovationDate": "2023-07-19T00:00:00+00:00",
        "Rating": 4.1,
    },
    {
        "HotelId": "9",
        "HotelName": "City Skyline Antiquity Hotel",
        "Description": "In vogue since 1888, this hotel combines old world charm with skyline views.",
        "Description_fr": "Hotel historique avec vue sur la ville.",
        "Category": "Boutique",
        "Tags": ["view", "concierge", "bar"],
        "ParkingIncluded": False,
        "IsDeleted": False,
        "LastRenovationDate": "2017-03-28T00:00:00+00:00",
        "Rating": 4.5,
    },
    {
        "HotelId": "10",
        "HotelName": "Countryside Hotel",
        "Description": "Save up to 50 percent off traditional hotels with great location and full kitchen.",
        "Description_fr": "Hotel avec cuisine complete et tres bon emplacement.",
        "Category": "Extended-Stay",
        "Tags": ["24-hour front desk service", "laundry service", "free wifi"],
        "ParkingIncluded": False,
        "IsDeleted": False,
        "LastRenovationDate": "2014-08-09T00:00:00+00:00",
        "Rating": 2.7,
    },
]


# ---------------------------------------------------------------------------
# Context dataclass
# ---------------------------------------------------------------------------


@dataclass
class SearchLiveContext:
    """Bag of resources created for a single live test."""

    credential: Any
    index_client: SearchIndexClient
    index_name: Optional[str] = None
    knowledge_source_name: Optional[str] = None
    knowledge_base_name: Optional[str] = None
    knowledge_source: Optional[SearchIndexKnowledgeSource] = None
    knowledge_base: Optional[KnowledgeBase] = None
    extras: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Shared operations
# ---------------------------------------------------------------------------


def safe_delete(callable_: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    """Invoke a delete callable, swallowing ``HttpResponseError``."""
    try:
        callable_(*args, **kwargs)
    except HttpResponseError:
        pass


def poll_until(
    fn: Callable[[], Any],
    *,
    predicate: Callable[[Any], bool],
    interval: float = 5.0,
    attempts: int = 36,
) -> list:
    """Poll ``fn`` until ``predicate(result)`` is true; return all snapshots."""
    snapshots: list = []
    for attempt in range(attempts):
        snapshot = fn()
        snapshots.append(snapshot)
        if predicate(snapshot):
            return snapshots
        if attempt < attempts - 1:
            time.sleep(interval)
    last_snapshot = snapshots[-1] if snapshots else None
    raise AssertionError(
        f"Polling timed out after {attempts} attempts; last snapshot: {last_snapshot!r}"
    )


# ---------------------------------------------------------------------------
# Client + model factories
# ---------------------------------------------------------------------------


def make_index_client(endpoint: str, *, credential: Any = None) -> SearchIndexClient:
    """Create a ``SearchIndexClient`` with the standard live-test config."""
    cred = credential if credential is not None else get_credential()
    return SearchIndexClient(endpoint, cred, retry_backoff_factor=60)


def make_search_client(endpoint: str, index_name: str, *, credential: Any = None) -> SearchClient:
    """Create a ``SearchClient`` for ``index_name`` with the standard live-test config."""
    cred = credential if credential is not None else get_credential()
    return SearchClient(endpoint, index_name, cred, retry_backoff_factor=60)


def make_indexer_client(endpoint: str, *, credential: Any = None) -> SearchIndexerClient:
    """Create a ``SearchIndexerClient`` with the standard live-test config."""
    cred = credential if credential is not None else get_credential()
    return SearchIndexerClient(endpoint, cred, retry_backoff_factor=60)


def build_index(index_name: str, *, semantic: bool = False) -> SearchIndex:
    """Build a minimal ``SearchIndex`` (id/content fields), optionally semantic."""
    fields_ = [
        SearchField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
    ]
    semantic_search = (
        SemanticSearch(
            default_configuration_name=SEMANTIC_CONFIGURATION_NAME,
            configurations=[
                SemanticConfiguration(
                    name=SEMANTIC_CONFIGURATION_NAME,
                    prioritized_fields=SemanticPrioritizedFields(
                        content_fields=[SemanticField(field_name="content")]
                    ),
                )
            ],
        )
        if semantic
        else None
    )
    return SearchIndex(name=index_name, fields=fields_, semantic_search=semantic_search)


def build_knowledge_source(
    index_name: str,
    knowledge_source_name: str,
    *,
    description: str = KNOWLEDGE_SOURCE_DESCRIPTION,
) -> SearchIndexKnowledgeSource:
    return SearchIndexKnowledgeSource(
        name=knowledge_source_name,
        description=description,
        search_index_parameters=SearchIndexKnowledgeSourceParameters(search_index_name=index_name),
    )


def build_knowledge_base(
    knowledge_base_name: str,
    knowledge_source_name: str,
    *,
    description: str = KNOWLEDGE_BASE_DESCRIPTION,
) -> KnowledgeBase:
    return KnowledgeBase(
        name=knowledge_base_name,
        description=description,
        knowledge_sources=[KnowledgeSourceReference(name=knowledge_source_name)],
    )


def _hotel_field(
    name: str,
    field_type: str | SearchFieldDataType,
    *,
    key: bool | None = None,
    searchable: bool | None = None,
    filterable: bool | None = None,
    sortable: bool | None = None,
    facetable: bool | None = None,
    analyzer_name: str | None = None,
) -> SearchField:
    return SearchField(
        name=name,
        type=field_type,
        key=key,
        searchable=searchable,
        filterable=filterable,
        sortable=sortable,
        facetable=facetable,
        analyzer_name=analyzer_name,
    )


def build_hotel_index(index_name: str) -> SearchIndex:
    """Build the deterministic sample-shaped hotel index shared by live tests."""
    return SearchIndex(
        name=index_name,
        fields=[
            _hotel_field(
                "HotelId",
                SearchFieldDataType.STRING,
                key=True,
                searchable=True,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
            _hotel_field(
                "HotelName",
                SearchFieldDataType.STRING,
                searchable=True,
                filterable=False,
                sortable=True,
                facetable=False,
            ),
            _hotel_field(
                "Description",
                SearchFieldDataType.STRING,
                searchable=True,
                filterable=False,
                sortable=False,
                facetable=False,
                analyzer_name="en.lucene",
            ),
            _hotel_field(
                "Description_fr",
                SearchFieldDataType.STRING,
                searchable=True,
                filterable=False,
                sortable=False,
                facetable=False,
                analyzer_name="fr.lucene",
            ),
            _hotel_field(
                "Category",
                SearchFieldDataType.STRING,
                searchable=True,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
            _hotel_field(
                "Tags",
                SearchFieldDataType.Collection(SearchFieldDataType.STRING),
                searchable=True,
                filterable=True,
                sortable=False,
                facetable=True,
            ),
            _hotel_field(
                "ParkingIncluded",
                SearchFieldDataType.BOOLEAN,
                searchable=False,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
            _hotel_field(
                "IsDeleted",
                SearchFieldDataType.BOOLEAN,
                searchable=False,
                filterable=True,
                sortable=True,
                facetable=False,
            ),
            _hotel_field(
                "LastRenovationDate",
                SearchFieldDataType.DATE_TIME_OFFSET,
                searchable=False,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
            _hotel_field(
                "Rating",
                SearchFieldDataType.DOUBLE,
                searchable=False,
                filterable=True,
                sortable=True,
                facetable=True,
            ),
        ],
        suggesters=[
            SearchSuggester(
                name=HOTEL_SUGGESTER_NAME,
                source_fields=["HotelName"],
            )
        ],
    )


def build_hotel_documents(count: int = HOTEL_DOCUMENT_COUNT) -> list[dict[str, Any]]:
    """Return deterministic sample-shaped hotel documents with stable IDs."""
    documents = []
    for document_number in range(1, count + 1):
        document = deepcopy(_HOTEL_DOCUMENTS[(document_number - 1) % HOTEL_DOCUMENT_COUNT])
        document["HotelId"] = str(document_number)
        documents.append(document)
    return documents


def build_hotel_document(
    hotel_id: str,
    *,
    rating: float,
    hotel_name: str = HOTEL_NAME,
) -> dict[str, Any]:
    """Build a single sample-shaped hotel document for indexing action tests."""
    return {
        "HotelId": hotel_id,
        "HotelName": hotel_name,
        "Rating": rating,
        "IsDeleted": False,
    }


def wait_for_live_indexing(test: Any, *, delay_seconds: int = INDEXING_DELAY_SECONDS) -> None:
    if test.is_live:
        time.sleep(delay_seconds)


def wait_for_document_count(test: Any, search_client: Any, expected_count: int) -> None:
    snapshots = poll_until(
        search_client.get_document_count,
        predicate=lambda document_count: document_count == expected_count,
        interval=INDEXING_DELAY_SECONDS if test.is_live else 0,
        attempts=20,
    )
    assert snapshots[-1] == expected_count


def upload_documents(search_client: Any, documents: list[dict[str, Any]]) -> None:
    batch = IndexDocumentsBatch()
    batch.add_upload_actions(documents)
    results = search_client.index_documents(batch)
    assert all(result.succeeded for result in results)


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------


def live_test() -> Callable:
    """Compose the standard live-test decorator stack.

    Equivalent to::

        @SearchEnvVarPreparer()
        @search_decorator()
        @recorded_by_proxy
    """

    def wrap(fn: Callable) -> Callable:
        return SearchEnvVarPreparer()(search_decorator()(recorded_by_proxy(fn)))

    return wrap


# ---------------------------------------------------------------------------
# Context managers (one per resource family)
# ---------------------------------------------------------------------------


@contextmanager
def index_resources(
    test: Any, endpoint: str, *, semantic: bool = False, prefix: str = SEARCH_RESOURCE_PREFIX
) -> Iterator[SearchLiveContext]:
    """Provision one search index. Cleanup deletes it."""
    credential = get_credential()
    index_client = make_index_client(endpoint, credential=credential)
    index_name = test.get_resource_name(f"{prefix}-index")
    index_client.create_index(build_index(index_name, semantic=semantic))
    ctx = SearchLiveContext(credential=credential, index_client=index_client, index_name=index_name)
    try:
        yield ctx
    finally:
        try:
            safe_delete(index_client.delete_index, index_name)
        finally:
            index_client.close()


@contextmanager
def hotel_index(
    test: Any,
    endpoint: str,
    index_name: str,
    *,
    documents: list[dict[str, Any]] | None = None,
    document_count: int | None = None,
) -> Iterator[tuple[Any, list[dict[str, Any]]]]:
    index_client = make_index_client(endpoint)
    search_client = make_search_client(endpoint, index_name)
    index_documents = (
        documents
        if documents is not None
        else build_hotel_documents(document_count or HOTEL_DOCUMENT_COUNT)
    )
    try:
        index_client.create_index(build_hotel_index(index_name))
        upload_documents(search_client, index_documents)
        wait_for_document_count(test, search_client, len(index_documents))
        yield search_client, index_documents
    finally:
        safe_delete(index_client.delete_index, index_name)
        search_client.close()
        index_client.close()


@contextmanager
def hotel_index_with_buffered_sender(
    test: Any,
    endpoint: str,
    index_name: str,
    **sender_kwargs: Any,
) -> Iterator[tuple[Any, SearchIndexingBufferedSender]]:
    with hotel_index(test, endpoint, index_name) as (search_client, _):
        buffered_sender = SearchIndexingBufferedSender(
            endpoint,
            index_name,
            get_credential(),
            retry_backoff_factor=60,
            **sender_kwargs,
        )
        try:
            yield search_client, buffered_sender
        finally:
            buffered_sender.close()


@contextmanager
def knowledge_source_resources(
    test: Any,
    endpoint: str,
    *,
    prefix: str = SEARCH_RESOURCE_PREFIX,
    source_description: str = KNOWLEDGE_SOURCE_DESCRIPTION,
) -> Iterator[SearchLiveContext]:
    """Provision an index + a knowledge source. Cleanup tears down both."""
    credential = get_credential()
    index_client = make_index_client(endpoint, credential=credential)
    index_name = test.get_resource_name(f"{prefix}-index")
    knowledge_source_name = test.get_resource_name(f"{prefix}-source")
    index_create_attempted = False
    source_create_attempted = False
    try:
        index_create_attempted = True
        index_client.create_index(build_index(index_name, semantic=True))
        source_create_attempted = True
        created_source = index_client.create_knowledge_source(
            build_knowledge_source(index_name, knowledge_source_name, description=source_description)
        )
        ctx = SearchLiveContext(
            credential=credential,
            index_client=index_client,
            index_name=index_name,
            knowledge_source_name=knowledge_source_name,
            knowledge_source=created_source,
        )
        yield ctx
    finally:
        try:
            if source_create_attempted:
                safe_delete(index_client.delete_knowledge_source, knowledge_source_name)
            if index_create_attempted:
                safe_delete(index_client.delete_index, index_name)
        finally:
            index_client.close()


@contextmanager
def knowledge_base_resources(
    test: Any,
    endpoint: str,
    *,
    prefix: str = SEARCH_RESOURCE_PREFIX,
    wait_for_active: bool = False,
    description: str = KNOWLEDGE_BASE_DESCRIPTION,
    source_description: str = KNOWLEDGE_SOURCE_DESCRIPTION,
) -> Iterator[SearchLiveContext]:
    """Provision an index + knowledge source + knowledge base.

    If ``wait_for_active`` is true, polls the knowledge source until its
    ``synchronization_status`` reaches ``"active"``.
    """
    credential = get_credential()
    index_client = make_index_client(endpoint, credential=credential)
    index_name = test.get_resource_name(f"{prefix}-index")
    knowledge_source_name = test.get_resource_name(f"{prefix}-source")
    knowledge_base_name = test.get_resource_name(f"{prefix}-base")
    index_create_attempted = False
    source_create_attempted = False
    base_create_attempted = False
    try:
        index_create_attempted = True
        index_client.create_index(build_index(index_name, semantic=True))
        source_create_attempted = True
        created_source = index_client.create_knowledge_source(
            build_knowledge_source(index_name, knowledge_source_name, description=source_description)
        )
        base_create_attempted = True
        created_base = index_client.create_knowledge_base(
            build_knowledge_base(knowledge_base_name, knowledge_source_name, description=description)
        )

        if wait_for_active:
            poll_until(
                lambda: index_client.get_knowledge_source_status(knowledge_source_name),
                predicate=lambda s: s.synchronization_status == "active",
            )

        ctx = SearchLiveContext(
            credential=credential,
            index_client=index_client,
            index_name=index_name,
            knowledge_source_name=knowledge_source_name,
            knowledge_source=created_source,
            knowledge_base_name=knowledge_base_name,
            knowledge_base=created_base,
        )
        yield ctx
    finally:
        try:
            if base_create_attempted:
                safe_delete(index_client.delete_knowledge_base, knowledge_base_name)
            if source_create_attempted:
                safe_delete(index_client.delete_knowledge_source, knowledge_source_name)
            if index_create_attempted:
                safe_delete(index_client.delete_index, index_name)
        finally:
            index_client.close()
