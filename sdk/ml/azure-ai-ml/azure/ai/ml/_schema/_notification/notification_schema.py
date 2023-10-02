# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from marshmallow import fields, validate, post_load

from azure.ai.ml._schema.core.schema import PatchedSchemaMeta


class NotificationSchema(metaclass=PatchedSchemaMeta):
    email_on = fields.List(
        fields.Str(validate=validate.OneOf(["JobCompleted", "JobFailed", "JobCancelled"])),
        required=True,
        allow_none=False,
    )
    emails = fields.List(fields.Str, required=True, allow_none=False)

    @post_load
    def make(self, data, **kwargs):
        from azure.ai.ml.entities._notification.notification import Notification

        return Notification(**data)
