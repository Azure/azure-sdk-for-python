# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

# TODO: Waiting for emitter release with perf improvements before editing the patch
import xml.etree.ElementTree as ET
from typing import Any, Callable, Dict, List, Optional

from .._utils.model_base import Model as _deserialize
from azure.core.serialization import as_attribute_dict


# ---------------------------------------------------------------------------
# Backcompat shims for public methods that existed on the old autorest msrest models.
# The TypeSpec-generated models inherit from ``_Model`` (a ``MutableMapping`` subclass) which does not
# expose ``serialize``/``deserialize``/``from_dict``/``validate``/
# ``is_xml_model``/``enable_additional_properties_sending``. Re-adding them
# here preserves backward compatibility for users.
# ---------------------------------------------------------------------------


def as_dict(
    self,
    keep_readonly: bool = True,
    key_transformer: Optional[Callable[[str, dict, Any], Any]] = None,  # pylint: disable=unused-argument
    **kwargs: Any,
) -> Dict[str, Any]:
    """Backcompat wrapper that returns Python attribute names (snake_case).

    Accepts both the old autorest signature (``keep_readonly``,
    ``key_transformer``) and the new TypeSpec keyword-only
    ``exclude_readonly`` parameter.  ``key_transformer`` is accepted for
    signature compatibility but ignored; keys are always remapped to
    Python attribute names.
    """
    result = as_attribute_dict(self, exclude_readonly=not keep_readonly)
    return result


class _ModelBackCompatMixin:

    def serialize(self, keep_readonly: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """Backcompat alias for the old autorest ``Model.serialize``.

        Equivalent to ``as_dict(keep_readonly=keep_readonly)`` with REST wire
        names (camelCase) as keys — matching what the old autorest serializer
        sent to the server.
        """
        return as_attribute_dict(self, exclude_readonly=not keep_readonly)

    @classmethod
    def deserialize(cls, data: Any, content_type: Optional[str] = None) -> Any:
        """Backcompat classmethod for the old autorest ``Model.deserialize``.

        Accepts either a JSON-compatible dict/str or (when ``content_type`` is
        XML) an XML string or ``ElementTree.Element``.
        """
        if content_type and "xml" in content_type.lower():
            if isinstance(data, (bytes, str)):
                data = ET.fromstring(data)  # nosec
            return cls(data)
        return _deserialize(cls, data)

    @classmethod
    def from_dict(
        cls,
        data: Any,
        key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None,  # pylint: disable=unused-argument
        content_type: Optional[str] = None,
    ) -> Any:
        """Backcompat classmethod for the old autorest ``Model.from_dict``.

        ``key_extractors`` is accepted for signature compatibility but ignored;
        the TypeSpec deserializer always uses REST-key mapping.
        """
        if content_type and "xml" in content_type.lower():
            if isinstance(data, (bytes, str)):
                data = ET.fromstring(data)  # nosec
            return cls(data)
        return _deserialize(cls, data)

    @classmethod
    def enable_additional_properties_sending(cls) -> None:  # pylint: disable=unused-argument
        """Backcompat no-op for the old autorest ``Model.enable_additional_properties_sending``.

        TypeSpec models already round-trip unknown properties through ``_data``.
        """
        return None

    @classmethod
    def is_xml_model(cls) -> bool:
        """Backcompat classmethod for the old autorest ``Model.is_xml_model``.

        Returns True when the model has an ``_xml`` class attribute (set by the
        generator for models that serialize to/from XML).
        """
        return bool(getattr(cls, "_xml", None))


__all__: List[str] = []


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
