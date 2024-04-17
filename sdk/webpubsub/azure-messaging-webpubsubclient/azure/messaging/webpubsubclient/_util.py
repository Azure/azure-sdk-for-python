# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from typing import Optional, Any
from azure.core.pipeline.policies import UserAgentPolicy

from .models._models import SendMessageError, AckMessageError
from ._version import VERSION

NO_ACK_MESSAGE_ERROR = "NoAckMessageReceivedFromServer"


def format_user_agent(user_agent: Optional[str] = None) -> str:
    """Format user agent string.
    :param user_agent: User agent string.
    :type user_agent: str
    :return: The formatted user agent.
    :rtype: str
    """
    return UserAgentPolicy(user_agent=user_agent, sdk_moniker=f"webpubsub-client/{VERSION}").user_agent


def raise_for_empty_message_ack(message_ack: Optional[Any], ack_id: Optional[int] = None):
    if message_ack is None:
        raise SendMessageError(
            message="Failed to send message.",
            ack_id=ack_id,
            error_detail=AckMessageError(
                name=NO_ACK_MESSAGE_ERROR,
                message="The connection may have been lost during message sending, or the service didn't send ack message.",  # pylint: disable=line-too-long
            ),
        )
