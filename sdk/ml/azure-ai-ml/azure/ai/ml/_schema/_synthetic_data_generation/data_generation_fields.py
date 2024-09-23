# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields

from azure.ai.ml._utils._experimental import experimental


@experimental
class EndpointNameSchema:
    teacher_model_endpoint_name = fields.Str(required=True)


@experimental
class EndpointRequestSettingsSchema:
    request_batch_size = fields.Int()
    min_endpoint_success_ratio = fields.Number()
