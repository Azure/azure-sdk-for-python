# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from azure.ai.ml.entities._job.distillation.distillation_types import (
    EndpointRequestSettings,
    PromptSettings,
    TeacherModelSettings,
)

__all__ = ["PromptSettings", "EndpointRequestSettings", "TeacherModelSettings"]
