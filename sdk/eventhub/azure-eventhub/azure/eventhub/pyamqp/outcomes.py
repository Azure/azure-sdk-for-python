#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# The Messaging layer defines a concrete set of delivery states which can be used (via the disposition frame)
# to indicate the state of the message at the receiver.

# Delivery states may be either terminal or non-terminal. Once a delivery reaches a terminal delivery-state,
# the state for that delivery will no longer change. A terminal delivery-state is referred to as an outcome.

# The following outcomes are formally defined by the messaging layer to indicate the result of processing at the
# receiver:

#     - accepted: indicates successful processing at the receiver
#     - rejected: indicates an invalid and unprocessable message
#     - released: indicates that the message was not (and will not be) processed
#     - modified: indicates that the message was modified, but not processed

# The following non-terminal delivery-state is formally defined by the messaging layer for use during link
# recovery to allow the sender to resume the transfer of a large message without retransmitting all the
# message data:

#     - received: indicates partial message data seen by the receiver as well as the starting point for a
#         resumed transfer

from collections import namedtuple

from .types import AMQPTypes, FieldDefinition, ObjDefinition
from .constants import FIELD
from .performatives import _CAN_ADD_DOCSTRING


Received = namedtuple('received', ['section_number', 'section_offset'])
Received._code = 0x00000023
Received._definition = (
    FIELD("section_number", AMQPTypes.uint, True, None, False),
    FIELD("section_offset", AMQPTypes.ulong, True, None, False))
if _CAN_ADD_DOCSTRING:
    Received.__doc__ = """
    At the target the received state indicates the furthest point in the payload of the message
    which the target will not need to have resent if the link is resumed. At the source the received state represents
    the earliest point in the payload which the Sender is able to resume transferring at in the case of link
    resumption. When resuming a delivery, if this state is set on the first transfer performative it indicates
    the offset in the payload at which the first resumed delivery is starting. The Sender MUST NOT send the
    received state on transfer or disposition performatives except on the first transfer performative on a
    resumed delivery.

    :param int section_number:
        When sent by the Sender this indicates the first section of the message (with sectionnumber 0 being the
        first section) for which data can be resent. Data from sections prior to the given section cannot be
        retransmitted for this delivery. When sent by the Receiver this indicates the first section of the message
        for which all data may not yet have been received.
    :param int section_offset:
        When sent by the Sender this indicates the first byte of the encoded section data of the section given by
        section-number for which data can be resent (with section-offset 0 being the first byte). Bytes from the
        same section prior to the given offset section cannot be retransmitted for this delivery. When sent by the
        Receiver this indicates the first byte of the given section which has not yet been received. Note that if
        a receiver has received all of section number X (which contains N bytes of data), but none of section
        number X + 1, then it may indicate this by sending either Received(section-number=X, section-offset=N) or
        Received(section-number=X+1, section-offset=0). The state Received(sectionnumber=0, section-offset=0)
        indicates that no message data at all has been transferred.
    """


Accepted = namedtuple('accepted', [])
Accepted._code = 0x00000024
Accepted._definition = ()
if _CAN_ADD_DOCSTRING:
    Accepted.__doc__ = """
    The accepted outcome.

    At the source the accepted state means that the message has been retired from the node, and transfer of
    payload data will not be able to be resumed if the link becomes suspended. A delivery may become accepted at
    the source even before all transfer frames have been sent, this does not imply that the remaining transfers
    for the delivery will not be sent - only the aborted fiag on the transfer performative can be used to indicate
    a premature termination of the transfer. At the target, the accepted outcome is used to indicate that an
    incoming Message has been successfully processed, and that the receiver of the Message is expecting the sender
    to transition the delivery to the accepted state at the source. The accepted outcome does not increment the
    delivery-count in the header of the accepted Message.
    """


Rejected = namedtuple('rejected', ['error'])
Rejected._code = 0x00000025
Rejected._definition = (FIELD("error", ObjDefinition.error, False, None, False),)
if _CAN_ADD_DOCSTRING:
    Rejected.__doc__ = """
    The rejected outcome.

    At the target, the rejected outcome is used to indicate that an incoming Message is invalid and therefore
    unprocessable. The rejected outcome when applied to a Message will cause the delivery-count to be incremented
    in the header of the rejected Message. At the source, the rejected outcome means that the target has informed
    the source that the message was rejected, and the source has taken the required action. The delivery SHOULD
    NOT ever spontaneously attain the rejected state at the source.

    :param ~uamqp.error.AMQPError error: The error that caused the message to be rejected.
        The value supplied in this field will be placed in the delivery-annotations of the rejected Message
        associated with the symbolic key "rejected".
    """


Released = namedtuple('released', [])
Released._code = 0x00000026
Released._definition = ()
if _CAN_ADD_DOCSTRING:
    Released.__doc__ = """
    The released outcome.

    At the source the released outcome means that the message is no longer acquired by the receiver, and has been
    made available for (re-)delivery to the same or other targets receiving from the node. The message is unchanged
    at the node (i.e. the delivery-count of the header of the released Message MUST NOT be incremented).
    As released is a terminal outcome, transfer of payload data will not be able to be resumed if the link becomes
    suspended. A delivery may become released at the source even before all transfer frames have been sent, this
    does not imply that the remaining transfers for the delivery will not be sent. The source MAY spontaneously
    attain the released outcome for a Message (for example the source may implement some sort of time bound
    acquisition lock, after which the acquisition of a message at a node is revoked to allow for delivery to an
    alternative consumer).

    At the target, the released outcome is used to indicate that a given transfer was not and will not be acted upon.
    """


Modified = namedtuple('modified', ['delivery_failed', 'undeliverable_here', 'message_annotations'])
Modified._code = 0x00000027
Modified._definition = (
    FIELD('delivery_failed', AMQPTypes.boolean, False, None, False),
    FIELD('undeliverable_here', AMQPTypes.boolean, False, None, False),
    FIELD('message_annotations', FieldDefinition.fields, False, None, False))
if _CAN_ADD_DOCSTRING:
    Modified.__doc__ = """
    The modified outcome.

    At the source the modified outcome means that the message is no longer acquired by the receiver, and has been
    made available for (re-)delivery to the same or other targets receiving from the node. The message has been
    changed at the node in the ways indicated by the fields of the outcome. As modified is a terminal outcome,
    transfer of payload data will not be able to be resumed if the link becomes suspended. A delivery may become
    modified at the source even before all transfer frames have been sent, this does not imply that the remaining
    transfers for the delivery will not be sent. The source MAY spontaneously attain the modified outcome for a
    Message (for example the source may implement some sort of time bound acquisition lock, after which the
    acquisition of a message at a node is revoked to allow for delivery to an alternative consumer with the
    message modified in some way to denote the previous failed, e.g. with delivery-failed set to true).
    At the target, the modified outcome is used to indicate that a given transfer was not and will not be acted
    upon, and that the message should be modified in the specified ways at the node.

    :param bool delivery_failed: Count the transfer as an unsuccessful delivery attempt.
        If the delivery-failed fiag is set, any Messages modified MUST have their deliverycount incremented.
    :param bool undeliverable_here: Prevent redelivery.
        If the undeliverable-here is set, then any Messages released MUST NOT be redelivered to the modifying
        Link Endpoint.
    :param dict message_annotations: Message attributes.
        Map containing attributes to combine with the existing message-annotations held in the Message's header
        section. Where the existing message-annotations of the Message contain an entry with the same key as an
        entry in this field, the value in this field associated with that key replaces the one in the existing
        headers; where the existing message-annotations has no such value, the value in this map is added.
    """
