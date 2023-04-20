#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import logging
import sys
import os
import pytest
import time
from datetime import datetime, timedelta

try:
    from azure.servicebus._transport._uamqp_transport import UamqpTransport
except ImportError:
    pass
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport

from azure.common import AzureHttpError, AzureConflictHttpError
from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.pipeline.policies import RetryMode
from azure.mgmt.servicebus.models import AccessRights
from azure.servicebus import ServiceBusClient, ServiceBusSender, ServiceBusReceiver
from azure.servicebus._base_handler import ServiceBusSharedKeyCredential
from azure.servicebus._common.message import ServiceBusMessage, ServiceBusReceivedMessage
from azure.servicebus.exceptions import (
    ServiceBusError,
    ServiceBusAuthenticationError,
    ServiceBusAuthorizationError
)
from devtools_testutils import AzureMgmtRecordedTestCase
from servicebus_preparer import (
    CachedServiceBusNamespacePreparer, 
    ServiceBusTopicPreparer, 
    ServiceBusQueuePreparer,
    ServiceBusNamespaceAuthorizationRulePreparer,
    ServiceBusQueueAuthorizationRulePreparer,
    CachedServiceBusQueuePreparer,
    CachedServiceBusTopicPreparer,
    CachedServiceBusSubscriptionPreparer,
    CachedServiceBusResourceGroupPreparer,
    SERVICEBUS_ENDPOINT_SUFFIX
)
from utilities import uamqp_transport as get_uamqp_transport, ArgPasser
uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()

