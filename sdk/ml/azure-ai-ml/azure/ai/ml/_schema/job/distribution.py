# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import copy
import logging

from marshmallow import fields, post_load, pre_dump

from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml.constants import DistributionType

from ..core.schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class BaseDistributionSchema:
    @pre_dump
    def pre_dump_override(self, data, **kwargs):
        # copy a DistributionConfiguration and set type for the object to avoid using as_dict(), which will do strict
        # type checking and block data binding
        copy_data = copy.deepcopy(data)
        if copy_data.distribution_type is not None:
            copy_data.type = copy_data.distribution_type.lower()
        return copy_data


class MPIDistributionSchema(BaseDistributionSchema, metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=DistributionType.MPI)
    process_count_per_instance = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml import MpiDistribution

        data.pop("type", None)
        return MpiDistribution(**data)


class TensorFlowDistributionSchema(BaseDistributionSchema, metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=DistributionType.TENSORFLOW)
    parameter_server_count = fields.Int()
    worker_count = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml import TensorFlowDistribution

        data.pop("type", None)
        return TensorFlowDistribution(**data)


class PyTorchDistributionSchema(BaseDistributionSchema, metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=DistributionType.PYTORCH)
    process_count_per_instance = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml import PyTorchDistribution

        data.pop("type", None)
        return PyTorchDistribution(**data)
