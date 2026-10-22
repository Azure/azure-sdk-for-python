# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load

from azure.ai.ml._schema._distillation.endpoint_request_settings import EndpointRequestSettingsSchema
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental


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
        from azure.ai.ml.entities._job.distillation.teacher_model_settings import TeacherModelSettings

        return TeacherModelSettings(**data)
