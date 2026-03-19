"""Step A contract-freeze checks for Phase E parity naming."""

from __future__ import annotations

import asyncio

from azure.ai.agentserver.responses._handlers import RuntimeResponseContext
from azure.ai.agentserver.responses.store._base import ResponseProviderProtocol
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider


async def _empty_loader() -> tuple[()]:
    return ()


def test_phase_e_contract_freeze__provider_contract_maps_to_responseproviderprotocol() -> None:
    provider = InMemoryResponseProvider()

    assert isinstance(provider, ResponseProviderProtocol)


def test_phase_e_contract_freeze__runtime_context_exposes_async_contract() -> None:
    context = RuntimeResponseContext(
        response_id="resp_step_a",
        mode_flags=0,
        _input_items_loader=_empty_loader,
        _history_loader=_empty_loader,
    )

    input_items = asyncio.run(context.get_input_items_async())
    history_items = asyncio.run(context.get_history_async())

    assert input_items == ()
    assert history_items == ()
