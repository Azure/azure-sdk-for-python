# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end tests for the FoundryStorage samples (06-08).

Per the repo's sample-testing convention (see
``azure-ai-agentserver-responses/tests/e2e/test_sample_e2e.py``), each sample's
handler logic is replicated here *inline* (not imported from the sample
module) and driven through the real M365 Agents SDK turn pipeline
(``AgentApplication`` + ``HttpAdapterBase.process_activity``) for the full
in-process lifecycle: state load -> handler dispatch -> state save -> outbound
send. ``MemoryStorage`` stands in for ``FoundryStorage`` (both implement the
same M365 ``Storage`` contract; see ``test_foundry_storage.py`` for the adapter
unit tests), and a fake ``ChannelServiceClientFactory`` captures outbound
activities in place of a real Bot Connector call, so these tests exercise the
samples' actual behavior end-to-end without any network access.
"""

from __future__ import annotations

from typing import Any

import pytest
from microsoft_agents.activity import Activity, ChannelAccount, ConversationAccount, ResourceResponse
from microsoft_agents.hosting.core import AgentApplication, ClaimsIdentity, HttpAdapterBase, MemoryStorage, TurnState
from microsoft_agents.hosting.core.app.proactive.proactive_options import ProactiveOptions

# ---------------------------------------------------------------------------
# Shared network-free turn-driving harness
# ---------------------------------------------------------------------------


class _FakeConversations:
    """Captures outbound sends instead of calling the real Bot Connector API."""

    def __init__(self) -> None:
        self.sent: list[Activity] = []

    async def reply_to_activity(self, conversation_id: str, activity_id: str, activity: Activity) -> ResourceResponse:
        _ = conversation_id, activity_id
        self.sent.append(activity)
        return ResourceResponse(id="r1")

    async def send_to_conversation(self, conversation_id: str, activity: Activity) -> ResourceResponse:
        _ = conversation_id
        self.sent.append(activity)
        return ResourceResponse(id="r1")


class _FakeConnectorClient:
    def __init__(self) -> None:
        self.conversations = _FakeConversations()

    async def close(self) -> None:
        pass


class _FakeUserTokenClient:
    async def close(self) -> None:
        pass


class _FakeChannelServiceClientFactory:
    """Network-free stand-in for ``RestChannelServiceClientFactory``."""

    def __init__(self) -> None:
        self.client = _FakeConnectorClient()

    async def create_connector_client(
        self,
        context: Any,
        claims_identity: Any,
        service_url: str,
        audience: str,
        scopes: list[str] | None = None,
        use_anonymous: bool = False,
    ) -> _FakeConnectorClient:
        _ = context, claims_identity, service_url, audience, scopes, use_anonymous
        return self.client

    async def create_user_token_client(
        self, context: Any, claims_identity: Any, use_anonymous: bool = False
    ) -> _FakeUserTokenClient:
        _ = context, claims_identity, use_anonymous
        return _FakeUserTokenClient()


def _test_adapter() -> tuple[HttpAdapterBase, _FakeChannelServiceClientFactory]:
    factory = _FakeChannelServiceClientFactory()
    return HttpAdapterBase(channel_service_client_factory=factory), factory


def _anonymous_claims() -> ClaimsIdentity:
    return ClaimsIdentity({}, is_authenticated=False, authentication_type="anonymous")


def _message(text: str, *, conversation_id: str = "c1", user_id: str = "u1") -> Activity:
    return Activity(
        type="message",
        text=text,
        channel_id="test",
        conversation=ConversationAccount(id=conversation_id),
        from_property=ChannelAccount(id=user_id),
        recipient=ChannelAccount(id="bot"),
        service_url="https://test.example",
    )


def _conversation_update(*, conversation_id: str = "c1", member_id: str = "u1") -> Activity:
    return Activity(
        type="conversationUpdate",
        channel_id="test",
        conversation=ConversationAccount(id=conversation_id),
        from_property=ChannelAccount(id=member_id),
        recipient=ChannelAccount(id="bot"),
        service_url="https://test.example",
        members_added=[ChannelAccount(id=member_id)],
    )


# ---------------------------------------------------------------------------
# Sample 06: durable conversation/user state (samples/06-foundry-storage-state)
# ---------------------------------------------------------------------------


def _build_state_sample_app(storage: MemoryStorage, adapter: HttpAdapterBase) -> AgentApplication:
    """Replicates samples/06-foundry-storage-state/main.py's handlers."""
    app = AgentApplication[TurnState](storage=storage, adapter=adapter)

    @app.activity("conversationUpdate")
    async def on_members_added(context, _state):
        for member in context.activity.members_added or []:
            if member.id != context.activity.recipient.id:
                await context.send_activity(
                    "Hello! I persist conversation and user state with FoundryStorage.\n\n"
                    "Send any message to increment the durable counters."
                )

    @app.activity("message")
    async def on_message(context, state):
        conversation_count = state.conversation.get_value("message_count", lambda: 0)
        user_count = state.user.get_value("message_count", lambda: 0)
        conversation_count += 1
        user_count += 1
        state.conversation.set_value("message_count", conversation_count)
        state.user.set_value("message_count", user_count)
        await context.send_activity(
            "FoundryStorage persisted this turn.\n\n"
            f"- Conversation messages: **{conversation_count}**\n"
            f"- Messages from you: **{user_count}**"
        )

    return app


