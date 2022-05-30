# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from marshmallow import fields
from .schema import YamlFileSchema

module_logger = logging.getLogger(__name__)


class ResourceSchema(YamlFileSchema):
    name = fields.Str(attribute="name")
    id = fields.Str(attribute="id")
    description = fields.Str(attribute="description")
    tags = fields.Dict(keys=fields.Str, attribute="tags")
