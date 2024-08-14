# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

class GenerativeAIPackage(str, Enum):
    """An enumeration class to represent the packages that provide generative AI traces."""

    INFERENCE = "azure.ai.inference"


def start_generative_ai_traces(package_name: GenerativeAIPackage, enable_content_tracing: bool=False):
    """This function starts generative AI traces for the requested package.

    Args:
        package_name (GenerativeAIPackage): The pacakge for which generative AI tracing is to be started.
        enable_content_tracing (enable_content_tracing, optional): Configures whether the message content gets traced as part of the generative AI traces for the specific pacakge
                                                                   for which tracing is being started as specified in the pacakge_name parameter.
                                                                   Note that this value is package specific, in other words, the value passed in will only apply for the specific
                                                                   package for which the traces are requested to be started and will not have an impact on any traces previously started
                                                                   for other packages.
                                                                   Defaults to False.

    Raises:
        RuntimeError: If traces for the requested package have already been started.
        ValueError: The specified package does not support generative AI traces.
    """
    if package_name == GenerativeAIPackage.INFERENCE:
        from ._inference_api_injector import _inject_inference_api
        _inject_inference_api(enable_content_tracing)
    else:
        raise ValueError("The specified package does not support generative AI traces")


def stop_generative_ai_traces(package_name: GenerativeAIPackage):
    """This function stops tracing for the generative AI pacakge.

    Args:
        package_name (GenerativeAIPackage): The pacakge for which tracing is to be stopped.

    Raises:
        ValueError: The specified package does not support generative AI traces.        
    """
    if package_name == GenerativeAIPackage.INFERENCE:
        from ._inference_api_injector import _restore_inference_api
        _restore_inference_api()
    else:
        raise ValueError("The specified package does not support generative AI traces")