@pytest.mark.asyncio
async def test_sample06_welcomes_new_members() -> None:
    storage = MemoryStorage()
    adapter, factory = _test_adapter()
    app = _build_state_sample_app(storage, adapter)

    await adapter.process_activity(_anonymous_claims(), _conversation_update(), app.on_turn)

    assert len(factory.client.conversations.sent) == 1
    assert "persist conversation and user state" in factory.client.conversations.sent[0].text


@pytest.mark.asyncio
async def test_sample06_counters_persist_across_turns() -> None:
    """Conversation and user counters survive across separate turns via storage."""
    storage = MemoryStorage()
    adapter, factory = _test_adapter()
    app = _build_state_sample_app(storage, adapter)

    for _ in range(3):
        await adapter.process_activity(_anonymous_claims(), _message("hi"), app.on_turn)

    replies = [a.text for a in factory.client.conversations.sent]
    assert "Conversation messages: **1**" in replies[0]
    assert "Conversation messages: **2**" in replies[1]
    assert "Conversation messages: **3**" in replies[2]
    assert "Messages from you: **3**" in replies[2]


@pytest.mark.asyncio
async def test_sample06_user_counter_is_scoped_per_user() -> None:
    """The per-user counter is independent of the conversation-wide counter."""
    storage = MemoryStorage()
    adapter, factory = _test_adapter()
    app = _build_state_sample_app(storage, adapter)

    await adapter.process_activity(_anonymous_claims(), _message("hi", user_id="alice"), app.on_turn)
    await adapter.process_activity(_anonymous_claims(), _message("hi", user_id="bob"), app.on_turn)

    replies = [a.text for a in factory.client.conversations.sent]
    # Conversation counter keeps incrementing across both users ...
    assert "Conversation messages: **1**" in replies[0]
    assert "Conversation messages: **2**" in replies[1]
    # ... but each user's own counter starts fresh.
    assert "Messages from you: **1**" in replies[0]
    assert "Messages from you: **1**" in replies[1]


# ---------------------------------------------------------------------------
# Sample 08: durable transcript history (samples/08-foundry-storage-history)
# ---------------------------------------------------------------------------


def _build_history_sample_app(storage: MemoryStorage, adapter: HttpAdapterBase) -> AgentApplication:
    """Replicates samples/08-foundry-storage-history/main.py's handlers."""
    app = AgentApplication[TurnState](storage=storage, adapter=adapter)

    @app.activity("message")
    async def on_message(context, state):
        user_text = (context.activity.text or "").strip()
        if not user_text:
            return

        history = state.conversation.get_value("history", lambda: [])

        if user_text == "/clear":
            state.conversation.set_value("history", [])
            await context.send_activity("Transcript cleared.")
            return

        if user_text == "/history":
            if not history:
                await context.send_activity("No messages stored yet.")
            else:
                transcript = "\n".join(f"{i}. {line}" for i, line in enumerate(history, 1))
                await context.send_activity(f"**Stored transcript ({len(history)}):**\n\n{transcript}")
            return

        history.append(f"You: {user_text}")
        state.conversation.set_value("history", history)
        await context.send_activity(
            f"Saved. I've persisted **{len(history)}** message(s) this conversation. "
            "Send `/history` to see them all."
        )

    return app


@pytest.mark.asyncio
async def test_sample08_history_command_reports_no_messages_initially() -> None:
    storage = MemoryStorage()
    adapter, factory = _test_adapter()
    app = _build_history_sample_app(storage, adapter)

    await adapter.process_activity(_anonymous_claims(), _message("/history"), app.on_turn)

    assert factory.client.conversations.sent[0].text == "No messages stored yet."


