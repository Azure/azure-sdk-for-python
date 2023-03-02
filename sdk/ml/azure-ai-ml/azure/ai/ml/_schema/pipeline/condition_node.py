# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields

from azure.ai.ml._schema import StringTransformedEnum
from azure.ai.ml._schema.core.fields import DataBindingStr, NodeBindingStr, UnionField
from azure.ai.ml._schema.pipeline.control_flow_job import ControlFlowSchema
from azure.ai.ml.constants._component import ControlFlowType


# ConditionNodeSchema did not inherit from BaseNodeSchema since it doesn't have inputs/outputs like other nodes.
class ConditionNodeSchema(ControlFlowSchema):
    type = StringTransformedEnum(allowed_values=[ControlFlowType.IF_ELSE])
    condition = UnionField([DataBindingStr(), fields.Bool()])
    true_block = UnionField([NodeBindingStr(), fields.List(NodeBindingStr())])
    false_block = UnionField([NodeBindingStr(), fields.List(NodeBindingStr())])
