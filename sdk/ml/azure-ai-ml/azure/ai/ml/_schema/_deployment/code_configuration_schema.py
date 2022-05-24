# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from azure.ai.ml._schema import NestedField, PathAwareSchema, UnionField
from azure.ai.ml._schema.assets.code_asset import CodeAssetSchema
from azure.ai.ml._schema.core.fields import ArmVersionedStr
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, AzureMLResourceType, EndpointYamlFields
from marshmallow import fields, post_load, validates_schema, ValidationError

module_logger = logging.getLogger(__name__)


class CodeConfigurationSchema(PathAwareSchema):
    code = fields.Str()
    scoring_script = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities import CodeConfiguration

        return CodeConfiguration(**data)
