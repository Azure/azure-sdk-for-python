# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import sys
import time
import asyncio
import pytest
import hmac
import hashlib
import base64
import certifi
import ssl
from urllib.parse import quote as url_parse_quote

from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential, AccessToken
from azure.mgmt.servicebus.models import AccessRights
from azure.servicebus.aio import ServiceBusClient, ServiceBusSender, ServiceBusReceiver
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio._base_handler_async import ServiceBusSharedKeyCredential
from azure.servicebus.exceptions import (
    ServiceBusError,
    ServiceBusAuthenticationError,
    ServiceBusAuthorizationError,
    ServiceBusConnectionError,
)
from devtools_testutils import AzureMgmtRecordedTestCase, get_credential
from tests.servicebus_preparer import (
    CachedServiceBusNamespacePreparer,
    ServiceBusTopicPreparer,
    ServiceBusQueuePreparer,
    ServiceBusNamespaceAuthorizationRulePreparer,
    ServiceBusQueueAuthorizationRulePreparer,
    CachedServiceBusQueuePreparer,
    CachedServiceBusTopicPreparer,
    CachedServiceBusSubscriptionPreparer,
    CachedServiceBusResourceGroupPreparer,
    SERVICEBUS_ENDPOINT_SUFFIX,
)
from tests.utilities import (
    get_logger,
    uamqp_transport as get_uamqp_transport,
    ArgPasserAsync,
    SocketArgPasserAsync,
    socket_transport as get_socket_transport,
)

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()
socket_transport_params, socket_transport_ids = get_socket_transport()

_logger = get_logger(logging.DEBUG)


