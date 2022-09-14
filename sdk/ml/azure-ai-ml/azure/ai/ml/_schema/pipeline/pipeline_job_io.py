# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
import re

from marshmallow import ValidationError, fields

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
        # _to_job_output in io.py will return Output, add this branch to judge whether original value is a simple binding or Output
        elif (
            isinstance(value.path, str)
            and re.match(ComponentJobConstants.OUTPUT_PATTERN, value.path)
            and value.mode is None
        ):
            return value.path
        else:
            raise ValidationError(f"Invalid output binding string '{value}' passed")

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, dict) and "path" in value and "mode" not in value:
            value = value["path"]
        if isinstance(value, str) and re.match(ComponentJobConstants.OUTPUT_PATTERN, value):
            return value
        else:
            raise ValidationError(f"Invalid output binding string '{value}' passed")
