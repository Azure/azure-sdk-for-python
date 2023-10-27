# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NumberVersionField, StringTransformedEnum, UnionField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta


class SparkResourceConfigurationSchema(metaclass=PatchedSchemaMeta):
    """Schema for SparkResourceConfiguration."""

    instance_type = fields.Str(metadata={"description": "Optional type of VM used as supported by the compute target."})
    runtime_version = UnionField([fields.Str(), fields.Number()])

    @post_load
    def make(self, data, **kwargs):
        """Construct a SparkResourceConfiguration object from the marshalled data.

        :param data: The marshalled data.
        :type data: dict[str, str]
        :return: A SparkResourceConfiguration object.
        :rtype: :class:`~azure.ai.ml.entities.SparkResourceConfiguration`
        """
        from azure.ai.ml.entities import SparkResourceConfiguration

        return SparkResourceConfiguration(**data)


class SparkResourceConfigurationForNodeSchema(SparkResourceConfigurationSchema):
    """
    Schema for SparkResourceConfiguration, used for node configuration, where we need to move validation logic to
    schema.
    """

    instance_type = StringTransformedEnum(
        allowed_values=[
            "standard_e4s_v3",
            "standard_e8s_v3",
            "standard_e16s_v3",
            "standard_e32s_v3",
            "standard_e64s_v3",
        ],
        required=True,
        metadata={"description": "Optional type of VM used as supported by the compute target."},
    )
    runtime_version = NumberVersionField(
        upper_bound="3.4",
        lower_bound="3.2",
        required=True,
    )
