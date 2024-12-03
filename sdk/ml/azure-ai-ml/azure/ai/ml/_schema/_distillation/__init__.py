# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from .distillation_job import DistillationJobSchema
from .endpoint_request_settings import EndpointRequestSettingsSchema
from .prompt_settings import PromptSettingsSchema
from .teacher_model_settings import TeacherModelSettingsSchema

__all__ = [
    "DistillationJobSchema",
    "PromptSettingsSchema",
    "EndpointRequestSettingsSchema",
    "TeacherModelSettingsSchema",
]
