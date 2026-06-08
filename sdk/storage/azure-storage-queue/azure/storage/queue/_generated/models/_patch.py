# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
import xml.etree.ElementTree as ET
from collections.abc import MutableMapping
from typing import Any, Callable, Dict, List, Optional

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

JSON = MutableMapping[str, Any]


class BackCompatMixin:
    """A mixin to provide backwards compatibility for models
    that used to inherit from msrest models that have now changed to dpg models.
    This mixin should not be used for new models.

    Subclasses must define ``_attribute_map`` and optionally ``_validation``
    just like the old msrest ``Model``.
    """

    _attribute_map: Dict[str, Dict[str, Any]] = {}
    _validation: Dict[str, Dict[str, Any]] = {}
    _xml: Optional[Dict[str, Any]] = None

    def __eq__(self, other: Any) -> bool:
        """Compare objects by comparing all attributes.

        :param object other: The object to compare
        :returns: True if objects are equal
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other: Any) -> bool:
        """Compare objects by comparing all attributes.

        :param object other: The object to compare
        :returns: True if objects are not equal
        :rtype: bool
        """
        return not self.__eq__(other)

    def __str__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def _serialize_value(value: Any, keep_readonly: bool, use_rest_key: bool) -> Any:
        """Recursively serialize a value for ``_to_dict``."""
        if isinstance(value, BackCompatMixin):
            return value._to_dict(  # pylint: disable=protected-access
                keep_readonly=keep_readonly, use_rest_key=use_rest_key
            )
        if isinstance(value, list):
            return [BackCompatMixin._serialize_value(v, keep_readonly, use_rest_key) for v in value]
        if isinstance(value, dict):
            return {k: BackCompatMixin._serialize_value(v, keep_readonly, use_rest_key) for k, v in value.items()}
        return value

    def _to_dict(self, keep_readonly: bool, use_rest_key: bool) -> Dict[str, Any]:
        """Build a dict from ``_attribute_map``.

        :param bool keep_readonly: If False, skip attributes marked readonly.
        :param bool use_rest_key: If True, key the result by the REST wire name
            (e.g. ``Enabled``); if False, key by the Python attribute name
            (e.g. ``enabled``).
        """
        result: Dict[str, Any] = {}
        for attr, desc in self._attribute_map.items():
            if not keep_readonly and self._validation.get(attr, {}).get("readonly", False):
                continue
            value = getattr(self, attr, None)
            if value is None:
                continue
            key = desc["key"] if use_rest_key else attr
            result[key] = self._serialize_value(value, keep_readonly, use_rest_key)
        return result

    def serialize(self, keep_readonly: bool = False, **kwargs: Any) -> JSON:
        """Return the JSON that would be sent to server from this model.

        This is an alias to ``as_dict(full_restapi_key_transformer, keep_readonly=False)``.

        :param bool keep_readonly: If you want to serialize the readonly attributes.
        :returns: A dict JSON compatible object
        :rtype: dict
        """
        return self._to_dict(keep_readonly=keep_readonly, use_rest_key=True)

    def as_dict(
        self,
        keep_readonly: bool = True,
        key_transformer: Optional[Callable[[str, dict, Any], Any]] = None,  # pylint: disable=unused-argument
        **kwargs: Any,
    ) -> JSON:
        """Return a dict that can be serialized using json.dump.

        Keys are the Python attribute names (snake_case), matching the old
        autorest ``Model.as_dict`` default (``attribute_transformer``).

        :param bool keep_readonly: If you want to serialize the readonly attributes.
        :param function key_transformer: A key transformer function (accepted for
            signature compatibility but ignored).
        :returns: A dict JSON compatible object
        :rtype: dict
        """
        return self._to_dict(keep_readonly=keep_readonly, use_rest_key=False)

    @classmethod
    def _from_data(cls, data: Any) -> Self:
        """Create an instance from a dict with REST wire keys (e.g. from ``serialize``).

        Uses ``_attribute_map`` to reverse-map REST keys to Python attribute
        names, then sets them directly (bypassing ``__init__``).
        """
        if isinstance(data, cls):
            return data
        reverse_map = {desc["key"]: attr for attr, desc in cls._attribute_map.items()}
        instance = cls.__new__(cls)
        if isinstance(data, dict):
            for key, value in data.items():
                attr_name = reverse_map.get(key, key)
                setattr(instance, attr_name, value)
        return instance

    @classmethod
    def deserialize(cls, data: Any, content_type: Optional[str] = None) -> Self:
        """Backcompat classmethod for the old autorest ``Model.deserialize``.

        Accepts either a JSON-compatible dict/str or (when ``content_type`` is
        XML) an XML string or ``ElementTree.Element``.
        """
        if content_type and "xml" in content_type.lower():
            if isinstance(data, (bytes, str)):
                data = ET.fromstring(data)  # nosec
            return cls(data)
        return cls._from_data(data)

    @classmethod
    def from_dict(
        cls,
        data: Any,
        key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None,  # pylint: disable=unused-argument
        content_type: Optional[str] = None,
    ) -> Self:
        """Backcompat classmethod for the old autorest ``Model.from_dict``.

        ``key_extractors`` is accepted for signature compatibility but ignored;
        keys are reverse-mapped via ``_attribute_map``.
        """
        if content_type and "xml" in content_type.lower():
            if isinstance(data, (bytes, str)):
                data = ET.fromstring(data)  # nosec
            return cls(data)
        return cls._from_data(data)

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


__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
