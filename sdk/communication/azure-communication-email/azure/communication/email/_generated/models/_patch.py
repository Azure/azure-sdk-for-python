# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import msrest.serialization

class SendEmailResult(msrest.serialization.Model):
    """Results of a sent email.

    All required parameters must be populated in order to send to Azure.

    :ivar message_id: System generated id of an email message sent. Required.
    :vartype message_id: str
    """

    _validation = {
        'message_id': {'required': True},
    }

    _attribute_map = {
        "message_id": {"key": "messageId", "type": "str"},
    }

    def __init__(
        self,
        **kwargs
    ):
        """
        :keyword message_id: System generated id of an email message sent. Required.
        :paramtype message_id: str
        """
        super(SendEmailResult, self).__init__(**kwargs)
        self.message_id = kwargs['message_id']

__all__ = ["SendEmailResult"]  # type: List[str]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
