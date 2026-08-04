# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic builders for serverless-endpoint and marketplace-subscription entities.

These ``_autogen_entities`` models had their REST types migrated off the versioned msrest clients
(``ServerlessEndpoint``/``MarketplaceSubscription``/``ModelSettings``/``Sku`` from v2024_01 and the
openai-deployment types from v2024_04) onto ``arm_ml_service``. The migration also dropped the
``auth_mode="key"`` kwarg the old msrest model silently ignored. This pins their request bodies
byte-for-byte across the swap. ``_to_rest_object()`` is a no-arg method matching the suite contract.
"""
from azure.ai.ml.entities import MarketplaceSubscription, ServerlessEndpoint

_MODEL_ID = "azureml://registries/azureml-meta/models/Meta-Llama-3.1-8B-Instruct/versions/1"


def build_serverless_endpoint():
    """ServerlessEndpoint with model id, location and tags."""
    return ServerlessEndpoint(
        name="smoke-serverless-endpoint",
        model_id=_MODEL_ID,
        location="westus",
        tags={"tag1": "value1", "team": "smoke"},
    )


def build_marketplace_subscription():
    """MarketplaceSubscription for a marketplace model."""
    return MarketplaceSubscription(
        name="smoke-marketplace-sub",
        model_id=_MODEL_ID,
    )


SERVERLESS_BUILDERS = {
    "serverless_endpoint": build_serverless_endpoint,
    "marketplace_subscription": build_marketplace_subscription,
}
