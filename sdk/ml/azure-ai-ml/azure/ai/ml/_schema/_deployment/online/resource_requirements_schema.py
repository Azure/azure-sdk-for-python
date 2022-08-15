# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import post_load

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta

from .resource_settings_schema import ResourceSettingsSchema

module_logger = logging.getLogger(__name__)


class ResourceRequirementsSchema(metaclass=PatchedSchemaMeta):
    requests = NestedField(ResourceSettingsSchema)
    limits = NestedField(ResourceSettingsSchema)

    @post_load
    def make(self, data: Any, **kwargs: Any) -> "ResourceRequirementsSettings":
        from azure.ai.ml.entities import ResourceRequirementsSettings

        return ResourceRequirementsSettings(**data)
