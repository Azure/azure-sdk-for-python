#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An (overly) verbose sample demonstrating possible failure modes and potential recovery patterns.

Many of these catches are present for illustrative or duplicate purposes, and could be condensed or elided
in a production scenario depending on the system design.
"""

import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.exceptions import (
    MessageSizeExceededError,
    ServiceBusConnectionError,
    ServiceBusAuthorizationError,
    ServiceBusAuthenticationError,
    OperationTimeoutError,
    ServiceBusError,
    ServiceBusCommunicationError,
    MessageAlreadySettled,
    MessageLockLostError,
    MessageNotFoundError
)

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

def send_batch_messages(sender):
    batch_message = sender.create_message_batch()
    for i in range(10):
        try:
            message = ServiceBusMessage("Data {}".format(i))
        except TypeError:
            # Message body is of an inappropriate type, must be string, bytes or None.
            continue
        try:
            batch_message.add_message(message)
        except MessageSizeExceededError:
            # ServiceBusMessageBatch object reaches max_size.
            # New ServiceBusMessageBatch object can be created here to send more data.
            # This must be handled at the application layer, by breaking up or condensing.
            continue
    last_error = None
    for _ in range(3): # Send retries
        try:
            sender.send_messages(batch_message)
            return
        except OperationTimeoutError:
            # send has timed out, retry.
            continue
        except MessageSizeExceededError:
            # The body provided in the message to be sent is too large.
            # This must be handled at the application layer, by breaking up or condensing.
            raise
        except ServiceBusError as e:
            # Other types of service bus errors that can be handled at the higher level, such as connection/auth errors
            # If it happens persistently, should bubble up, and should be logged/alerted if high volume.
            last_error = e
            continue
    if last_error:
        raise last_error

def receive_messages(receiver):
    should_retry = True
    while should_retry:
        try:
            for msg in receiver:
                try:
                    # Do your application-specific data processing here
                    print(str(msg))
                    should_complete = True
                except Exception as e:
                    should_complete = False
                
                for _ in range(3): # Settlement retry
                    try:
                        if should_complete:
                            receiver.complete_message(msg)
                        else:
                            receiver.abandon_message(msg)
                            # Depending on the desired behavior, one could dead letter on failure instead; failure modes are comparable.
                            # Abandon returns the message to the queue for another consumer to receive, dead letter moves to the dead letter subqueue.
                            #
                            # receiver.dead_letter_message(msg, reason=str(e), error_description="Application level failure")
                        break
                    except MessageAlreadySettled:
                        # Message was already settled, either somewhere earlier in this processing or by another node.  Continue.
                        break
                    except MessageLockLostError:
                        # Message lock was lost before settlement.  Handle as necessary in the app layer for idempotency then continue on.
                        break
                    except MessageNotFoundError:
                        # Message has an improper sequence number, was dead lettered, or otherwise does not exist.  Handle at app layer, continue on.
                        break
                    except ServiceBusError:
                        # Any other undefined service errors during settlement.  Can be transient, and can retry, but should be logged, and alerted on high volume.
                        continue
            return
        except ServiceBusAuthorizationError:
            # Permission based errors should be bubbled up.
            raise
        except:
            # Although miscellaneous service errors and interruptions can occasionally occur during receiving,
            # In most pragmatic cases one can try to continue receiving unless the failure mode seens persistent.
            # Logging the associated failure and alerting on high volume is often prudent.
            continue



def send_and_receive_defensively():
    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)

    for _ in range(3): # Connection retries.
        try:
            print("Opening")
            with servicebus_client:
                sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
                try:
                    with sender:
                        print("Sending")
                        send_batch_messages(sender)
                except ValueError:
                    # Handler was shut down previously.  (Cannot happen in this example, shown for completeness.)
                    pass

                receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
                try:
                    with receiver:
                        print("Receiving")
                        receive_messages(receiver)
                except ValueError:
                    # Handler was shut down previously.  (Cannot happen in this example, shown for completeness.)
                    pass

                return
        except ServiceBusConnectionError:
            # An error occurred in the connection to the service.
            # This may have been caused by a transient network issue or service problem. It is recommended to retry.
            continue
        except ServiceBusAuthorizationError:
            # An error occurred when authorizing the connection to the service.
            # This may have been caused by the credentials not having the right permission to perform the operation.
            # It is recommended to check the permission of the credentials.
            raise
        except ServiceBusAuthenticationError:
            # An error occurred when authenticate the connection to the service.
            # This may have been caused by the credentials being incorrect. It is recommended to check the credentials.
            raise
        except ServiceBusCommunicationError:
            # Unable to communicate with the specified servicebus.  Ensure that the FQDN is correct,
            # and that there is no firewall or network issue preventing connectivity.
            raise

send_and_receive_defensively()
print("Send and Receive is done.")
