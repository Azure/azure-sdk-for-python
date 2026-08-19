# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Unit tests for :func:`hoist_messages_to_conversation`.

Covers the six branches called out in review:

1. No ``messages`` and no ``conversation`` — kwargs returned unchanged.
2. ``conversation`` already provided — short-circuit, no adjunct hoisting.
3. Bare ``messages`` with no adjuncts — hoisted into ``conversation``.
4. Bare ``messages`` + all adjuncts (``context``, ``ground_truth``,
   ``tool_definitions``) — adjuncts moved into ``conversation``,
   ``ground_truth`` stamped onto assistant turns.
5. Non-dict messages entries — skipped for stamping, hoist still runs.
6. Immutability guarantee — caller's ``messages`` list and dicts are not
   mutated when ``ground_truth`` is stamped, so the same list can be reused
   across evaluators with different ``ground_truth`` values.
"""

from azure.ai.evaluation._evaluators._common import hoist_messages_to_conversation


class TestHoistMessagesToConversation:
    def test_no_messages_no_conversation_is_noop(self):
        kwargs = {"query": "q", "response": "r"}
        result = hoist_messages_to_conversation(kwargs)
        assert result is kwargs
        assert kwargs == {"query": "q", "response": "r"}

    def test_conversation_already_provided_is_noop(self):
        conv = {"messages": [{"role": "user", "content": "hi"}]}
        kwargs = {
            "conversation": conv,
            "messages": [{"role": "assistant", "content": "should stay put"}],
            "context": "should stay put",
        }
        hoist_messages_to_conversation(kwargs)
        # conversation short-circuits before any adjunct is folded in.
        assert kwargs["conversation"] is conv
        assert kwargs["messages"] == [{"role": "assistant", "content": "should stay put"}]
        assert kwargs["context"] == "should stay put"

    def test_bare_messages_no_adjuncts(self):
        messages = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]
        kwargs = {"messages": messages}
        hoist_messages_to_conversation(kwargs)
        assert "messages" not in kwargs
        assert kwargs["conversation"] == {"messages": messages}
        # No ground_truth was passed, so messages list identity is preserved.
        assert kwargs["conversation"]["messages"] is messages

    def test_bare_messages_with_all_adjuncts(self):
        messages = [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "Paris."},
        ]
        tool_defs = [{"name": "search", "description": "search"}]
        kwargs = {
            "messages": messages,
            "context": "geography Q&A",
            "ground_truth": "Paris",
            "tool_definitions": tool_defs,
        }
        hoist_messages_to_conversation(kwargs)
        # Adjuncts moved into the conversation dict.
        assert "context" not in kwargs
        assert "ground_truth" not in kwargs
        assert "tool_definitions" not in kwargs
        assert "messages" not in kwargs
        conv = kwargs["conversation"]
        assert conv["context"] == "geography Q&A"
        assert conv["tool_definitions"] is tool_defs
        # ground_truth stamped onto the assistant turn.
        assert conv["messages"][0] == {"role": "user", "content": "What is the capital of France?"}
        assert conv["messages"][1] == {
            "role": "assistant",
            "content": "Paris.",
            "ground_truth": "Paris",
        }

    def test_non_dict_messages_are_skipped_for_stamping(self):
        # Non-dict entries (strings here as a stand-in for typed Message objects)
        # are silently skipped when stamping ground_truth. The hoist itself still
        # runs so the input isn't dropped on the floor.
        messages = [
            {"role": "user", "content": "hi"},
            "not-a-dict",
            {"role": "assistant", "content": "hello"},
        ]
        kwargs = {"messages": messages, "ground_truth": "GT"}
        hoist_messages_to_conversation(kwargs)
        conv = kwargs["conversation"]
        # dict assistant turn gets ground_truth; non-dict entry untouched.
        assert conv["messages"][1] == "not-a-dict"
        assert conv["messages"][2] == {
            "role": "assistant",
            "content": "hello",
            "ground_truth": "GT",
        }

    def test_caller_messages_list_not_mutated_when_ground_truth_stamped(self):
        # Regression guard against the review's Finding 2: reusing the same
        # messages list across two evaluations with different ground_truth
        # values must NOT leak the first ground_truth into the second call.
        shared_messages = [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "Paris."},
        ]
        original_assistant = shared_messages[1]

        # First hoist call — stamps ground_truth "A".
        first = {"messages": shared_messages, "ground_truth": "A"}
        hoist_messages_to_conversation(first)
        first_stamped = first["conversation"]["messages"][1]
        assert first_stamped["ground_truth"] == "A"

        # Caller's shared list and its assistant dict must be unchanged.
        assert shared_messages[1] is original_assistant
        assert "ground_truth" not in shared_messages[1]

        # Second hoist call with a different ground_truth must not see "A".
        second = {"messages": shared_messages, "ground_truth": "B"}
        hoist_messages_to_conversation(second)
        second_stamped = second["conversation"]["messages"][1]
        assert second_stamped["ground_truth"] == "B"
        # And the caller's shared list is STILL unchanged.
        assert shared_messages[1] is original_assistant
        assert "ground_truth" not in shared_messages[1]

    def test_ground_truth_not_overwritten_when_already_per_turn(self):
        # When an assistant turn already carries its own ground_truth, the
        # top-level scalar must not overwrite it.
        messages = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello", "ground_truth": "per-turn"},
        ]
        kwargs = {"messages": messages, "ground_truth": "top-level"}
        hoist_messages_to_conversation(kwargs)
        stamped = kwargs["conversation"]["messages"][1]
        assert stamped["ground_truth"] == "per-turn"
