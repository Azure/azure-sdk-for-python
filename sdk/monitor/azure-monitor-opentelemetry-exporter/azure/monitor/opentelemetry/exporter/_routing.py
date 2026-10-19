# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from opentelemetry.util.types import Attributes

from azure.monitor.opentelemetry.exporter._constants import _MICROSOFT_INSTRUMENTATION_KEY

_MAX_INSTRUMENTATION_KEY_LENGTH = 200


def _get_instrumentation_key(attributes: Attributes) -> str:
    """Validate a routed key independently of connection-string UUID validation.

    :param attributes: The telemetry item's attributes.
    :type attributes: ~opentelemetry.util.types.Attributes
    :return: The trimmed instrumentation key.
    :rtype: str
    :raises ValueError: If the key is missing, invalid, or longer than 200 characters.
    """
    key = attributes.get(_MICROSOFT_INSTRUMENTATION_KEY) if attributes else None
    if not isinstance(key, str):
        raise ValueError("Routing instrumentation key must be a nonempty string.")
    if len(key) > _MAX_INSTRUMENTATION_KEY_LENGTH:
        raise ValueError("Routing instrumentation key must not exceed 200 characters.")
    key = key.strip()
    if not key:
        raise ValueError("Routing instrumentation key must be a nonempty string.")
    return key
