# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from marshmallow import fields, post_load, validate
from ..core.schema import PatchedSchemaMeta
from azure.ai.ml.entities import InputPort

module_logger = logging.getLogger(__name__)


class InputPortSchema(metaclass=PatchedSchemaMeta):
    type_string = fields.Str(
        data_key="type", name="type", validate=validate.OneOf(["path", "number", "null"]), default="null"
    )
    default = fields.Str()
    optional = fields.Bool()

    @post_load
    def make(self, data, **kwargs):
        return InputPort(**data)
