# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental


@experimental
class PromptSettingsSchema(metaclass=PatchedSchemaMeta):
    enable_chain_of_thought = fields.Bool()
    enable_chain_of_density = fields.Bool()
    max_len_summary = fields.Int()
    # custom_prompt = fields.Str()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        """Post-load processing of the schema data

        :param data: Dictionary of parsed values from the yaml.
        :type data: typing.Dict
        :return: PromptSettings made from the yaml
        :rtype: PromptSettings
        """
        from azure.ai.ml.entities._job.distillation.prompt_settings import PromptSettings

        return PromptSettings(**data)
