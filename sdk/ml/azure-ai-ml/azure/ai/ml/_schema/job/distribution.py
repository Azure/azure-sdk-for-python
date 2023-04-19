# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

import logging

from marshmallow import ValidationError, fields, post_load, pre_dump

from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml.constants import DistributionType
from azure.ai.ml._utils._experimental import experimental

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


@experimental
class RayDistributionSchema(metaclass=PatchedSchemaMeta):
    type = StringTransformedEnum(required=True, allowed_values=DistributionType.RAY)
    port = fields.Int()
    address = fields.Str()
    include_dashboard = fields.Bool()
    dashboard_port = fields.Int()
    head_node_additional_args = fields.Str()
    worker_node_additional_args = fields.Str()

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml import RayDistribution

        data.pop("type", None)
        return RayDistribution(**data)

    @pre_dump
    def predump(self, data, **kwargs):
        from azure.ai.ml import RayDistribution

        if not isinstance(data, RayDistribution):
            raise ValidationError("Cannot dump non-RayDistribution object into RayDistributionSchema")
        return data
