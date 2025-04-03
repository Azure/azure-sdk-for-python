# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import pytest
from datetime import datetime, timedelta


from azure.servicebus import (
    ServiceBusClient,
    ServiceBusMessage,
)
from azure.servicebus._common.utils import utc_now

from devtools_testutils import AzureMgmtRecordedTestCase, get_credential
from servicebus_preparer import (
    SERVICEBUS_ENDPOINT_SUFFIX,
    CachedServiceBusNamespacePreparer,
    ServiceBusQueuePreparer,
    CachedServiceBusQueuePreparer,
    CachedServiceBusResourceGroupPreparer,
)
from utilities import get_logger
from utilities import uamqp_transport as get_uamqp_transport, ArgPasser

uamqp_transport_params, uamqp_transport_ids = get_uamqp_transport()

_logger = get_logger(logging.DEBUG)


class TestServiceBusMgmtOperationClient(AzureMgmtRecordedTestCase):

    @pytest.mark.liveTest
    @pytest.mark.live_test_only
    @CachedServiceBusResourceGroupPreparer(name_prefix="servicebustest")
    @CachedServiceBusNamespacePreparer(name_prefix="servicebustest")
    @ServiceBusQueuePreparer(name_prefix="servicebustest", requires_session=True)
    @pytest.mark.parametrize("uamqp_transport", uamqp_transport_params, ids=uamqp_transport_ids)
    @ArgPasser()
    def test_get_sessions(
        self, uamqp_transport, *, servicebus_namespace=None, servicebus_queue=None, **kwargs
    ):
        # Note: This test was to guard against github issue 7079
        fully_qualified_namespace = f"{servicebus_namespace.name}{SERVICEBUS_ENDPOINT_SUFFIX}"
        credential = get_credential()
        sb_client = ServiceBusClient(
            fully_qualified_namespace, credential, logging_enable=False, uamqp_transport=uamqp_transport
        )

        with sb_client.get_queue_sender(servicebus_queue.name) as sender:
            for i in range(5):
                sender.send_messages(ServiceBusMessage("ServiceBusMessage {}".format(i), session_id=str(i)))

        with sb_client.get_management_operation_client(servicebus_queue.name) as operator:
            batch = operator.get_sessions()

            assert len(batch) == 5
            
            for session in batch:
                assert session in ["0", "1", "2", "3", "4"]

                with sb_client.get_queue_receiver(servicebus_queue.name, session_id=session) as receiver:
                    messages = receiver.receive_messages(max_wait_time=5)
                    assert len(messages) == 1
                    assert messages[0].session_id == session