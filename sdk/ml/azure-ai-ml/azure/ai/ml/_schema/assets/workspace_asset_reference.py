# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging

from marshmallow import fields, post_load

from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY

from .asset import AssetSchema

module_logger = logging.getLogger(__name__)


class WorkspaceAssetReferenceSchema(AssetSchema):
    destination_name = fields.Str()
    destination_version = fields.Str()
    source_asset_id = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._assets.workspace_asset_reference import WorkspaceAssetReference

        return WorkspaceAssetReference(base_path=self.context[BASE_PATH_CONTEXT_KEY], **data)
