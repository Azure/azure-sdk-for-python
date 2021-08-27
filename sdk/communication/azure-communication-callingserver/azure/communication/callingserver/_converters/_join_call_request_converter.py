# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .._models import JoinCallOptions
from .._shared.models import CommunicationIdentifier
from .._generated.models import JoinCallRequest

class JoinCallRequestConverter(object):
    @classmethod
    def convert(self, source: CommunicationIdentifier, join_call_options: JoinCallOptions):
        if not source:
            raise ValueError("source can not be None")
        if not join_call_options:
            raise ValueError("join_call_options can not be None")

        return JoinCallRequest(
            source=source,
            callback_uri=join_call_options.callback_uri,
            requested_media_types=join_call_options.requested_media_types,
            requested_call_events=join_call_options.requested_call_events,
            subject= join_call_options.subject)