# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,bad-mcs-method-argument

import logging
from marshmallow import fields, post_load
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class RouteSchema(PatchedSchemaMeta):
    port = fields.Str()
    path = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets._artifacts._package.inferencing_server import Route

        return Route(**data)
