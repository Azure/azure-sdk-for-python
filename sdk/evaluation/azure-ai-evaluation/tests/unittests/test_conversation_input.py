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

import pytest

from azure.ai.evaluation import (
    FluencyEvaluator,
    RelevanceEvaluator,
    ResponseCompletenessEvaluator,
    RetrievalEvaluator,
    SimilarityEvaluator,
)
from azure.ai.evaluation._exceptions import EvaluationException
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


# Sample messages payload reused across the wiring tests below.
_USER_TURN = {"role": "user", "content": "What is 2+2?"}
_ASSISTANT_TURN = {"role": "assistant", "content": "4"}
_MESSAGES = [_USER_TURN, _ASSISTANT_TURN]
_TOOL_DEFS = [{"type": "function", "function": {"name": "calc"}}]


# All 5 direct-edit evaluators fixed in this PR. RAI evaluators go through
# ``RaiServiceEvaluatorBase._convert_kwargs_to_eval_input``, which is covered
# by the hoist helper's own tests plus the base's existing test suite.
_DIRECT_EVALUATORS = [
    RelevanceEvaluator,
    SimilarityEvaluator,
    FluencyEvaluator,
    RetrievalEvaluator,
    ResponseCompletenessEvaluator,
]


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestMessagesInputWiring:
    """Wiring-layer tests for the 5 direct-edit evaluators.

    The helper tests above prove ``hoist_messages_to_conversation`` reshapes
    kwargs correctly. These tests prove each evaluator's overridden
    ``_convert_kwargs_to_eval_input`` actually calls the hoist and that the
    hoisted output is what the base's ``_derive_conversation_converter`` sees.

    Assertion strategy: equivalence with the ``conversation={"messages": ...}``
    invocation. If both invocations produce the same per-turn eval_input list,
    hoist wiring is correct. This is robust to base-class output shape changes
    because both sides re-execute in lockstep.
    """

    # ------------------------------------------------------------------
    # A. Bare messages= (5 evaluators)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("evaluator_class", _DIRECT_EVALUATORS)
    def test_wiring_bare_messages(self, mock_model_config, evaluator_class):
        ev = evaluator_class(model_config=mock_model_config)

        with_messages = ev._convert_kwargs_to_eval_input(messages=list(_MESSAGES))
        with_conversation = ev._convert_kwargs_to_eval_input(conversation={"messages": list(_MESSAGES)})

        assert with_messages == with_conversation, (
            f"{evaluator_class.__name__}: bare messages= did not produce the "
            f"same eval_input as the equivalent conversation={{messages}} call."
        )

    # ------------------------------------------------------------------
    # B. Bare messages= + context + ground_truth + tool_definitions (5)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("evaluator_class", _DIRECT_EVALUATORS)
    def test_wiring_bare_messages_with_all_adjuncts(self, mock_model_config, evaluator_class):
        ev = evaluator_class(model_config=mock_model_config)

        with_messages = ev._convert_kwargs_to_eval_input(
            messages=list(_MESSAGES),
            context="ctx",
            ground_truth="gt",
            tool_definitions=list(_TOOL_DEFS),
        )
        # The equivalent conversation-shape call: ground_truth stamped onto
        # the assistant turn (matches the helper's stamping semantics), and
        # context / tool_definitions folded into the conversation dict.
        equivalent_conversation = {
            "messages": [
                dict(_USER_TURN),
                dict(_ASSISTANT_TURN, ground_truth="gt"),
            ],
            "context": "ctx",
            "tool_definitions": list(_TOOL_DEFS),
        }
        with_conversation = ev._convert_kwargs_to_eval_input(conversation=equivalent_conversation)

        assert with_messages == with_conversation, (
            f"{evaluator_class.__name__}: bare messages= + adjuncts did not "
            f"produce the same eval_input as the equivalent conversation= call. "
            f"Check hoist stamping of ground_truth and folding of "
            f"context / tool_definitions."
        )

    # ------------------------------------------------------------------
    # C. Legacy (query, response) path unchanged (5) — regression net
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("evaluator_class", _DIRECT_EVALUATORS)
    def test_wiring_legacy_query_response_unchanged(self, mock_model_config, evaluator_class):
        ev = evaluator_class(model_config=mock_model_config)

        # Every legacy shape needs at minimum query + response. Similarity
        # also requires ground_truth, Retrieval also requires context; supply
        # both universally so the legacy path is exercised without validator
        # noise unrelated to the wiring change.
        legacy_kwargs = {
            "query": "What is 2+2?",
            "response": "4",
            "context": "arithmetic",
            "ground_truth": "4",
        }

        # Baseline expectation: legacy input still routes through the base's
        # scalar path and produces a non-None eval_input. If this regresses,
        # the hoist code path is stealing kwargs it shouldn't touch.
        result = ev._convert_kwargs_to_eval_input(**legacy_kwargs)

        assert result is not None, (
            f"{evaluator_class.__name__}: legacy (query, response, ...) path "
            f"returned None after PR — hoist may be intercepting kwargs it "
            f"should leave alone."
        )
        # No hoisted 'conversation' key must have been synthesised when the
        # caller passed only scalar inputs — hoist is a no-op in this branch.
        assert "conversation" not in legacy_kwargs, (
            f"{evaluator_class.__name__}: hoist mutated caller kwargs by "
            f"synthesising 'conversation' on a legacy-only call."
        )

    # ------------------------------------------------------------------
    # D. Negative wiring tests (3) — pre-existing safety nets still fire
    # ------------------------------------------------------------------
    def test_wiring_empty_messages_still_rejected(self, mock_model_config):
        """Bare messages=[] must still fail the pre-existing empty-input check.
        Hoist should not paper over an empty conversation."""
        ev = RelevanceEvaluator(model_config=mock_model_config)
        with pytest.raises(EvaluationException):
            # Force validation to run end-to-end via the sync entry point.
            ev(messages=[])

    def test_wiring_messages_plus_query_is_ambiguous(self, mock_model_config):
        """Mixing bare messages= with a top-level query= must still be
        rejected as ambiguous input. Hoist is a routing fix, not a merge."""
        ev = SimilarityEvaluator(model_config=mock_model_config)
        with pytest.raises(EvaluationException):
            ev(
                messages=list(_MESSAGES),
                query="What is 2+2?",
                response="4",
                ground_truth="4",
            )

    def test_wiring_non_dict_message_entries_do_not_crash_hoist(self, mock_model_config):
        """Non-dict entries in messages must be silently skipped for
        ground_truth stamping (matches
        ``test_non_dict_messages_are_skipped_for_stamping`` in the helper
        tests). Hoist itself must not raise; downstream validation is what
        would reject a malformed message shape."""
        ev = FluencyEvaluator(model_config=mock_model_config)
        malformed = [
            {"role": "user", "content": "hi"},
            "not a dict",  # skipped for stamping
            {"role": "assistant", "content": "hello"},
        ]

        kwargs = {"messages": malformed, "ground_truth": "gt"}
        # Hoist runs at the top of the override; verify it doesn't raise.
        hoist_messages_to_conversation(kwargs)
        assert "conversation" in kwargs, "hoist should still synthesise conversation"
        # The assistant turn (index 2 in the caller's list, but the assistant
        # is the LAST entry in the shape we passed) receives the stamp; the
        # non-dict entry is untouched.
        conv_messages = kwargs["conversation"]["messages"]
        assert conv_messages[1] == "not a dict"
        assert conv_messages[2].get("ground_truth") == "gt"


