# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from typing import Any

from marshmallow import fields, post_load, pre_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._schema._utils.utils import replace_key_in_odict

module_logger = logging.getLogger(__name__)


class ResourceSettingsSchema(metaclass=PatchedSchemaMeta):
    cpu = fields.String()
    memory = fields.String()
    gpu = fields.String()

    @pre_load
    def conversion(self, data: Any, **kwargs) -> Any:
        data = replace_key_in_odict(data, "nvidia.com/gpu", "gpu")
        return data

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import ResourceSettings

        return ResourceSettings(**data)
