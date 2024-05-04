# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AzureML Retrieval Augmented Generation (RAG) utilities."""

from ._acs import _get_azuresearch_module_instance
from ._models import build_model_protocol
from ._open_ai_utils import build_open_ai_protocol, build_connection_id
from ._pipeline_decorator import pipeline
from ._requests import send_post_request

__all__ = [
    "_get_azuresearch_module_instance"
    "build_model_protocol",
    "build_open_ai_protocol",
    "build_connection_id",
    "pipeline",
    "send_post_request"
]
