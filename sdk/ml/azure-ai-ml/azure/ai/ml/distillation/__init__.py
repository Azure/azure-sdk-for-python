# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains distillation classes for Azure Machine Learning SDKv2."""

from azure.ai.ml.entities._job.distillation import EndpointRequestSettings, PromptSettings, TeacherModelSettings

__all__ = ["PromptSettings", "EndpointRequestSettings", "TeacherModelSettings"]
