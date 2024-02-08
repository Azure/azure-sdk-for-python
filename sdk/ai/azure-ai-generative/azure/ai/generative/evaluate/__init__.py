# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

try:
    from ._evaluate import evaluate
    from ._evaluation_result import EvaluationResult
except ModuleNotFoundError as ex:
    print("Please make sure evaluate extras is installed. Please run the following command to install "
          "azure-ai-generative[evaluate]")
    raise ex

__all__ = [
    "evaluate",
    "EvaluationResult"
]