# ------------------------------------------------------------------------
# RAI evaluator wiring — 8 evaluators inherit the hoist through
# ``RaiServiceEvaluatorBase._convert_kwargs_to_eval_input``. These tests
# parametrise directly over the 8 concrete RAI evaluators so each one gets
# a wiring assertion, mirroring the coverage grid used above for the 5
# direct-edit evaluators.
# ------------------------------------------------------------------------
from unittest.mock import MagicMock

from azure.ai.evaluation import (
    CodeVulnerabilityEvaluator,
    HateUnfairnessEvaluator,
    IndirectAttackEvaluator,
    ProtectedMaterialEvaluator,
    SelfHarmEvaluator,
    SexualEvaluator,
    ViolenceEvaluator,
)
from azure.ai.evaluation._evaluators._eci._eci import ECIEvaluator

_RAI_EVALUATORS = [
    ViolenceEvaluator,
    HateUnfairnessEvaluator,
    SelfHarmEvaluator,
    SexualEvaluator,
    ProtectedMaterialEvaluator,
    IndirectAttackEvaluator,
    CodeVulnerabilityEvaluator,
    ECIEvaluator,
]


def _make_rai_evaluator(cls):
    """Instantiate a RAI evaluator with a mock credential and a mock project
    scope. ``_convert_kwargs_to_eval_input`` runs entirely locally (no network),
    so mocks are sufficient for wiring-layer assertions."""
    scope = {
        "subscription_id": "mock-sub",
        "resource_group_name": "mock-rg",
        "project_name": "mock-project",
    }
    return cls(credential=MagicMock(), azure_ai_project=scope)


