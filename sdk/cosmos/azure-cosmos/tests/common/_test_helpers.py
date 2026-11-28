# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared test helpers:

- functions that build container settings for vector and full-text search;
- ResponseHookCaller, a response hook that counts how many responses the SDK received;
- MockHandler, a log handler that saves every log entry so a test can check what the SDK logged.
"""

import logging


def get_vector_indexing_policy(embedding_type):
    """Indexing policy that indexes every path and adds a vector index of the
    given type (for example "flat" or "diskANN") on /embedding."""
    return {
        "indexingMode": "consistent",
        "includedPaths": [{"path": "/*"}],
        'excludedPaths': [{'path': '/"_etag"/?'}],
        "vectorIndexes": [
            {"path": "/embedding", "type": f"{embedding_type}"}
        ]
    }


def get_vector_embedding_policy(distance_function, data_type, dimensions):
    """Vector embedding policy for /embedding: how vectors are compared, the
    number type they use, and how many numbers each vector holds."""
    return {
        "vectorEmbeddings": [
            {
                "path": "/embedding",
                "dataType": f"{data_type}",
                "dimensions": dimensions,
                "distanceFunction": f"{distance_function}"
            }
        ]
    }


def get_full_text_indexing_policy(path):
    """Indexing policy that indexes every path and adds a full-text index on ``path``."""
    return {
        "indexingMode": "consistent",
        "includedPaths": [{"path": "/*"}],
        'excludedPaths': [{'path': '/"_etag"/?'}],
        "fullTextIndexes": [
            {"path": path}
        ]
    }


def get_full_text_policy(path):
    """Full-text policy that treats the text at ``path`` as English (en-US)."""
    return {
        "defaultLanguage": "en-US",
        "fullTextPaths": [
            {
                "path": path,
                "language": "en-US"
            }
        ]
    }


class ResponseHookCaller:
    """Response hook that counts how many times the SDK calls it."""

    def __init__(self):
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1


class MockHandler(logging.Handler):
    """Log handler that saves every log entry in ``records``."""

    def __init__(self):
        super(MockHandler, self).__init__()
        self.records = []

    def reset(self):
        self.records = []

    def emit(self, record):
        self.records.append(record)