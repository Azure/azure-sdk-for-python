#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest


from examples.async_examples.example_queue_send_receive_batch_async import sample_queue_send_receive_batch_async
from examples.async_examples.example_session_send_receive_batch_async import sample_session_send_receive_batch_async
from examples.async_examples.example_session_send_receive_with_pool_async import sample_session_send_receive_with_pool_async


@pytest.mark.asyncio
async def test_async_sample_queue_send_receive_batch(live_servicebus_config, standard_queue):
    await sample_queue_send_receive_batch_async(live_servicebus_config, standard_queue)


@pytest.mark.asyncio
async def test_async_sample_session_send_receive_batch(live_servicebus_config, session_queue):
    await sample_session_send_receive_batch_async(live_servicebus_config, session_queue)


@pytest.mark.asyncio
async def test_async_sample_session_send_receive_with_pool(live_servicebus_config, session_queue):
    await sample_session_send_receive_with_pool_async(live_servicebus_config, session_queue)
