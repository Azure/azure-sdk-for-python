# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Unit tests for rubric-health response models."""

from azure.ai.projects.models import (
    RubricHealth,
    RubricHealthComputationMetadata,
    RubricHealthSimilarityMetric,
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