class TestServiceBusClient(AzureMgmtRecordedTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_sb_client_bad_credentials(self, uamqp_transport, *, servicebus_namespace=None, servicebus_queue=None, **kwargs):
        client = ServiceBusClient(
            fully_qualified_namespace=servicebus_namespace.name + f"{SERVICEBUS_ENDPOINT_SUFFIX}",
            credential=ServiceBusSharedKeyCredential('invalid', 'invalid'),
            logging_enable=False,
            uamqp_transport=uamqp_transport
            )
        with client:
            with pytest.raises(ServiceBusAuthenticationError):
                with client.get_queue_sender(servicebus_queue.name) as sender:
                    sender.send_messages(ServiceBusMessage("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_sb_client_bad_namespace(self, uamqp_transport, **kwargs):
        client = ServiceBusClient(
            fully_qualified_namespace=f"invalid{SERVICEBUS_ENDPOINT_SUFFIX}",
            credential=ServiceBusSharedKeyCredential('invalid', 'invalid'),
            logging_enable=False,
            uamqp_transport=uamqp_transport
            )
        with client:
            with pytest.raises(ServiceBusError):
                with client.get_queue_sender('invalidqueue') as sender:
                    sender.send_messages(ServiceBusMessage("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_sb_client_bad_entity(self, uamqp_transport, *, servicebus_namespace_connection_string=None, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string, uamqp_transport=uamqp_transport)

        with client:
            with pytest.raises(ServiceBusAuthenticationError):
                with client.get_queue_sender("invalid") as sender:
                    sender.send_messages(ServiceBusMessage("test"))

        fake_str = f"Endpoint=sb://mock{SERVICEBUS_ENDPOINT_SUFFIX}/;" \
                   f"SharedAccessKeyName=mock;SharedAccessKey=mock;EntityPath=mockentity"
        fake_client = ServiceBusClient.from_connection_string(fake_str, uamqp_transport=uamqp_transport)

        with pytest.raises(ValueError):
            fake_client.get_queue_sender('queue')

        with pytest.raises(ValueError):
            fake_client.get_queue_receiver('queue')

        with pytest.raises(ValueError):
            fake_client.get_topic_sender('topic')

        with pytest.raises(ValueError):
            fake_client.get_subscription_receiver('topic', 'subscription')

        fake_client.get_queue_sender('mockentity')
        fake_client.get_queue_receiver('mockentity')
        fake_client.get_topic_sender('mockentity')
        fake_client.get_subscription_receiver('mockentity', 'subscription')

        fake_str = f"Endpoint=sb://mock{SERVICEBUS_ENDPOINT_SUFFIX}/;" \
                   f"SharedAccessKeyName=mock;SharedAccessKey=mock"
        fake_client = ServiceBusClient.from_connection_string(fake_str, uamqp_transport=uamqp_transport)
        fake_client.get_queue_sender('queue')
        fake_client.get_queue_receiver('queue')
        fake_client.get_topic_sender('topic')
        fake_client.get_subscription_receiver('topic', 'subscription')

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest', access_rights=[AccessRights.listen])
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_sb_client_readonly_credentials(self, uamqp_transport, *, servicebus_authorization_rule_connection_string=None, servicebus_queue=None, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_authorization_rule_connection_string, uamqp_transport=uamqp_transport)

        with client:
            with client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = receiver.receive_messages(max_message_count=1, max_wait_time=1)

            with pytest.raises(ServiceBusAuthorizationError):
                with client.get_queue_sender(servicebus_queue.name) as sender:
                    sender.send_messages(ServiceBusMessage("test"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest', access_rights=[AccessRights.send])
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_sb_client_writeonly_credentials(self, uamqp_transport, *, servicebus_authorization_rule_connection_string=None, servicebus_queue=None, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_authorization_rule_connection_string, uamqp_transport=uamqp_transport)

        with client:
            with pytest.raises(ServiceBusError):
                with client.get_queue_receiver(servicebus_queue.name) as receiver:
                    messages = receiver.receive_messages(max_message_count=1, max_wait_time=1)

            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("test"))

                with pytest.raises(TypeError):
                    sender.send_messages("cat")

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix='servicebustest')
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix='servicebustest')
    @ServiceBusQueuePreparer(name_prefix='servicebustest_qone', parameter_name='wrong_queue', dead_lettering_on_message_expiration=True)
    @ServiceBusQueuePreparer(name_prefix='servicebustest_qtwo', dead_lettering_on_message_expiration=True)
    @ServiceBusQueueAuthorizationRulePreparer(name_prefix='servicebustest_qtwo')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_sb_client_incorrect_queue_conn_str(self, uamqp_transport, *, servicebus_queue_authorization_rule_connection_string=None, servicebus_queue=None, wrong_queue=None, **kwargs):
        if uamqp_transport:
            amqp_transport = UamqpTransport
        else:
            amqp_transport = PyamqpTransport
        client = ServiceBusClient.from_connection_string(servicebus_queue_authorization_rule_connection_string, uamqp_transport=uamqp_transport)
        with client:
            # Validate that the wrong sender/receiver queues with the right credentials fail.
            with pytest.raises(ValueError):
                with client.get_queue_sender(wrong_queue.name) as sender:
                    sender.send_messages(ServiceBusMessage("test"))

            with pytest.raises(ValueError):
                with client.get_queue_receiver(wrong_queue.name) as receiver:
                    messages =  receiver.receive_messages(max_message_count=1, max_wait_time=1)

            # But that the correct ones work.
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("test")) 

            with client.get_queue_receiver(servicebus_queue.name) as receiver:
               messages =  receiver.receive_messages(max_message_count=1, max_wait_time=1)

            # Now do the same but with direct connstr initialization.
            with pytest.raises(ValueError):
                with ServiceBusSender._from_connection_string(
                    servicebus_queue_authorization_rule_connection_string,
                    queue_name=wrong_queue.name,
                    amqp_transport=amqp_transport
                ) as sender:
                        sender.send_messages(ServiceBusMessage("test"))

            with pytest.raises(ValueError):
                with ServiceBusReceiver._from_connection_string(
                    servicebus_queue_authorization_rule_connection_string,
                    queue_name=wrong_queue.name,
                    amqp_transport=amqp_transport
                ) as receiver:
                    messages =  receiver.receive_messages(max_message_count=1, max_wait_time=1)

            with ServiceBusSender._from_connection_string(
                servicebus_queue_authorization_rule_connection_string,
                queue_name=servicebus_queue.name,
                amqp_transport=amqp_transport
            ) as sender:
                sender.send_messages(ServiceBusMessage("test"))

            with ServiceBusReceiver._from_connection_string(
                servicebus_queue_authorization_rule_connection_string,
                queue_name=servicebus_queue.name,
                amqp_transport=amqp_transport
            ) as receiver:
                messages =  receiver.receive_messages(max_message_count=1, max_wait_time=1)

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest', dead_lettering_on_message_expiration=True)
    @CachedServiceBusTopicPreparer(name_prefix='servicebustest')
    @CachedServiceBusSubscriptionPreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_sb_client_close_spawned_handlers(self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_queue=None, servicebus_topic=None, servicebus_subscription=None, **kwargs):
        client = ServiceBusClient.from_connection_string(servicebus_namespace_connection_string, uamqp_transport=uamqp_transport)

        client.close()

        # context manager
        with client:
            assert len(client._handlers) == 0
            sender = client.get_queue_sender(servicebus_queue.name)
            receiver = client.get_queue_receiver(servicebus_queue.name)
            sender._open()
            receiver._open()

            assert sender._handler and sender._running
            assert receiver._handler and receiver._running
            assert len(client._handlers) == 2

        assert not sender._handler and not sender._running
        assert not receiver._handler and not receiver._running
        assert len(client._handlers) == 0

        # close operation
        sender = client.get_queue_sender(servicebus_queue.name)
        receiver = client.get_queue_receiver(servicebus_queue.name)
        sender._open()
        receiver._open()

        assert sender._handler and sender._running
        assert receiver._handler and receiver._running
        assert len(client._handlers) == 2

        client.close()

        assert not sender._handler and not sender._running
        assert not receiver._handler and not receiver._running
        assert len(client._handlers) == 0

        queue_sender = client.get_queue_sender(servicebus_queue.name)
        queue_receiver = client.get_queue_receiver(servicebus_queue.name)
        assert len(client._handlers) == 2
        queue_sender = client.get_queue_sender(servicebus_queue.name)
        queue_receiver = client.get_queue_receiver(servicebus_queue.name)
        # the previous sender/receiver can not longer be referenced, there might be a delay in CPython
        # to remove the reference, so len of handlers should be less than 4
        assert len(client._handlers) < 4
        client.close()

        queue_sender = client.get_queue_sender(servicebus_queue.name)
        queue_receiver = client.get_queue_receiver(servicebus_queue.name)
        assert len(client._handlers) == 2
        queue_sender = None
        queue_receiver = None
        assert len(client._handlers) < 2

        client.close()
        topic_sender = client.get_topic_sender(servicebus_topic.name)
        subscription_receiver = client.get_subscription_receiver(servicebus_topic.name, servicebus_subscription.name)
        assert len(client._handlers) == 2
        topic_sender = None
        subscription_receiver = None
        # the previous sender/receiver can not longer be referenced, so len of handlers should just be 2 instead of 4
        assert len(client._handlers) < 4

        client.close()
        topic_sender = client.get_topic_sender(servicebus_topic.name)
        subscription_receiver = client.get_subscription_receiver(servicebus_topic.name, servicebus_subscription.name)
        assert len(client._handlers) == 2
        topic_sender = client.get_topic_sender(servicebus_topic.name)
        subscription_receiver = client.get_subscription_receiver(servicebus_topic.name, servicebus_subscription.name)
        # the previous sender/receiver can not longer be referenced, so len of handlers should just be 2 instead of 4
        assert len(client._handlers) < 4

        client.close()
        for _ in range(5):
            queue_sender = client.get_queue_sender(servicebus_queue.name)
            queue_receiver = client.get_queue_receiver(servicebus_queue.name)
            topic_sender = client.get_topic_sender(servicebus_topic.name)
            subscription_receiver = client.get_subscription_receiver(servicebus_topic.name,
                                                                     servicebus_subscription.name)
        assert len(client._handlers) < 15
        client.close()

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_client_sas_credential(self,
                                   uamqp_transport,
                                   *,
                                   servicebus_queue,
                                   servicebus_namespace,
                                   servicebus_namespace_key_name,
                                   servicebus_namespace_primary_key,
                                   servicebus_namespace_connection_string,
                                   **kwargs):
        # This should "just work" to validate known-good.
        credential = ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        hostname = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        auth_uri = "sb://{}/{}".format(hostname, servicebus_queue.name)
        token = credential.get_token(auth_uri).token

        # Finally let's do it with SAS token + conn str
        token_conn_str = "Endpoint=sb://{}/;SharedAccessSignature={};".format(hostname, token)

        client = ServiceBusClient.from_connection_string(token_conn_str, uamqp_transport=uamqp_transport)
        with client:
            assert len(client._handlers) == 0
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("foo"))

        # This is disabled pending UAMQP fix https://github.com/Azure/azure-uamqp-python/issues/170
        #
        #token_conn_str_without_se = token_conn_str.split('se=')[0] + token_conn_str.split('se=')[1].split('&')[1]
        #
        #client = ServiceBusClient.from_connection_string(token_conn_str_without_se, uamqp_transport=uamqp_transport)
        #with client:
        #    assert len(client._handlers) == 0
        #    with client.get_queue_sender(servicebus_queue.name) as sender:
        #        sender.send_messages(ServiceBusMessage("foo"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_client_credential(self,
                                   uamqp_transport,
                                   *,
                                   servicebus_queue=None,
                                   servicebus_namespace=None,
                                   servicebus_namespace_key_name=None,
                                   servicebus_namespace_primary_key=None,
                                   servicebus_namespace_connection_string=None,
                                   **kwargs):
        # This should "just work" to validate known-good.
        credential = ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        hostname = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"

        client = ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport)
        with client:
            assert len(client._handlers) == 0
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("foo"))

        hostname = f"sb://{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"

        client = ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport)
        with client:
            assert len(client._handlers) == 0
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("foo"))

        hostname = f"https://{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"

        client = ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport)
        with client:
            assert len(client._handlers) == 0
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("foo"))

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_client_azure_named_key_credential(self,
                                   uamqp_transport,
                                   *,
                                   servicebus_queue=None,
                                   servicebus_namespace=None,
                                   servicebus_namespace_key_name=None,
                                   servicebus_namespace_primary_key=None,
                                   servicebus_namespace_connection_string=None,
                                   **kwargs):
        # This should "just work" to validate known-good.
        credential = ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        hostname = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        auth_uri = "sb://{}/{}".format(hostname, servicebus_queue.name)
        token = credential.get_token(auth_uri).token

        # Finally let's do it with AzureSasCredential
        credential = AzureSasCredential(token)

        client = ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport)
        with client:
            assert len(client._handlers) == 0

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_azure_named_key_credential(self,
                                   uamqp_transport,
                                   *,
                                   servicebus_queue=None,
                                   servicebus_namespace=None,
                                   servicebus_namespace_key_name=None,
                                   servicebus_namespace_primary_key=None,
                                   servicebus_namespace_connection_string=None,
                                   **kwargs):
        hostname = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = AzureNamedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)

        client = ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport)
        with client:
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("foo"))
        
        credential.update("foo", "bar")
        with pytest.raises(Exception):
            with client:
                with client.get_queue_sender(servicebus_queue.name) as sender:
                    sender.send_messages(ServiceBusMessage("foo"))

        # update back to the right key again
        credential.update(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        with client:
            with client.get_queue_sender(servicebus_queue.name) as sender:
                sender.send_messages(ServiceBusMessage("foo"))

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_backoff_fixed_retry(self, uamqp_transport):

        client = ServiceBusClient(
            'fake.host.com',
            'fake_eh',
            retry_mode='fixed',
            uamqp_transport=uamqp_transport
        )
        # queue sender
        sender = client.get_queue_sender('fake_name')
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        sender._backoff(retried_times=1, last_exception=Exception('fake'), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        # exp = 0.8 * (2 ** 1) = 1.6
        # time.sleep() in _backoff will take AT LEAST time 'exp' for retry_mode='exponential'
        # check that fixed is less than 'exp'
        assert sleep_time_fixed < backoff * (2 ** 1)

        # topic sender
        sender = client.get_topic_sender('fake_name')
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        sender._backoff(retried_times=1, last_exception=Exception('fake'), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        assert sleep_time_fixed < backoff * (2 ** 1)

        # queue receiver 
        receiver = client.get_queue_receiver('fake_name')
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        receiver._backoff(retried_times=1, last_exception=Exception('fake'), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        assert sleep_time_fixed < backoff * (2 ** 1)

        # subscription receiver 
        receiver = client.get_subscription_receiver('fake_topic', 'fake_sub')
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        receiver._backoff(retried_times=1, last_exception=Exception('fake'), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        assert sleep_time_fixed < backoff * (2 ** 1)

        client = ServiceBusClient(
            'fake.host.com',
            'fake_eh',
            retry_mode=RetryMode.Fixed,
            uamqp_transport=uamqp_transport
        )
        # queue sender
        sender = client.get_queue_sender('fake_name')
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        sender._backoff(retried_times=1, last_exception=Exception('fake'), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        # exp = 0.8 * (2 ** 1) = 1.6
        # time.sleep() in _backoff will take AT LEAST time 'exp' for retry_mode='exponential'
        # check that fixed is less than 'exp'
        assert sleep_time_fixed < backoff * (2 ** 1)

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_custom_client_id_queue_sender(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f'Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;'
        queue_name = "queue_name"
        custom_id = "my_custom_id"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport)
        with servicebus_client:
            queue_sender = servicebus_client.get_queue_sender(queue_name=queue_name, client_identifier=custom_id)
            assert queue_sender.client_identifier is not None
            assert queue_sender.client_identifier == custom_id

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_default_client_id_queue_sender(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f'Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;'
        queue_name = "queue_name"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport)
        with servicebus_client:
            queue_sender = servicebus_client.get_queue_sender(queue_name=queue_name)
            assert queue_sender.client_identifier is not None
            assert "SBSender" in queue_sender.client_identifier

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_custom_client_id_queue_receiver(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f'Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;'
        queue_name = "queue_name"
        custom_id = "my_custom_id"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport)
        with servicebus_client:
            queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, client_identifier=custom_id)
            assert queue_receiver.client_identifier is not None
            assert queue_receiver.client_identifier == custom_id

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_default_client_id_queue_receiver(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f'Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;'
        queue_name = "queue_name"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport)
        with servicebus_client:
            queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
            assert queue_receiver.client_identifier is not None
            assert "SBReceiver" in queue_receiver.client_identifier

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_custom_client_id_topic_sender(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f'Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;'
        custom_id = "my_custom_id"
        topic_name = "topic_name"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport)
        with servicebus_client:
            topic_sender = servicebus_client.get_topic_sender(topic_name=topic_name, client_identifier=custom_id)
            assert topic_sender.client_identifier is not None
            assert topic_sender.client_identifier == custom_id

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_default_client_id_topic_sender(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f'Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;'
        topic_name = "topic_name"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport)
        with servicebus_client:
            topic_sender = servicebus_client.get_topic_sender(topic_name=topic_name)
            assert topic_sender.client_identifier is not None
            assert "SBSender" in topic_sender.client_identifier

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_default_client_id_subscription_receiver(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f'Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;'
        topic_name = "topic_name"
        sub_name = "sub_name"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport)
        with servicebus_client:
            subscription_receiver = servicebus_client.get_subscription_receiver(topic_name, sub_name)
            assert subscription_receiver.client_identifier is not None
            assert "SBReceiver" in subscription_receiver.client_identifier

    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    def test_custom_client_id_subscription_receiver(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f'Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;'
        custom_id = "my_custom_id"
        topic_name = "topic_name"
        sub_name = "sub_name"
        servicebus_client = ServiceBusClient.from_connection_string(conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport)
        with servicebus_client:
            subscription_receiver = servicebus_client.get_subscription_receiver(topic_name, sub_name, client_identifier=custom_id)
            assert subscription_receiver.client_identifier is not None
            assert subscription_receiver.client_identifier == custom_id

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix='servicebustest')
    @CachedServiceBusQueuePreparer(name_prefix='servicebustest')
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_connection_verify_exception(self,
                                   uamqp_transport,
                                   *,
                                   servicebus_queue=None,
                                   servicebus_namespace=None,
                                   servicebus_namespace_key_name=None,
                                   servicebus_namespace_primary_key=None,
                                   servicebus_namespace_connection_string=None,
                                   **kwargs):
        hostname = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = AzureNamedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)

        client = ServiceBusClient(hostname, credential, connection_verify="cacert.pem", uamqp_transport=uamqp_transport)
        with client:
            with pytest.raises(ServiceBusError):
                with client.get_queue_sender(servicebus_queue.name) as sender:
                    sender.send_messages(ServiceBusMessage("foo"))
