# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Replacement ownership and full returned fields on isolated backend targets."""

import asyncio
from copy import deepcopy

import pytest

from azure.cosmos import ThroughputProperties
from common._parity_helpers import (
    run_on_both_backends, run_on_both_backends_async,
    run_target_operation, run_target_operation_async, skip_unless_emulator, skip_unless_rust_binding,
)
from common.throughput_fixtures import (
    container_for as container_for, autoscale_container_for as autoscale_container_for, container_for_backend,
)


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("autoscale", [False, True], ids=["manual", "autoscale"])
@pytest.mark.parametrize("warm", [False, True], ids=["cold", "warm"])
def test_replacement_fields_and_callback_ownership_rust(request, asynchronous, autoscale, warm):
    resources = request.getfixturevalue("autoscale_container_for" if autoscale else "container_for")

    def prepare(client):
        container = container_for_backend(client, resources)
        options = {"initialHeaders": {"x-ms-client-request-id": "container-replacement-parity"}}
        original = deepcopy(options)
        callbacks = []
        throughput = (
            ThroughputProperties(auto_scale_max_throughput=6000, auto_scale_increment_percent=0)
            if autoscale else ThroughputProperties(offer_throughput=500)
        )

        def hook(headers, offer):
            callbacks.append(dict(headers))
            headers.clear()
            offer["content"].clear()
            offer.clear()

        def finish(result):
            assert options == original
            assert callbacks == [dict(result.get_response_headers())]
            assert float(result.get_response_headers()["x-ms-request-charge"]) > 0
            assert result.properties["content"]
            fields = {
                "offer_throughput": result.offer_throughput,
                "auto_scale_max_throughput": result.auto_scale_max_throughput,
                "auto_scale_increment_percent": result.auto_scale_increment_percent,
            }
            assert fields == {
                "offer_throughput": None if autoscale else 500,
                "auto_scale_max_throughput": 6000 if autoscale else None,
                "auto_scale_increment_percent": 0 if autoscale else None,
            }
            return fields

        return container, throughput, options, hook, finish

    def sync_call(client):
        container, throughput, options, hook, finish = prepare(client)
        if warm:
            container.read(timeout=30)
        result = run_target_operation(client, lambda: container.replace_throughput(
            throughput, request_options=options, response_hook=hook, timeout=30,
        ))
        fields = finish(result)
        persisted = container.get_throughput(timeout=30)
        assert persisted.offer_throughput == fields["offer_throughput"]
        assert persisted.auto_scale_max_throughput == fields["auto_scale_max_throughput"]
        assert persisted.auto_scale_increment_percent == fields["auto_scale_increment_percent"]
        return fields

    async def async_call(client):
        container, throughput, options, hook, finish = prepare(client)
        if warm:
            await container.read(timeout=30)
        result = await run_target_operation_async(client, lambda: container.replace_throughput(
            throughput, request_options=options, response_hook=hook, timeout=30,
        ))
        fields = finish(result)
        persisted = await container.get_throughput(timeout=30)
        assert persisted.offer_throughput == fields["offer_throughput"]
        assert persisted.auto_scale_max_throughput == fields["auto_scale_max_throughput"]
        assert persisted.auto_scale_increment_percent == fields["auto_scale_increment_percent"]
        return fields

    comparison = (
        asyncio.run(run_on_both_backends_async(async_call, description="container replacement callback ownership"))
        if asynchronous else run_on_both_backends(sync_call, description="container replacement callback ownership")
    )
    comparison.print_report()
    comparison.assert_functional_parity()
