# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from marshmallow import fields, post_dump

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

    @post_dump
    def simplify_blocks(self, data, **kwargs):  # pylint: disable=unused-argument, no-self-use
        # simplify true_block and false_block to single node if there is only one node in the list
        # this is to make sure the request to backend won't change after we support list true/false blocks
        block_keys = ["true_block", "false_block"]
        for block in block_keys:
            if isinstance(data.get(block), list) and len(data.get(block)) == 1:
                data[block] = data.get(block)[0]
        return data