@pytest.mark.asyncio
async def test_sample08_transcript_persists_and_history_command_replays_it() -> None:
    storage = MemoryStorage()
    adapter, factory = _test_adapter()
    app = _build_history_sample_app(storage, adapter)

    await adapter.process_activity(_anonymous_claims(), _message("hello"), app.on_turn)
    await adapter.process_activity(_anonymous_claims(), _message("world"), app.on_turn)
    await adapter.process_activity(_anonymous_claims(), _message("/history"), app.on_turn)

    transcript_reply = factory.client.conversations.sent[-1].text
    assert "**Stored transcript (2):**" in transcript_reply
    assert "1. You: hello" in transcript_reply
    assert "2. You: world" in transcript_reply


@pytest.mark.asyncio
async def test_sample08_clear_command_erases_the_transcript() -> None:
    storage = MemoryStorage()
    adapter, factory = _test_adapter()
    app = _build_history_sample_app(storage, adapter)

    await adapter.process_activity(_anonymous_claims(), _message("hello"), app.on_turn)
    await adapter.process_activity(_anonymous_claims(), _message("/clear"), app.on_turn)
    await adapter.process_activity(_anonymous_claims(), _message("/history"), app.on_turn)

    assert factory.client.conversations.sent[1].text == "Transcript cleared."
    assert factory.client.conversations.sent[2].text == "No messages stored yet."


# ---------------------------------------------------------------------------
# Sample 07: durable proactive conversation references
# (samples/07-foundry-storage-proactive)
# ---------------------------------------------------------------------------


def _build_proactive_sample_app(storage: MemoryStorage, adapter: HttpAdapterBase) -> AgentApplication:
    """Replicates samples/07-foundry-storage-proactive/main.py's handlers."""
    app = AgentApplication[TurnState](storage=storage, adapter=adapter, proactive=ProactiveOptions(storage=storage))

    @app.message("/subscribe")
    async def on_subscribe(context, _state):
        await app.proactive.store_conversation(context)
        conversation_id = context.activity.conversation.id
        await context.send_activity(
            "Stored this conversation in FoundryStorage.\n\n"
            f"POST `/notify/{conversation_id}` to send a proactive notification."
        )

    @app.activity("message")
    async def on_message(context, _state):
        await context.send_activity("Send **/subscribe** to store this conversation for proactive notifications.")

    return app


async def _notify(app: AgentApplication, adapter: HttpAdapterBase, conversation_id: str) -> None:
    """Replicates samples/07-foundry-storage-proactive/main.py's notify() route."""

    async def send_notification(context, _state):
        await context.send_activity("Proactive notification sent from a conversation reference in FoundryStorage.")

    await app.proactive.continue_conversation(adapter, conversation_id, send_notification)


@pytest.mark.asyncio
async def test_sample07_subscribe_stores_the_conversation_reference() -> None:
    storage = MemoryStorage()
    adapter, factory = _test_adapter()
    app = _build_proactive_sample_app(storage, adapter)

    await adapter.process_activity(_anonymous_claims(), _message("/subscribe"), app.on_turn)

    assert "Stored this conversation in FoundryStorage" in factory.client.conversations.sent[0].text
    assert await app.proactive.get_conversation("c1") is not None


@pytest.mark.asyncio
async def test_sample07_notify_resumes_the_stored_conversation() -> None:
    storage = MemoryStorage()
    adapter, factory = _test_adapter()
    app = _build_proactive_sample_app(storage, adapter)

    await adapter.process_activity(_anonymous_claims(), _message("/subscribe"), app.on_turn)
    await _notify(app, adapter, "c1")

    assert factory.client.conversations.sent[-1].text == (
        "Proactive notification sent from a conversation reference in FoundryStorage."
    )


@pytest.mark.asyncio
async def test_sample07_notify_unknown_conversation_raises_key_error() -> None:
    """Mirrors the sample's notify() route, which maps this to a 404 response."""
    storage = MemoryStorage()
    adapter, _factory = _test_adapter()
    app = _build_proactive_sample_app(storage, adapter)

    with pytest.raises(KeyError):
        await _notify(app, adapter, "never-subscribed")


@pytest.mark.asyncio
async def test_sample07_default_message_prompts_to_subscribe() -> None:
    storage = MemoryStorage()
    adapter, factory = _test_adapter()
    app = _build_proactive_sample_app(storage, adapter)

    await adapter.process_activity(_anonymous_claims(), _message("hi"), app.on_turn)

    assert factory.client.conversations.sent[0].text == (
        "Send **/subscribe** to store this conversation for proactive notifications."
    )
