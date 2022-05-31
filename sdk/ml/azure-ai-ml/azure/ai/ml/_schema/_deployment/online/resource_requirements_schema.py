# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from azure.ai.ml._schema import PatchedSchemaMeta
from azure.ai.ml._schema import NestedField
from .resource_settings_schema import ResourceSettingsSchema
from marshmallow import fields, post_load

module_logger = logging.getLogger(__name__)


class ResourceRequirementsSchema(metaclass=PatchedSchemaMeta):
    requests = NestedField(ResourceSettingsSchema)
    limits = NestedField(ResourceSettingsSchema)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> "ResourceRequirementsSettings":
        from azure.ai.ml.entities import ResourceRequirementsSettings

        return ResourceRequirementsSettings(**data)
