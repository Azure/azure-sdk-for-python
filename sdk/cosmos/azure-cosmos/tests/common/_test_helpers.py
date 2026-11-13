# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Reusable policy builders and response/log observers, independent of legacy setup."""

import logging


def get_vector_indexing_policy(embedding_type):
    return {
        "indexingMode": "consistent",
        "includedPaths": [{"path": "/*"}],
        'excludedPaths': [{'path': '/"_etag"/?'}],
        "vectorIndexes": [
            {"path": "/embedding", "type": f"{embedding_type}"}
        ]
    }


def get_vector_embedding_policy(distance_function, data_type, dimensions):
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
    return {
        "indexingMode": "consistent",
        "includedPaths": [{"path": "/*"}],
        'excludedPaths': [{'path': '/"_etag"/?'}],
        "fullTextIndexes": [
            {"path": path}
        ]
    }


def get_full_text_policy(path):
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
    def __init__(self):
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1


class MockHandler(logging.Handler):

    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record)
