# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Any

from marshmallow import post_load, fields

from azure.ai.ml._schema import PatchedSchemaMeta, StringTransformedEnum, NestedField, UnionField
from azure.ai.ml._schema._deployment.online.data_asset_schema import DataAssetSchema
from azure.ai.ml.constants._common import Boolean

module_logger = logging.getLogger(__name__)


class DeploymentCollectionSchema(metaclass=PatchedSchemaMeta):
    enabled = StringTransformedEnum(required=True, allowed_values=[Boolean.TRUE, Boolean.FALSE])
    data = UnionField(
        [
            fields.Str(),
            NestedField(DataAssetSchema),
        ]
    )
    client_id = fields.Str()

    # pylint: disable=unused-argument,no-self-use
    @post_load
    def make(self, data: Any, **kwargs: Any) -> Any:
        from azure.ai.ml.entities._deployment.deployment_collection import DeploymentCollection

        return DeploymentCollection(**data)
