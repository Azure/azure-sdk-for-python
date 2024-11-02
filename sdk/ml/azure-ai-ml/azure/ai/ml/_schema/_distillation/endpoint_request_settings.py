# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta
from azure.ai.ml._utils._experimental import experimental


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
        from azure.ai.ml.entities._job.distillation.endpoint_request_settings import EndpointRequestSettings

        return EndpointRequestSettings(**data)
