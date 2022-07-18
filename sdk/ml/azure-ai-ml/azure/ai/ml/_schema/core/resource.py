# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from marshmallow import fields, post_load, pre_load
from .schema import YamlFileSchema
from ...constants import SOURCE_PATH_CONTEXT_KEY

module_logger = logging.getLogger(__name__)


class ResourceSchema(YamlFileSchema):
    name = fields.Str(attribute="name")
    id = fields.Str(attribute="id")
    description = fields.Str(attribute="description")
    tags = fields.Dict(keys=fields.Str, attribute="tags")

    @post_load
    def pass_source_path(self, data, **kwargs):
        from ...entities import Resource

        if isinstance(data, dict):
            # data will be used in Resource.__init__
            data["source_path"] = self.context[SOURCE_PATH_CONTEXT_KEY]
        elif isinstance(data, Resource):
            # some resource will make dict into object in their post_load
            # not sure if it's a better way to unify them
            data._set_source_path(self.context[SOURCE_PATH_CONTEXT_KEY])
        return data
