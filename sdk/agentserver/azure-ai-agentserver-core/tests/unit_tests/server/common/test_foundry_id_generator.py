# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.agentserver.core.server.common.id_generator.foundry_id_generator import FoundryIdGenerator


def test_conversation_id_none_uses_response_partition():
    response_id = FoundryIdGenerator._new_id("resp")
    generator = FoundryIdGenerator(response_id=response_id, conversation_id=None)

    assert generator.conversation_id is None

    expected_partition = FoundryIdGenerator._extract_partition_id(response_id)
    generated_id = generator.generate("msg")
    assert FoundryIdGenerator._extract_partition_id(generated_id) == expected_partition


def test_conversation_id_present_uses_conversation_partition():
    response_id = FoundryIdGenerator._new_id("resp")
    conversation_id = FoundryIdGenerator._new_id("conv")
    generator = FoundryIdGenerator(response_id=response_id, conversation_id=conversation_id)

    assert generator.conversation_id == conversation_id

    expected_partition = FoundryIdGenerator._extract_partition_id(conversation_id)
    generated_id = generator.generate("msg")
    assert FoundryIdGenerator._extract_partition_id(generated_id) == expected_partition
