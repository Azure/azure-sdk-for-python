# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging
from marshmallow import fields
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class RouteSchema(PatchedSchemaMeta):
    port = fields.Str()
    path = fields.Str()
