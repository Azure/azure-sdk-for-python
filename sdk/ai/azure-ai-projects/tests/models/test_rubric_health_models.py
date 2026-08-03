# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Unit tests for rubric-health response models."""

from azure.ai.projects.models import (
    DimensionChangeKind,
    DimensionMetadata,
    RubricHealth,
    RubricHealthComputationMetadata,
    RubricHealthSimilarityMetric,
    SupersededDimension,
)


def test_rubric_health_deserializes_computation_metadata():
    health = RubricHealth(
        {
            "confidence": "low",
            "computation": {
                "algorithm_version": "1",
                "vectorizer": "local_tfidf_feature_hashing",
                "vectorizer_version": "1",
                "similarity_metric": "cosine",
            },
        }
    )

    assert isinstance(
        health.computation,
        RubricHealthComputationMetadata,
    )
    assert health.computation.algorithm_version == "1"
    assert health.computation.vectorizer == "local_tfidf_feature_hashing"
    assert health.computation.vectorizer_version == "1"
    assert health.computation.similarity_metric == RubricHealthSimilarityMetric.COSINE


def test_rubric_health_accepts_future_similarity_metric():
    health = RubricHealth(
        {
            "computation": {
                "algorithm_version": "2",
                "vectorizer": "future_vectorizer",
                "similarity_metric": "future_metric",
            },
        }
    )

    assert health.computation is not None
    assert health.computation.similarity_metric == "future_metric"


def test_superseded_dimension_deserializes_full_snapshot():
    superseded = SupersededDimension(
        {
            "id": "policy_compliance",
            "description": "The response follows support policy.",
            "weight": 7,
            "always_applicable": True,
            "metadata": {
                "origin_version": "1",
                "last_modified_version": "2",
                "change_kind": "human_edited",
                "change_detail": "Edited before removal.",
            },
            "reason": "human_removed",
        }
    )

    assert superseded.id == "policy_compliance"
    assert superseded.description == "The response follows support policy."
    assert superseded.weight == 7
    assert superseded.always_applicable is True
    assert isinstance(superseded.metadata, DimensionMetadata)
    assert superseded.metadata.change_kind == DimensionChangeKind.HUMAN_EDITED
    assert superseded.reason == "human_removed"


def test_superseded_dimension_accepts_future_change_kind():
    superseded = SupersededDimension(
        {
            "id": "future_dimension",
            "description": "A future dimension.",
            "weight": 3,
            "metadata": {
                "origin_version": "1",
                "last_modified_version": "2",
                "change_kind": "future_change_kind",
            },
            "reason": "future_reason",
        }
    )

    assert superseded.metadata is not None
    assert superseded.metadata.change_kind == "future_change_kind"
