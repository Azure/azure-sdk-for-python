# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
from typing import Any, Callable, Dict, List, Optional

from .._utils.serialization import JSON, Model, attribute_transformer

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


# These public models inherited (transitively) from the autorest msrest model,
# which exposed ``serialize``, ``deserialize``, ``from_dict``, ``as_dict``,
# ``is_xml_model``, and ``enable_additional_properties_sending``. After the
# migration the generated models use a different base class. The public classes mix this in to expose
# exactly the historical methods, each delegating to ``Model``.
class _BackCompatMixin:
    _validation = {}

    def serialize(self, keep_readonly: bool = False, **kwargs: Any) -> JSON:
        """Serialize this model to a dictionary.

        :param bool keep_readonly: If you want to serialize the readonly attributes.
        :returns: A dict JSON compatible object.
        :rtype: JSON
        """
        return Model.serialize(self, keep_readonly=keep_readonly, **kwargs)  # type: ignore[arg-type]

    def as_dict(
        self,
        keep_readonly: bool = True,
        key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer,
        **kwargs: Any
    ) -> JSON:
        """Return a dict that can be serialized using json.dump.

        :param bool keep_readonly: If you want to serialize the readonly attributes.
        :param key_transformer: A function that takes an attribute name, the attribute map, and the value, and returns the key to use in the output dict.
        :returns: A dict JSON compatible object.
        :rtype: JSON
        """
        return Model.as_dict(self, keep_readonly=keep_readonly, key_transformer=key_transformer, **kwargs)  # type: ignore[arg-type]

    @classmethod
    def deserialize(cls, data: Any, content_type: Optional[str] = None) -> Self:
        """Deserialize this model from a dictionary.

        :param data: A str using RestAPI structure. JSON by default.
        :type data: str
        :param str content_type: JSON by default, set application/xml if XML.
        :returns: An instance of this model.
        :rtype: Self
        """
        # ``Model.deserialize`` is a classmethod already bound to ``Model``; reach
        # through ``__func__`` so it runs with this subclass as ``cls``.
        return Model.deserialize.__func__(cls, data, content_type=content_type)

    @classmethod
    def from_dict(
        cls,
        data: Any,
        key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None,
        content_type: Optional[str] = None,
    ) -> Self:
        """Parse a dict using a given key extractor and return a model.

        :param dict data: A dict using RestAPI structure.
        :param key_extractors: A key extractor function.
        :type key_extractors: callable or None
        :param str content_type: JSON by default, set application/xml if XML.
        :returns: An instance of this model.
        :rtype: Self
        """
        return Model.from_dict.__func__(cls, data, key_extractors=key_extractors, content_type=content_type)

    @classmethod
    def enable_additional_properties_sending(cls) -> None:
        """Add ``additional_properties`` to the attribute map so they are sent to the service.

        :returns: None
        :rtype: None
        """
        return Model.enable_additional_properties_sending.__func__(cls)

    @classmethod
    def is_xml_model(cls) -> bool:
        """Whether this model is serialized as XML.

        :returns: True if this model is serialized as XML, otherwise False.
        :rtype: bool
        """
        return Model.is_xml_model.__func__(cls)

    @classmethod
    def _infer_class_models(cls) -> Dict[str, type]:
        # Internal helper used by serialize/as_dict/deserialize/from_dict.
        return Model._infer_class_models.__func__(cls)

    @classmethod
    def _create_xml_node(cls) -> Any:
        # Internal helper used during XML (de)serialization.
        return Model._create_xml_node.__func__(cls)

    def __eq__(self, other: Any) -> bool:
        return Model.__eq__(self, other)  # type: ignore[arg-type]

    def __ne__(self, other: Any) -> bool:
        return Model.__ne__(self, other)  # type: ignore[arg-type]

    def __str__(self) -> str:
        return Model.__str__(self)  # type: ignore[arg-type]


__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
