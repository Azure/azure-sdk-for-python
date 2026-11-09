# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from io import BytesIO
from typing import Any, Awaitable, Callable, Mapping
from uuid import UUID

from ._external_evaluation import PolicyTokenRequestContext


def _check_subscription(context: PolicyTokenRequestContext, subscription_id: str) -> None:
    if context.subscription_id.lower() != subscription_id:
        raise ValueError("The policy-token provider is configured for a different subscription.")


def create_policy_token_provider(
    acquire_policy_token: Callable[..., Mapping[str, Any]], *, subscription_id: str
) -> Callable[[PolicyTokenRequestContext], Mapping[str, Any]]:
    """Create a default synchronous callback for an external-evaluation policy.

    Bind the callback to a separate Policy client's ``policy_tokens.acquire``
    method. The client must use the same trusted ARM cloud/endpoint as the guarded
    resource client and must not contain an external-evaluation policy. This helper
    does not create or close that client, or add a dependency on the Policy package.

    The callback preserves the original serialized JSON, rejects operations from
    another subscription, and disables acquisition redirects and raw HTTP logging.
    Custom providers can still be supplied directly to ``ExternalEvaluationPolicy``.

    :param acquire_policy_token: The bound ``policy_tokens.acquire`` method.
    :type acquire_policy_token: callable[..., Mapping[str, Any]]
    :keyword str subscription_id: The subscription used to construct the Policy client.
    :return: A callback suitable for ``ExternalEvaluationPolicy``.
    :rtype: callable[[~azure.mgmt.core.policies.PolicyTokenRequestContext], Mapping[str, Any]]
    :raises ValueError: If the subscription ID is invalid, or the callback receives
        an operation for a different subscription.
    """
    if not callable(acquire_policy_token):
        raise TypeError("acquire_policy_token must be callable.")
    expected_subscription = str(UUID(subscription_id))

    def provider(context: PolicyTokenRequestContext) -> Mapping[str, Any]:
        _check_subscription(context, expected_subscription)
        with BytesIO(context.get_request_body()) as body:
            return acquire_policy_token(body, logging_enable=False, permit_redirects=False)

    return provider


def create_async_policy_token_provider(
    acquire_policy_token: Callable[..., Awaitable[Mapping[str, Any]]], *, subscription_id: str
) -> Callable[[PolicyTokenRequestContext], Awaitable[Mapping[str, Any]]]:
    """Create a default asynchronous callback for an external-evaluation policy.

    Bind the callback to a separate async Policy client's ``policy_tokens.acquire``
    method. The caller owns the client and its lifetime. The client must use the
    same trusted ARM cloud/endpoint as the guarded resource client and must not
    contain an external-evaluation policy.

    Like the synchronous helper, the callback preserves serialized JSON, checks
    the subscription, and disables acquisition redirects and raw HTTP logging.
    Acquisition is awaited; errors and cancellation are not intercepted.

    :param acquire_policy_token: The bound async ``policy_tokens.acquire`` method.
    :type acquire_policy_token: callable[..., Awaitable[Mapping[str, Any]]]
    :keyword str subscription_id: The subscription used to construct the Policy client.
    :return: An async callback suitable for ``AsyncExternalEvaluationPolicy``.
    :rtype: callable[[~azure.mgmt.core.policies.PolicyTokenRequestContext], Awaitable[Mapping[str, Any]]]
    :raises ValueError: If the subscription ID is invalid, or the callback receives
        an operation for a different subscription.
    """
    if not callable(acquire_policy_token):
        raise TypeError("acquire_policy_token must be callable.")
    expected_subscription = str(UUID(subscription_id))

    async def provider(context: PolicyTokenRequestContext) -> Mapping[str, Any]:
        _check_subscription(context, expected_subscription)
        with BytesIO(context.get_request_body()) as body:
            return await acquire_policy_token(body, logging_enable=False, permit_redirects=False)

    return provider
