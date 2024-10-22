# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains distillation classes for Azure Machine Learning SDKv2."""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from azure.ai.ml.entities._job.distillation import EndpointRequestSettings, PromptSettings, TeacherModelSettings

__all__ = ["PromptSettings", "EndpointRequestSettings", "TeacherModelSettings"]
