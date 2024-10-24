# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField
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
        from azure.ai.ml.entities._job.distillation.distillation_types import PromptSettings

        return PromptSettings(**data)


@experimental
class EndpointRequestSettingsSchema(metaclass=PatchedSchemaMeta):
    request_batch_size = fields.Int()
    min_endpoint_success_ratio = fields.Number()

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        """Post-load processing of the schema data

        :param data: Dictionary of parsed values from the yaml.
        :type data: typing.Dict
        :return: EndpointRequestSettings made from the yaml
        :rtype: EndpointRequestSettings
        """
        from azure.ai.ml.entities._job.distillation.distillation_types import EndpointRequestSettings

        return EndpointRequestSettings(**data)


@experimental
class TeacherModelSettingsSchema(metaclass=PatchedSchemaMeta):
    inference_parameters = fields.Dict(keys=fields.Str(), values=fields.Raw())
    endpoint_request_settings = NestedField(EndpointRequestSettingsSchema)

    @post_load
    def make(self, data, **kwargs):  # pylint: disable=unused-argument
        """Post-load processing of the schema data

        :param data: Dictionary of parsed values from the yaml.
        :type data: typing.Dict
        :return: TeacherModelSettings made from the yaml
        :rtype: TeacherModelSettings
        """
        from azure.ai.ml.entities._job.distillation.distillation_types import TeacherModelSettings

        return TeacherModelSettings(**data)