class TestServiceBusClientAsync(AzureMgmtRecordedTestCase):

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusQueuePreparer(name_prefix="servicebustest", dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_sb_client_bad_credentials_async(
        self, uamqp_transport, *, servicebus_namespace, servicebus_queue, **kwargs
    ):
        client = ServiceBusClient(
            fully_qualified_namespace=f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}",
            credential=ServiceBusSharedKeyCredential("invalid", "invalid"),
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        )
        async with client:
            with pytest.raises(ServiceBusAuthenticationError):
                async with client.get_queue_sender(servicebus_queue.name) as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_sb_client_bad_namespace_async(self, uamqp_transport, **kwargs):

        client = ServiceBusClient(
            fully_qualified_namespace=f"invalid{SERVICEBUS_ENDPOINT_SUFFIX}",
            credential=ServiceBusSharedKeyCredential("invalid", "invalid"),
            logging_enable=False,
            uamqp_transport=uamqp_transport,
        )
        async with client:
            with pytest.raises(ServiceBusError):
                async with client.get_queue_sender("invalidqueue") as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_sb_client_bad_entity_async(
        self, uamqp_transport, *, servicebus_namespace_connection_string=None, servicebus_namespace=None, **kwargs
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential(is_async=True)
        client = ServiceBusClient(fully_qualified_namespace, credential, uamqp_transport=uamqp_transport)

        async with client:
            with pytest.raises(ServiceBusAuthenticationError):
                async with client.get_queue_sender("invalid") as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

        fake_str = (
            f"Endpoint=sb://mock{SERVICEBUS_ENDPOINT_SUFFIX}/;"
            f"SharedAccessKeyName=mock;SharedAccessKey=mock;EntityPath=mockentity"
        )
        fake_client = ServiceBusClient.from_connection_string(fake_str, uamqp_transport=uamqp_transport)

        with pytest.raises(ValueError):
            fake_client.get_queue_sender("queue")

        with pytest.raises(ValueError):
            fake_client.get_queue_receiver("queue")

        with pytest.raises(ValueError):
            fake_client.get_topic_sender("topic")

        with pytest.raises(ValueError):
            fake_client.get_subscription_receiver("topic", "subscription")

        fake_client.get_queue_sender("mockentity")
        fake_client.get_queue_receiver("mockentity")
        fake_client.get_topic_sender("mockentity")
        fake_client.get_subscription_receiver("mockentity", "subscription")

        fake_str = f"Endpoint=sb://mock{SERVICEBUS_ENDPOINT_SUFFIX}/;" f"SharedAccessKeyName=mock;SharedAccessKey=mock"
        fake_client = ServiceBusClient.from_connection_string(fake_str)
        fake_client.get_queue_sender("queue")
        fake_client.get_queue_receiver("queue")
        fake_client.get_topic_sender("topic")
        fake_client.get_subscription_receiver("topic", "subscription")

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusQueuePreparer(name_prefix="servicebustest", dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix="servicebustest", access_rights=[AccessRights.listen])
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_sb_client_readonly_credentials(
        self, uamqp_transport, *, servicebus_authorization_rule_connection_string=None, servicebus_queue=None, **kwargs
    ):
        client = ServiceBusClient.from_connection_string(
            servicebus_authorization_rule_connection_string, uamqp_transport=uamqp_transport
        )

        async with client:
            async with client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

            with pytest.raises(ServiceBusAuthorizationError):
                async with client.get_queue_sender(servicebus_queue.name) as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusQueuePreparer(name_prefix="servicebustest", dead_lettering_on_message_expiration=True)
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix="servicebustest", access_rights=[AccessRights.send])
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_sb_client_writeonly_credentials_async(
        self, uamqp_transport, *, servicebus_authorization_rule_connection_string=None, servicebus_queue=None, **kwargs
    ):
        client = ServiceBusClient.from_connection_string(
            servicebus_authorization_rule_connection_string, uamqp_transport=uamqp_transport
        )

        async with client:
            with pytest.raises(ServiceBusError):
                async with client.get_queue_receiver(servicebus_queue.name) as receiver:
                    messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("test"))

                with pytest.raises(TypeError):
                    await sender.send_messages("cat")

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusQueuePreparer(name_prefix="servicebustest", dead_lettering_on_message_expiration=True)
    @CachedServiceBusTopicPreparer(name_prefix="servicebustest")
    @CachedServiceBusSubscriptionPreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_async_sb_client_close_spawned_handlers(
        self,
        uamqp_transport,
        *,
        servicebus_namespace_connection_string,
        servicebus_namespace,
        servicebus_queue,
        servicebus_topic,
        servicebus_subscription,
        **kwargs,
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential(is_async=True)
        client = ServiceBusClient(fully_qualified_namespace, credential, uamqp_transport=uamqp_transport)

        await client.close()

        # context manager
        async with client:
            assert len(client._handlers) == 0
            sender = client.get_queue_sender(servicebus_queue.name)
            receiver = client.get_queue_receiver(servicebus_queue.name)
            await sender._open()
            await receiver._open()

            assert sender._handler and sender._running
            assert receiver._handler and receiver._running
            assert len(client._handlers) == 2

        assert not sender._handler and not sender._running
        assert not receiver._handler and not receiver._running
        assert len(client._handlers) == 0

        # close operation
        sender = client.get_queue_sender(servicebus_queue.name)
        receiver = client.get_queue_receiver(servicebus_queue.name)
        await sender._open()
        await receiver._open()

        assert sender._handler and sender._running
        assert receiver._handler and receiver._running
        assert len(client._handlers) == 2

        await client.close()

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
        await client.close()

        queue_sender = client.get_queue_sender(servicebus_queue.name)
        queue_receiver = client.get_queue_receiver(servicebus_queue.name)
        assert len(client._handlers) == 2
        queue_sender = None
        queue_receiver = None
        assert len(client._handlers) < 2

        await client.close()
        topic_sender = client.get_topic_sender(servicebus_topic.name)
        subscription_receiver = client.get_subscription_receiver(servicebus_topic.name, servicebus_subscription.name)
        assert len(client._handlers) == 2
        topic_sender = None
        subscription_receiver = None
        # the previous sender/receiver can not longer be referenced, so len of handlers should just be 2 instead of 4
        assert len(client._handlers) < 4

        await client.close()
        topic_sender = client.get_topic_sender(servicebus_topic.name)
        subscription_receiver = client.get_subscription_receiver(servicebus_topic.name, servicebus_subscription.name)
        assert len(client._handlers) == 2
        topic_sender = client.get_topic_sender(servicebus_topic.name)
        subscription_receiver = client.get_subscription_receiver(servicebus_topic.name, servicebus_subscription.name)
        # the previous sender/receiver can not longer be referenced, so len of handlers should just be 2 instead of 4
        assert len(client._handlers) < 4

        await client.close()
        for _ in range(5):
            queue_sender = client.get_queue_sender(servicebus_queue.name)
            queue_receiver = client.get_queue_receiver(servicebus_queue.name)
            topic_sender = client.get_topic_sender(servicebus_topic.name)
            subscription_receiver = client.get_subscription_receiver(
                servicebus_topic.name, servicebus_subscription.name
            )
        assert len(client._handlers) < 15
        await client.close()

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusNamespaceAuthorizationRulePreparer(name_prefix="servicebustest")
    @ServiceBusQueuePreparer(
        name_prefix="servicebustest_qone", parameter_name="wrong_queue", dead_lettering_on_message_expiration=True
    )
    @ServiceBusQueuePreparer(name_prefix="servicebustest_qtwo", dead_lettering_on_message_expiration=True)
    @ServiceBusQueueAuthorizationRulePreparer(name_prefix="servicebustest_qtwo")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_sb_client_incorrect_queue_conn_str_async(
        self,
        uamqp_transport,
        *,
        servicebus_queue_authorization_rule_connection_string,
        servicebus_queue,
        wrong_queue,
        **kwargs,
    ):

        client = ServiceBusClient.from_connection_string(
            servicebus_queue_authorization_rule_connection_string, uamqp_transport=uamqp_transport
        )
        async with client:
            # Validate that the wrong sender/receiver queues with the right credentials fail.
            with pytest.raises(ValueError):
                async with client.get_queue_sender(wrong_queue.name) as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

            with pytest.raises(ValueError):
                async with client.get_queue_receiver(wrong_queue.name) as receiver:
                    messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

            # But that the correct ones work.
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("test"))

            async with client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

            # Now do the same but with direct connstr initialization.
            with pytest.raises(ValueError):
                async with ServiceBusSender._from_connection_string(
                    servicebus_queue_authorization_rule_connection_string,
                    queue_name=wrong_queue.name,
                ) as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

            with pytest.raises(ValueError):
                async with ServiceBusReceiver._from_connection_string(
                    servicebus_queue_authorization_rule_connection_string,
                    queue_name=wrong_queue.name,
                ) as receiver:
                    messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

            async with ServiceBusSender._from_connection_string(
                servicebus_queue_authorization_rule_connection_string,
                queue_name=servicebus_queue.name,
            ) as sender:
                await sender.send_messages(ServiceBusMessage("test"))

            async with ServiceBusReceiver._from_connection_string(
                servicebus_queue_authorization_rule_connection_string,
                queue_name=servicebus_queue.name,
            ) as receiver:
                messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusQueuePreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_client_sas_credential_async(
        self,
        uamqp_transport,
        *,
        servicebus_queue=None,
        servicebus_namespace=None,
        servicebus_namespace_key_name=None,
        servicebus_namespace_primary_key=None,
        servicebus_namespace_connection_string=None,
        **kwargs,
    ):
        # This should "just work" to validate known-good.
        credential = ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        hostname = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        auth_uri = "sb://{}/{}".format(hostname, servicebus_queue.name)
        token = (await credential.get_token(auth_uri)).token

        # Finally let's do it with SAS token + conn str
        token_conn_str = "Endpoint=sb://{}/;SharedAccessSignature={};".format(hostname, token)

        client = ServiceBusClient.from_connection_string(token_conn_str, uamqp_transport=uamqp_transport)
        async with client:
            assert len(client._handlers) == 0
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

        def generate_sas_token(uri, sas_name, sas_value, token_ttl):
            """Performs the signing and encoding needed to generate a sas token from a sas key."""
            sas = sas_value.encode("utf-8")
            expiry = str(int(time.time() + token_ttl))
            string_to_sign = (uri + "\n" + expiry).encode("utf-8")
            signed_hmac_sha256 = hmac.HMAC(sas, string_to_sign, hashlib.sha256)
            signature = url_parse_quote(base64.b64encode(signed_hmac_sha256.digest()))
            return "SharedAccessSignature sr={}&sig={}&se={}&skn={}".format(uri, signature, expiry, sas_name)

        class CustomizedSASCredential(object):
            def __init__(self, token, expiry):
                """
                :param str token: The token string
                :param float expiry: The epoch timestamp
                """
                self.token = token
                self.expiry = expiry
                self.token_type = b"servicebus.windows.net:sastoken"

            async def get_token(self, *scopes, **kwargs):
                """
                This method is automatically called when token is about to expire.
                """
                return AccessToken(self.token, self.expiry)

        token_ttl = 5  # seconds
        sas_token = generate_sas_token(
            auth_uri, servicebus_namespace_key_name, servicebus_namespace_primary_key, token_ttl
        )
        credential = CustomizedSASCredential(sas_token, time.time() + token_ttl)

        async with ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport) as client:
            sender = client.get_queue_sender(queue_name=servicebus_queue.name)
            await asyncio.sleep(10)
            with pytest.raises(ServiceBusAuthenticationError):
                async with sender:
                    message = ServiceBusMessage("Single Message")
                    await sender.send_messages(message)

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusQueuePreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_client_credential_async(
        self,
        uamqp_transport,
        *,
        servicebus_queue=None,
        servicebus_namespace=None,
        servicebus_namespace_key_name=None,
        servicebus_namespace_primary_key=None,
        servicebus_namespace_connection_string=None,
        **kwargs,
    ):
        # This should "just work" to validate known-good.
        credential = ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        hostname = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"

        client = ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport)
        async with client:
            assert len(client._handlers) == 0
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

        hostname = f"sb://{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"

        client = ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport)
        async with client:
            assert len(client._handlers) == 0
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

        hostname = f"https://{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"

        client = ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport)
        async with client:
            assert len(client._handlers) == 0
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusQueuePreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_client_azure_sas_credential_async(
        self,
        uamqp_transport,
        *,
        servicebus_queue=None,
        servicebus_namespace=None,
        servicebus_namespace_key_name=None,
        servicebus_namespace_primary_key=None,
        servicebus_namespace_connection_string=None,
        **kwargs,
    ):
        # This should "just work" to validate known-good.
        credential = ServiceBusSharedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        hostname = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        auth_uri = "sb://{}/{}".format(hostname, servicebus_queue.name)
        token = (await credential.get_token(auth_uri)).token

        credential = AzureSasCredential(token)

        client = ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport)
        async with client:
            assert len(client._handlers) == 0
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusQueuePreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_azure_named_key_credential_async(
        self,
        uamqp_transport,
        *,
        servicebus_queue=None,
        servicebus_namespace=None,
        servicebus_namespace_key_name=None,
        servicebus_namespace_primary_key=None,
        servicebus_namespace_connection_string=None,
        **kwargs,
    ):
        hostname = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = AzureNamedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)

        client = ServiceBusClient(hostname, credential, uamqp_transport=uamqp_transport)
        async with client:
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

        credential.update("foo", "bar")
        with pytest.raises(Exception):
            async with client:
                async with client.get_queue_sender(servicebus_queue.name) as sender:
                    await sender.send_messages(ServiceBusMessage("foo"))

        # update back to the right key again
        credential.update(servicebus_namespace_key_name, servicebus_namespace_primary_key)
        async with client:
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusQueuePreparer(name_prefix="servicebustest", dead_lettering_on_message_expiration=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @pytest.mark.parametrize("socket_transport", socket_transport_params, ids=socket_transport_ids)
    @SocketArgPasserAsync()
    async def test_sb_client_with_ssl_context_async(
        self,
        uamqp_transport,
        socket_transport,
        *,
        servicebus_namespace=None,
        servicebus_queue=None,
        **kwargs,
    ):
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential(is_async=True)

        # Check that SSLContext with invalid/nonexistent cert file raises an error
        context = ssl.SSLContext(cafile="fakecert.pem")
        context.verify_mode = ssl.CERT_REQUIRED
        client = ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            uamqp_transport=uamqp_transport,
            ssl_context=context,
            transport_type=socket_transport,
            retry_total=0,
        )
        async with client:
            with pytest.raises(ServiceBusConnectionError):
                async with client.get_queue_sender(servicebus_queue.name) as sender:
                    await sender.send_messages(ServiceBusMessage("test"))

            with pytest.raises(ServiceBusConnectionError):
                async with client.get_queue_receiver(servicebus_queue.name) as receiver:
                    messages = await receiver.receive_messages(max_message_count=1, max_wait_time=1)

        # Check that SSLContext with valid cert file doesn't raise an error
        async def verify_context_async():
            # asyncio.to_thread only available in Python 3.9+
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            await asyncio.to_thread(context.load_verify_locations, certifi.where())
            purpose = ssl.Purpose.SERVER_AUTH
            await asyncio.to_thread(context.load_default_certs, purpose=purpose)
            return context

        def verify_context():  # for Python 3.8
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_verify_locations(certifi.where())
            purpose = ssl.Purpose.SERVER_AUTH
            context.load_default_certs(purpose=purpose)
            return context

        if hasattr(asyncio, "to_thread"):
            context = await verify_context_async()
        else:
            context = verify_context()

        client = ServiceBusClient(
            fully_qualified_namespace=fully_qualified_namespace,
            credential=credential,
            uamqp_transport=uamqp_transport,
            ssl_context=context,
            transport_type=socket_transport,
        )

        async with client:
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("test"))
                await sender.send_messages(ServiceBusMessage("test"))

            async with client.get_queue_receiver(servicebus_queue.name) as receiver:
                messages = await receiver.receive_messages(max_message_count=2, max_wait_time=10)

            assert len(messages) == 2

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    async def test_backoff_fixed_retry(self, uamqp_transport):
        client = ServiceBusClient("fake.host.com", "fake_eh", retry_mode="fixed", uamqp_transport=uamqp_transport)
        # queue sender
        sender = client.get_queue_sender("fake_name")
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        await sender._backoff(retried_times=1, last_exception=Exception("fake"), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        # exp = 0.8 * (2 ** 1) = 1.6
        # time.sleep() in _backoff will take AT LEAST time 'exp' for retry_mode='exponential'
        # check that fixed is less than 'exp'
        assert sleep_time_fixed < backoff * (2**1)

        # topic sender
        sender = client.get_topic_sender("fake_name")
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        await sender._backoff(retried_times=1, last_exception=Exception("fake"), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        assert sleep_time_fixed < backoff * (2**1)

        # queue receiver
        receiver = client.get_queue_receiver("fake_name")
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        await receiver._backoff(retried_times=1, last_exception=Exception("fake"), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        assert sleep_time_fixed < backoff * (2**1)

        # subscription receiver
        receiver = client.get_subscription_receiver("fake_topic", "fake_sub")
        backoff = client._config.retry_backoff_factor
        start_time = time.time()
        await receiver._backoff(retried_times=1, last_exception=Exception("fake"), abs_timeout_time=None)
        sleep_time_fixed = time.time() - start_time
        assert sleep_time_fixed < backoff * (2**1)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    async def test_custom_client_id_queue_sender_async(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f"Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;"
        queue_name = "queue_name"
        custom_id = "my_custom_id"
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport
        )
        async with servicebus_client:
            queue_sender = servicebus_client.get_queue_sender(queue_name=queue_name, client_identifier=custom_id)
            assert queue_sender.client_identifier is not None
            assert queue_sender.client_identifier == custom_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    async def test_default_client_id_queue_sender(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f"Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;"
        queue_name = "queue_name"
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport
        )
        async with servicebus_client:
            queue_sender = servicebus_client.get_queue_sender(queue_name=queue_name)
            assert queue_sender.client_identifier is not None
            assert "SBSender" in queue_sender.client_identifier

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    async def test_custom_client_id_queue_receiver(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f"Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;"
        queue_name = "queue_name"
        custom_id = "my_custom_id"
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport
        )
        async with servicebus_client:
            queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name, client_identifier=custom_id)
            assert queue_receiver.client_identifier is not None
            assert queue_receiver.client_identifier == custom_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    async def test_default_client_id_queue_receiver(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f"Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;"
        queue_name = "queue_name"
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport
        )
        async with servicebus_client:
            queue_receiver = servicebus_client.get_queue_receiver(queue_name=queue_name)
            assert queue_receiver.client_identifier is not None
            assert "SBReceiver" in queue_receiver.client_identifier

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    async def test_custom_client_id_topic_sender(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f"Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;"
        custom_id = "my_custom_id"
        topic_name = "topic_name"
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport
        )
        async with servicebus_client:
            topic_sender = servicebus_client.get_topic_sender(topic_name=topic_name, client_identifier=custom_id)
            assert topic_sender.client_identifier is not None
            assert topic_sender.client_identifier == custom_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    async def test_default_client_id_topic_sender(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f"Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;"
        topic_name = "topic_name"
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport
        )
        async with servicebus_client:
            topic_sender = servicebus_client.get_topic_sender(topic_name=topic_name)
            assert topic_sender.client_identifier is not None
            assert "SBSender" in topic_sender.client_identifier

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    async def test_default_client_id_subscription_receiver(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f"Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;"
        topic_name = "topic_name"
        sub_name = "sub_name"
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport
        )
        async with servicebus_client:
            subscription_receiver = servicebus_client.get_subscription_receiver(topic_name, sub_name)
            assert subscription_receiver.client_identifier is not None
            assert "SBReceiver" in subscription_receiver.client_identifier

    @pytest.mark.asyncio
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    async def test_custom_client_id_subscription_receiver(self, uamqp_transport, **kwargs):
        servicebus_connection_str = f"Endpoint=sb://resourcename{SERVICEBUS_ENDPOINT_SUFFIX}/;SharedAccessSignature=THISISATESTKEYXXXXXXXXXXXXXXXXXXXXXXXXXXXX=;"
        custom_id = "my_custom_id"
        topic_name = "topic_name"
        sub_name = "sub_name"
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=servicebus_connection_str, uamqp_transport=uamqp_transport
        )
        async with servicebus_client:
            subscription_receiver = servicebus_client.get_subscription_receiver(
                topic_name, sub_name, client_identifier=custom_id
            )
            assert subscription_receiver.client_identifier is not None
            assert subscription_receiver.client_identifier == custom_id

    @pytest.mark.asyncio
    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer()
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @CachedServiceBusQueuePreparer(name_prefix="servicebustest")
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasserAsync()
    async def test_custom_endpoint_connection_verify_exception_async(
        self,
        uamqp_transport,
        *,
        servicebus_queue=None,
        servicebus_namespace=None,
        servicebus_namespace_key_name=None,
        servicebus_namespace_primary_key=None,
        servicebus_namespace_connection_string=None,
        **kwargs,
    ):
        hostname = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = AzureNamedKeyCredential(servicebus_namespace_key_name, servicebus_namespace_primary_key)

        # ensure regular connection_verify works
        certfile = certifi.where()
        client = ServiceBusClient(hostname, credential, connection_verify=certfile, uamqp_transport=uamqp_transport)
        async with client:
            async with client.get_queue_sender(servicebus_queue.name) as sender:
                await sender.send_messages(ServiceBusMessage("foo"))

        # invalid cert file to connection_verify should fail
        client = ServiceBusClient(
            hostname, credential, connection_verify="fakecertfile.pem", uamqp_transport=uamqp_transport
        )
        async with client:
            with pytest.raises(ServiceBusError):
                async with client.get_queue_sender(servicebus_queue.name) as sender:
                    await sender.send_messages(ServiceBusMessage("foo"))

        # Skipping on OSX uamqp - it's raising an Authentication/TimeoutError
        if not uamqp_transport or not sys.platform.startswith("darwin"):
            # invalid custom endpoint should fail
            fake_addr = "fakeaddress.com:1111"
            client = ServiceBusClient(
                hostname, credential, custom_endpoint_address=fake_addr, retry_total=0, uamqp_transport=uamqp_transport
            )
            async with client:
                if not uamqp_transport:
                    error = ServiceBusConnectionError
                else:
                    # if uamqp, catches an "Authorization timeout" error and raises ServiceBusError
                    error = ServiceBusError
                with pytest.raises(error):
                    async with client.get_queue_sender(servicebus_queue.name) as sender:
                        await sender.send_messages(ServiceBusMessage("foo"))

            client = ServiceBusClient(
                hostname,
                credential,
                custom_endpoint_address=fake_addr,
                connection_verify=certfile,
                retry_total=0,
                uamqp_transport=uamqp_transport,
            )
            async with client:
                with pytest.raises(ServiceBusError):
                    async with client.get_queue_sender(servicebus_queue.name) as sender:
                        await sender.send_messages(ServiceBusMessage("foo"))
