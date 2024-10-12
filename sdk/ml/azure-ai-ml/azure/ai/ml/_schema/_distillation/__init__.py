# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from .distillation_job import DistillationJobSchema
from .distillation_types import DistillationPromptSettingsSchema

__all__ = ["DistillationJobSchema", "DistillationPromptSettingsSchema"]
