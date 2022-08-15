# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,protected-access

import logging

from marshmallow import fields, post_load

from .schema import YamlFileSchema

module_logger = logging.getLogger(__name__)


class ResourceSchema(YamlFileSchema):
    name = fields.Str(attribute="name")
    id = fields.Str(attribute="id")
    description = fields.Str(attribute="description")
    tags = fields.Dict(keys=fields.Str, attribute="tags")

    @post_load(pass_original=True)
    def pass_source_path(self, data, original, **kwargs):
        path = self.resolve_path(original, base_path=self._previous_base_path)
        if path is not None:
            from ...entities import Resource

            if isinstance(data, dict):
                # data will be used in Resource.__init__
                data["source_path"] = path.as_posix()
            elif isinstance(data, Resource):
                # some resource will make dict into object in their post_load
                # not sure if it's a better way to unify them
                data._source_path = path
        return data
