# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Azure Inference Service client library."""

from ._inference_service_client import InferenceServiceClient
from ._version import VERSION

__version__ = VERSION

__all__ = ["InferenceServiceClient"]
