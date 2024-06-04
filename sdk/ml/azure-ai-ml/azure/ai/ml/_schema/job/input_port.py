# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging

from marshmallow import fields, post_load, validate

from azure.ai.ml.entities import InputPort

from ..core.schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class InputPortSchema(metaclass=PatchedSchemaMeta):
    type_string = fields.Str(
        data_key="type",
        validate=validate.OneOf(["path", "number", "null"]),
        dump_default="null",
    )
    default = fields.Str()
    optional = fields.Bool()

    @post_load
    def make(self, data, **kwargs):
        return InputPort(**data)
