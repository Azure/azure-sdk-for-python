# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

import logging

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental

module_logger = logging.getLogger(__name__)


@experimental
class AcceleratorMapSchema(metaclass=PatchedSchemaMeta):
    """Schema for AcceleratorMap."""

    accelerator_type = fields.Str(
        required=True,
        metadata={"description": "The type of accelerator (e.g. H100_80GB, H200_141GB, A100_80GB)."},
    )
    number_of_accelerators_per_model_instance = fields.Int(
        required=True,
        metadata={"description": "Number of accelerators per model instance."},
    )
    default = fields.Bool(
        load_default=None,
        metadata={"description": "Whether this is the default accelerator map."},
    )

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._deployment.accelerator_map import AcceleratorMap

        return AcceleratorMap(**data)
