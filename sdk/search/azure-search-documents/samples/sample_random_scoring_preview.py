# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
DESCRIPTION:
    Configure seeded and unseeded random scoring profiles. Verify repeatability,
    different seeds, signed 64-bit seed boundaries, paging, filtering, result
    counts, and the error returned when a required seed is omitted.
    Follows the core index/search scenarios in random-score-fn.http.

USAGE:
    python sample_random_scoring_preview.py

    Set AZURE_SEARCH_SERVICE_ENDPOINT and optionally AZURE_SEARCH_API_KEY.
    Requires 2026-11-01-preview and one free index slot; no model deployment.
    Only the newly created sample index is deleted, including on failure.
    This is not the HTTP file's exhaustive validation or API-version test suite.
"""

import math
import os
import time
import uuid
from typing import Any

from sample_utils import cleanup_preview_resources, get_sample_run_tag


def main():  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
    # [START sample_random_scoring_preview]
    from azure.core import MatchConditions
    from azure.core.credentials import AzureKeyCredential
    from azure.core.exceptions import HttpResponseError
    from azure.identity import DefaultAzureCredential
    from azure.search.documents import ApiVersion, SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        RandomScoringFunction,
        RandomScoringParameters,
        ScoringProfile,
        SearchIndex,
        SearchableField,
        SimpleField,
    )

    endpoint = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
    name = f"hotels-random-{get_sample_run_tag()}-{uuid.uuid4().hex[:6]}"
    documents: list[dict[str, Any]] = [
        {"id": str(i), "title": "hotel alpha", "rating": (i - 1) % 5 + 1} for i in range(1, 21)
    ]
    expected_ids = {document["id"] for document in documents}
    created: list[tuple[str, str]] = []
    with DefaultAzureCredential(process_timeout=60) as identity:
        key = os.environ.get("AZURE_SEARCH_API_KEY")
        credential = AzureKeyCredential(key) if key else identity
        with SearchIndexClient(endpoint, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as indexes:
            try:
                indexes.create_or_update_index(
                    SearchIndex(
                        name=name,
                        fields=[
                            SimpleField(name="id", type="Edm.String", key=True, filterable=True, sortable=True),
                            SearchableField(name="title", type="Edm.String"),
                            SimpleField(name="rating", type="Edm.Int32", filterable=True, sortable=True),
                        ],
                        scoring_profiles=[
                            ScoringProfile(name="randomUnseeded", functions=[RandomScoringFunction()]),
                            ScoringProfile(
                                name="randomSeeded",
                                functions=[
                                    RandomScoringFunction(
                                        parameters=RandomScoringParameters(seed_parameter="randomSeed")
                                    )
                                ],
                            ),
                            ScoringProfile(
                                name="randomSeededB",
                                functions=[
                                    RandomScoringFunction(
                                        parameters=RandomScoringParameters(seed_parameter="otherSeed")
                                    )
                                ],
                            ),
                        ],
                    ),
                    match_condition=MatchConditions.IfMissing,
                )
                created.append(("index", name))
                stored = indexes.get_index(name)
                unseeded_profile = next(
                    (profile for profile in stored.scoring_profiles or [] if profile.name == "randomUnseeded"), None
                )
                if unseeded_profile is None or not unseeded_profile.functions:
                    raise RuntimeError("The unseeded random-scoring profile did not round-trip.")
                function = unseeded_profile.functions[0].as_dict()
                if {key: value for key, value in function.items() if value is not None} != {"type": "random"}:
                    raise RuntimeError(
                        "Unseeded random scoring must round-trip without fieldName, boost or parameters."
                    )
                with SearchClient(endpoint, name, credential, api_version=ApiVersion.V2026_11_01_PREVIEW) as search:
                    if not all(result.succeeded for result in search.upload_documents(documents)):
                        raise RuntimeError("Some hotel documents could not be uploaded.")
                    for _ in range(30):
                        if search.get_document_count() == len(documents):
                            break
                        time.sleep(2)
                    else:
                        raise TimeoutError("The hotel documents did not become searchable within 60 seconds.")

                    def seeded(seed):
                        return list(
                            search.search(
                                search_text="hotel",
                                scoring_profile="randomSeeded",
                                scoring_parameters=[f"randomSeed-{seed}"],
                                select=["id"],
                                top=20,
                            )
                        )

                    first = seeded(12345)
                    ids = [row["id"] for row in first]
                    if len(ids) != 20 or set(ids) != expected_ids:
                        raise RuntimeError("Seeded scoring must return every hotel exactly once.")
                    if any(not math.isfinite(row["@search.score"]) for row in first):
                        raise RuntimeError("Random scores must be finite.")
                    if first != seeded(12345):
                        raise RuntimeError("The same seed must preserve both document order and scores.")
                    if ids == [row["id"] for row in seeded(98765)]:
                        raise RuntimeError("The two demonstrated seeds did not produce different orders.")
                    print("Seeded hotel order:", ids)

                    unseeded_orders = []
                    for _ in range(3):
                        rows = list(
                            search.search(search_text="hotel", scoring_profile="randomUnseeded", select=["id"], top=20)
                        )
                        order = tuple(row["id"] for row in rows)
                        if len(order) != 20 or set(order) != expected_ids:
                            raise RuntimeError("Unseeded scoring must preserve the complete result set.")
                        unseeded_orders.append(order)
                    print("Distinct unseeded orders across three requests:", len(set(unseeded_orders)))

                    for seed in (0, -42, 9223372036854775807, -9223372036854775808):
                        rows = seeded(seed)
                        if rows != seeded(seed) or len(rows) != 20 or {row["id"] for row in rows} != expected_ids:
                            raise RuntimeError(f"Signed 64-bit seed {seed} did not return stable, complete results.")

                    pages: list[dict[str, Any]] = []
                    for offset in range(0, 20, 5):
                        pages.extend(
                            search.search(
                                search_text="hotel",
                                scoring_profile="randomSeeded",
                                scoring_parameters=["randomSeed-12345"],
                                select=["id"],
                                top=5,
                                skip=offset,
                            )
                        )
                    if [row["id"] for row in pages] != ids:
                        raise RuntimeError("Fixed-seed pages must reconstruct the original order without duplicates.")
                    filtered = list(
                        search.search(
                            search_text="hotel",
                            scoring_profile="randomSeeded",
                            scoring_parameters=["randomSeed-12345"],
                            filter="rating ge 4",
                            select=["id", "rating"],
                            top=20,
                        )
                    )
                    eligible = {document["id"] for document in documents if document["rating"] >= 4}
                    if [row["id"] for row in filtered] != [doc_id for doc_id in ids if doc_id in eligible]:
                        raise RuntimeError("Filtering must preserve the relative seeded order.")
                    counted = search.search(
                        search_text="hotel",
                        scoring_profile="randomSeeded",
                        scoring_parameters=["randomSeed-12345"],
                        select=["id"],
                        top=50,
                        include_total_count=True,
                    )
                    if [row["id"] for row in counted] != ids or counted.get_count() != 20:
                        raise RuntimeError("The result count must agree with the complete seeded result set.")
                    alternate = list(
                        search.search(
                            search_text="hotel",
                            scoring_profile="randomSeededB",
                            scoring_parameters=["otherSeed-12345"],
                            select=["id"],
                            top=20,
                        )
                    )
                    if len(alternate) != 20 or {row["id"] for row in alternate} != expected_ids:
                        raise RuntimeError("The alternate profile must use its own declared seed parameter.")
                    try:
                        list(search.search(search_text="hotel", scoring_profile="randomSeeded", select=["id"]))
                    except HttpResponseError as error:
                        if error.status_code != 400:
                            raise
                        print("Omitting the declared seed correctly returned HTTP 400.")
                    else:
                        raise RuntimeError("A seeded profile must reject a query without its declared seed.")
                    print("Random-scoring seed boundaries, paging, filtering and counts verified.")
            finally:
                cleanup_preview_resources(indexes, created)
    # [END sample_random_scoring_preview]


if __name__ == "__main__":
    main()
