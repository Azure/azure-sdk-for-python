# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,protected-access

import logging
from pathlib import Path

from marshmallow import fields, post_load, pre_dump, post_dump

from .schema import YamlFileSchema
from ...constants._common import BASE_PATH_CONTEXT_KEY

module_logger = logging.getLogger(__name__)


class ResourceSchema(YamlFileSchema):
    name = fields.Str(attribute="name")
    id = fields.Str(attribute="id")
    description = fields.Str(attribute="description")
    tags = fields.Dict(keys=fields.Str, attribute="tags")

    @post_load(pass_original=True)
    def pass_source_path(self, data, original, **kwargs):
        path = self._resolve_path(original, base_path=self._previous_base_path)
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

    @pre_dump
    def update_base_path_pre_dump(self, data, **kwargs):
        # inherit from parent if base_path is not set
        if data.base_path:
            cur_base_path: Path = Path(data.base_path).resolve()
            if not cur_base_path.samefile(self.context[BASE_PATH_CONTEXT_KEY]):
                self._previous_base_path = Path(self.context[BASE_PATH_CONTEXT_KEY])
                self.context[BASE_PATH_CONTEXT_KEY] = cur_base_path
        return data

    @post_dump
    def reset_base_path_post_dump(self, data, **kwargs):
        if self._previous_base_path is not None:
            # pop state
            self.context[BASE_PATH_CONTEXT_KEY] = self._previous_base_path
        return data
