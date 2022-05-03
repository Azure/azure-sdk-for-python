# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from abc import ABC, abstractmethod

class AmqpTransport(ABC):

    # define constants
    BATCH_MESSAGE = None
    MAX_MESSAGE_LENGTH_BYTES = None

    @abstractmethod
    def to_outgoing_amqp_message(self, annotated_message):
        """
        Converts an AmqpAnnotatedMessage into an Amqp Transport Message.
        """