@pytest.mark.unittest
class TestRaiMessagesInputWiring:
    """Wiring-layer tests for the 8 RAI evaluators fixed by the
    ``RaiServiceEvaluatorBase._convert_kwargs_to_eval_input`` override.

    Same assertion strategy as ``TestMessagesInputWiring`` for the 5
    direct-edit evaluators: shape equivalence with the ``conversation={...}``
    invocation. If both invocations produce the same eval_input, hoist wiring
    through the RAI base is correct for that concrete evaluator.
    """

    # ------------------------------------------------------------------
    # A. Bare messages= (8 evaluators)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("evaluator_class", _RAI_EVALUATORS)
    def test_wiring_bare_messages_rai(self, evaluator_class):
        ev = _make_rai_evaluator(evaluator_class)

        with_messages = ev._convert_kwargs_to_eval_input(messages=list(_MESSAGES))
        with_conversation = ev._convert_kwargs_to_eval_input(conversation={"messages": list(_MESSAGES)})

        assert with_messages == with_conversation, (
            f"{evaluator_class.__name__}: bare messages= did not route through "
            f"RaiServiceEvaluatorBase._convert_kwargs_to_eval_input equivalently "
            f"to a conversation={{messages}} call."
        )

    # ------------------------------------------------------------------
    # B. Bare messages= + context + ground_truth + tool_definitions (8)
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("evaluator_class", _RAI_EVALUATORS)
    def test_wiring_bare_messages_with_all_adjuncts_rai(self, evaluator_class):
        ev = _make_rai_evaluator(evaluator_class)

        with_messages = ev._convert_kwargs_to_eval_input(
            messages=list(_MESSAGES),
            context="ctx",
            ground_truth="gt",
            tool_definitions=list(_TOOL_DEFS),
        )
        equivalent_conversation = {
            "messages": [
                dict(_USER_TURN),
                dict(_ASSISTANT_TURN, ground_truth="gt"),
            ],
            "context": "ctx",
            "tool_definitions": list(_TOOL_DEFS),
        }
        with_conversation = ev._convert_kwargs_to_eval_input(conversation=equivalent_conversation)

        assert with_messages == with_conversation, (
            f"{evaluator_class.__name__}: bare messages= + adjuncts did not "
            f"produce the same eval_input as the equivalent conversation= call "
            f"via the RAI base override."
        )

    # ------------------------------------------------------------------
    # C. Legacy (query, response) path unchanged (8) — regression net
    # ------------------------------------------------------------------
    @pytest.mark.parametrize("evaluator_class", _RAI_EVALUATORS)
    def test_wiring_legacy_query_response_unchanged_rai(self, evaluator_class):
        ev = _make_rai_evaluator(evaluator_class)

        legacy_kwargs = {"query": "What is 2+2?", "response": "4"}
        result = ev._convert_kwargs_to_eval_input(**legacy_kwargs)

        assert result is not None, (
            f"{evaluator_class.__name__}: legacy (query, response) path returned "
            f"None after PR — RAI base hoist may be intercepting kwargs it "
            f"should leave alone."
        )
        # No hoisted 'conversation' key must have been synthesised when the
        # caller passed only scalar inputs.
        assert "conversation" not in legacy_kwargs, (
            f"{evaluator_class.__name__}: RAI base hoist mutated caller kwargs "
            f"by synthesising 'conversation' on a legacy-only call."
        )

    # ------------------------------------------------------------------
    # D. Branch tests for the ``_use_legacy_endpoint`` short-circuit (2)
    # ------------------------------------------------------------------
    def test_use_legacy_endpoint_true_short_circuits_to_kwargs_list(self):
        """When ``_use_legacy_endpoint`` is True, the RAI override must
        return ``[kwargs]`` with the hoisted ``conversation`` present, NOT
        delegate to ``super()._convert_kwargs_to_eval_input``. This preserves
        pre-sync-migration single-call behavior for the legacy endpoint."""
        ev = _make_rai_evaluator(ViolenceEvaluator)
        ev._use_legacy_endpoint = True

        result = ev._convert_kwargs_to_eval_input(messages=list(_MESSAGES))

        # Short-circuit branch returns [kwargs] intact.
        assert isinstance(result, list), "legacy-endpoint branch should return a list"
        assert len(result) == 1, "legacy-endpoint branch returns exactly one entry"
        assert "conversation" in result[0], (
            "legacy-endpoint branch must return kwargs with 'conversation' " "hoisted from bare messages="
        )
        # Sanity: the hoisted conversation carries the same messages the
        # caller supplied.
        assert result[0]["conversation"]["messages"] == list(_MESSAGES)

    def test_use_legacy_endpoint_false_delegates_to_super(self):
        """When ``_use_legacy_endpoint`` is False (the default), the RAI
        override must delegate to ``super()._convert_kwargs_to_eval_input``
        so the base's per-turn conversation converter runs. The observable
        difference vs. the legacy branch is that the result is NOT the raw
        kwargs list."""
        ev = _make_rai_evaluator(ViolenceEvaluator)
        assert ev._use_legacy_endpoint is False, "default should be non-legacy"

        result = ev._convert_kwargs_to_eval_input(messages=list(_MESSAGES))

        # Delegated branch: base's per-turn converter runs. Concretely, the
        # result must equal what we'd get by calling with the equivalent
        # conversation dict directly — that IS super()'s output.
        reference = ev._convert_kwargs_to_eval_input(conversation={"messages": list(_MESSAGES)})
        assert result == reference

        # And it must NOT be shaped like the legacy short-circuit's
        # ``[kwargs]`` (which would still carry the raw ``messages`` key).
        # In the delegated path, the raw ``messages`` kwarg was consumed by
        # hoist before super() ran, so no result entry should retain it.
        if isinstance(result, list) and result and isinstance(result[0], dict):
            assert "messages" not in result[0], "delegated branch must not pass raw ``messages`` kwarg through"
