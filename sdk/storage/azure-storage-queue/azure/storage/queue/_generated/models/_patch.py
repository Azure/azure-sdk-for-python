# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Dict, List, Optional
from .._utils import serialization as _serialization


# These public models inherited (transitively) from the autorest msrest model,
# which exposed ``serialize``, ``deserialize``, ``from_dict``, ``as_dict``,
# ``is_xml_model``, and ``enable_additional_properties_sending``. After the
# migration the generated models use a different base class, so the public
# classes mix this in to preserve the historical method surface.
class _BackCompatMixin(_serialization.Model):
    # The hand-written models define their own ``__init__`` and never call the
    # base ``Model.__init__``, so expose ``additional_properties`` at the class
    # level just as the previous decorator-based approach did.
    additional_properties: Optional[Dict[str, Any]] = None

    # ``Model`` defines ``__eq__`` (value equality), which would otherwise set
    # ``__hash__`` to ``None``. Keep these models hashable by identity, matching
    # their previous behavior.
    def __hash__(self) -> int:
        return object.__hash__(self)


__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
