# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml.constants import DistributionType

from ..core.schema import PatchedSchemaMeta

module_logger = logging.getLogger(__name__)


class MPIDistributionSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=DistributionType.MPI)
    process_count_per_instance = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml import MpiDistribution

        data.pop("type", None)
        return MpiDistribution(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml import MpiDistribution

        if not isinstance(data, MpiDistribution):
            raise ValidationError("Cannot dump non-MpiDistribution object into MpiDistributionSchema")
        return data


class TensorFlowDistributionSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=DistributionType.TENSORFLOW)
    parameter_server_count = fields.Int()
    worker_count = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml import TensorFlowDistribution

        data.pop("type", None)
        return TensorFlowDistribution(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml import TensorFlowDistribution

        if not isinstance(data, TensorFlowDistribution):
            raise ValidationError("Cannot dump non-TensorFlowDistribution object into TensorFlowDistributionSchema")
        return data


class PyTorchDistributionSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=DistributionType.PYTORCH)
    process_count_per_instance = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml import PyTorchDistribution

        data.pop("type", None)
        return PyTorchDistribution(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml import PyTorchDistribution

        if not isinstance(data, PyTorchDistribution):
            raise ValidationError("Cannot dump non-PyTorchDistribution object into PyTorchDistributionSchema")
        return data
