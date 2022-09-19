# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import fields, post_load

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY

from .asset import AssetSchema

module_logger = logging.getLogger(__name__)


class WorkspaceModelReferenceSchema(AssetSchema):
    destination_name = fields.Str()
    destination_version = fields.Str()
    source_asset_id = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets import WorkspaceModelReference

        return WorkspaceModelReference(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
