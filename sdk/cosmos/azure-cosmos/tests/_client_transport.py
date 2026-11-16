# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Inject test senders at the retained pipeline, not through public client options."""

import importlib
from unittest.mock import patch


def create_client_with_transport(factory, *args, transport=None, **kwargs):
    if transport is None:
        return factory(*args, **kwargs)
    async_mode = "aio" in factory.__module__.split(".")
    module = importlib.import_module(
        "azure.cosmos.aio._cosmos_client_connection_async"
        if async_mode else "azure.cosmos._cosmos_client_connection"
    )
    name = "AsyncPipelineClient" if async_mode else "PipelineClient"
    pipeline_factory = getattr(module, name)

    def create_pipeline(*pipeline_args, **pipeline_kwargs):
        return pipeline_factory(*pipeline_args, transport=transport, **pipeline_kwargs)

    with patch.object(module, name, side_effect=create_pipeline):
        client = factory(*args, **kwargs)
        # Materialize the deferred async pipeline while its factory is patched.
        _ = client.client_connection.pipeline_client
    return client
