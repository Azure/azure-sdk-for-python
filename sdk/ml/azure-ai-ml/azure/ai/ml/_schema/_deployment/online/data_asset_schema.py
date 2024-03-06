# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


import logging
from typing import Any

from marshmallow import fields, post_load

from azure.ai.ml._schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class DataAssetSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str()
    path = fields.Str()
    version = fields.Str()
    data_id = fields.Str()

    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:  # pylint: disable=unused-argument
        from azure.ai.ml.entities._deployment.data_asset import DataAsset

        return DataAsset(**data)
