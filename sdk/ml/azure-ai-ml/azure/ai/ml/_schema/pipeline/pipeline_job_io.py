# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import re

from marshmallow import fields, post_load, ValidationError
from azure.ai.ml._schema import PatchedSchemaMeta, UnionField
from azure.ai.ml.constants import ComponentJobConstants

module_logger = logging.getLogger(__name__)


class OutputBindingStr(fields.Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _jsonschema_type_mapping(self):
        schema = {"type": "string", "pattern": ComponentJobConstants.OUTPUT_PATTERN}
        if self.name is not None:
            schema["title"] = self.name
        if self.dump_only:
            schema["readonly"] = True
        return schema

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, str) and re.match(ComponentJobConstants.OUTPUT_PATTERN, value):
            return value
        elif isinstance(value.path, str) and re.match(ComponentJobConstants.OUTPUT_PATTERN, value.path):
            return value.path
        else:
            raise ValidationError(f"Invalid output binding string '{value}' passed")

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, dict) and "path" in value:
            value = value["path"]
        if isinstance(value, str) and re.match(ComponentJobConstants.OUTPUT_PATTERN, value):
            return value
        else:
            raise ValidationError(f"Invalid output binding string '{value}' passed")
