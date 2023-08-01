# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging
from marshmallow import fields, post_load
from azure.ai.ml._schema.core.schema import PathAwareSchema


module_logger = logging.getLogger(__name__)


class BaseEnvironmentSourceSchema(PathAwareSchema):
    type = fields.Str()
    resource_id = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities import BaseEnvironment

        return BaseEnvironment(**data)
