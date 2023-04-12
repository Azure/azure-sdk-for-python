# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class AlertNotificationSchema(metaclass=PatchedSchemaMeta):
    azure_monitoring_signals = fields.Dict(keys=fields.Str, values=fields.Str)
    emails = fields.List(fields.Str)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._monitoring.alert_notification import AlertNotification

        return AlertNotification(**data)
