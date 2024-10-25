# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from azure.ai.ml.entities._job.distillation.endpoint_request_settings import EndpointRequestSettings
from azure.ai.ml.entities._job.distillation.prompt_settings import PromptSettings
from azure.ai.ml.entities._job.distillation.teacher_model_settings import TeacherModelSettings

from ._distillation import distillation

__all__ = ["distillation", "EndpointRequestSettings", "PromptSettings", "TeacherModelSettings"]
