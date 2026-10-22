# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from azure.ai.ml.dsl._pipeline_decorator import pipeline

__all__ = ["pipeline"]
