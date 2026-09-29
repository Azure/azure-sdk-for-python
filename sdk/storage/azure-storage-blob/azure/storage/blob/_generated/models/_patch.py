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
from .._utils.model_base import Model as _Model, _RestField
from ._models import (
    CorsRule as _GeneratedCorsRule,
    Logging as _GeneratedLogging,
    Metrics as _GeneratedMetrics,
    RetentionPolicy as _GeneratedRetentionPolicy,
    StaticWebsite as _GeneratedStaticWebsite,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


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
        **kwargs: Any,
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


# For backwards compatibility with older releases of `azure-storage-file-datalake`
# that have models that inherit from the _generated.models of `azure-storage-blob` directly
def _patched_getattr(self, name):
    """Lazily initialize ``_data`` for subclasses that skip ``super().__init__()``.

    Older releases of ``azure-storage-file-datalake`` subclass these blob generated XML models and set rest_field
    attributes directly inside their own ``__init__`` without ever calling
    ``super().__init__()`` - so typespec's ``_Model.__init__`` (the one that creates
    ``_data``) is never invoked. The first attribute write would otherwise raise
    ``AttributeError`` deep inside ``_RestField.__set__``.
    """
    if name == "_data":
        object.__setattr__(self, "_data", {})
        return self._data
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


def _patched_setattr(self, name, value):
    """Route attribute writes through the inherited ``_RestField`` descriptors.

    Datalake subclasses redeclare class attributes (``version: str = "1.0"``) which
    shadow the parent class's ``_RestField`` descriptors. Without this patch,
    ``self.version = "1.0"`` would write to ``instance.__dict__`` and never populate
    ``self._data`` - leaving the wire payload empty.
    """
    if not name.startswith("_"):
        try:
            rf = type(self)._attr_to_rest_field.get(name)
        except AttributeError:
            rf = None
        if rf is not None:
            rf.__set__(self, value)
            return
    object.__setattr__(self, name, value)


def _patched_getattribute(self, name):
    """Route attribute reads through the inherited ``_RestField`` descriptors.

    Counterpart to ``_patched_setattr``: reads also need to hit ``_data`` (where
    ``__set__`` writes), not the shadowed class attribute on the subclass.
    """
    if not name.startswith("_"):
        try:
            rest_fields = type(self)._attr_to_rest_field
        except AttributeError:
            rest_fields = None
        if rest_fields is not None:
            rf = rest_fields.get(name)
            if rf is not None:
                return rf.__get__(self, type(self))
    return object.__getattribute__(self, name)


# The original ``_Model.__new__`` does ``rf._module = cls.__module__``, which lets an
# external subclass (e.g. from ``azure-storage-file-datalake``) overwrite ``_module``
# on the *shared* descriptor instance, corrupting type resolution for every class
# that shares it. This replacement resolves forward references against the module
# that *defined* the rest_field instead.
def _patched_new(cls, *args, **kwargs):  # pylint: disable=unused-argument
    if f"{cls.__module__}.{cls.__qualname__}" not in cls._calculated:
        user_classes = []
        for c in cls.__mro__:
            if c is _Model:
                break
            user_classes.append(c)

        attr_to_rest_field: Dict[str, _RestField] = {}
        for mro_class in reversed(user_classes):
            annotations = getattr(mro_class, "__annotations__", {})
            for k, v in mro_class.__dict__.items():
                if not k.startswith("_") and isinstance(v, _RestField):
                    attr_to_rest_field[k] = v
                    v._module = mro_class.__module__
                    if not v._type:
                        v._type = v._get_deserialize_callable_from_annotation(annotations.get(k, None))
                    if not v._rest_name_input:
                        v._rest_name_input = k

        cls._attr_to_rest_field = attr_to_rest_field
        cls._backcompat_attr_to_rest_field = {
            _Model._get_backcompat_attribute_name(cls._attr_to_rest_field, attr): rf
            for attr, rf in cls._attr_to_rest_field.items()
        }
        cls._rest_name_to_attr = {rf._rest_name: attr for attr, rf in attr_to_rest_field.items()}
        cls._calculated.add(f"{cls.__module__}.{cls.__qualname__}")

    instance = object.__new__(cls)
    object.__setattr__(instance, "_data", {})
    return instance


def _apply_back_compat_to_generated(
    cls: type,
    attribute_map: Dict[str, Dict[str, str]],
    validation: Dict[str, Dict[str, Any]],
    xml_name: str,
) -> None:
    """Retrofit the msrest ``Model`` surface onto a trivial subclass of a typespec
    generated class.

    :param cls: the trivial back-compat subclass defined in this module.
    :param attribute_map: the historical msrest ``_attribute_map``.
    :param validation: the historical msrest ``_validation`` map.
    :param xml_name: the historical XML node name.
    """
    cls._attribute_map = attribute_map  # type: ignore[attr-defined]
    cls._validation = validation  # type: ignore[attr-defined]
    cls._xml_map = {"name": xml_name}  # type: ignore[attr-defined]
    cls.serialize = _BackCompatMixin.serialize  # type: ignore[attr-defined]
    cls.as_dict = _BackCompatMixin.as_dict  # type: ignore[attr-defined]
    cls.deserialize = classmethod(Model.deserialize.__func__)  # type: ignore[attr-defined]
    cls.from_dict = classmethod(Model.from_dict.__func__)  # type: ignore[attr-defined]
    cls.enable_additional_properties_sending = classmethod(  # type: ignore[attr-defined]
        Model.enable_additional_properties_sending.__func__
    )
    cls.is_xml_model = classmethod(Model.is_xml_model.__func__)  # type: ignore[attr-defined]
    cls._infer_class_models = classmethod(Model._infer_class_models.__func__)  # type: ignore[attr-defined]
    cls._create_xml_node = classmethod(Model._create_xml_node.__func__)  # type: ignore[attr-defined]
    cls._to_generated = lambda self: self  # type: ignore[attr-defined]

    cls.__new__ = _patched_new  # type: ignore[assignment]
    cls.__getattr__ = _patched_getattr  # type: ignore[attr-defined]
    cls.__setattr__ = _patched_setattr  # type: ignore[assignment]
    cls.__getattribute__ = _patched_getattribute  # type: ignore[assignment]


class Logging(_GeneratedLogging):
    """Back-compat subclass of the generated ``Logging`` that retains the msrest
    ``Model`` API surface (``serialize``/``as_dict``/``deserialize``/etc.) and routes
    attribute writes through the rest_field descriptors. Required for the still-on-PyPI
    ``azure-storage-file-datalake`` whose ``AnalyticsLogging.__init__`` does direct
    ``self.attr = value`` writes without calling ``super().__init__()``."""


class Metrics(_GeneratedMetrics):
    """Back-compat subclass of the generated ``Metrics``. See :class:`Logging`."""


class RetentionPolicy(_GeneratedRetentionPolicy):
    """Back-compat subclass of the generated ``RetentionPolicy``. See :class:`Logging`."""


class CorsRule(_GeneratedCorsRule):
    """Back-compat subclass of the generated ``CorsRule``. See :class:`Logging`."""


class StaticWebsite(_GeneratedStaticWebsite):
    """Back-compat subclass of the generated ``StaticWebsite``. See :class:`Logging`."""


_apply_back_compat_to_generated(
    Logging,
    attribute_map={
        "version": {"key": "Version", "type": "str"},
        "delete": {"key": "Delete", "type": "bool"},
        "read": {"key": "Read", "type": "bool"},
        "write": {"key": "Write", "type": "bool"},
        "retention_policy": {"key": "RetentionPolicy", "type": "RetentionPolicy"},
    },
    validation={
        "version": {"required": True},
        "delete": {"required": True},
        "read": {"required": True},
        "write": {"required": True},
        "retention_policy": {"required": True},
    },
    xml_name="Logging",
)

_apply_back_compat_to_generated(
    Metrics,
    attribute_map={
        "version": {"key": "Version", "type": "str"},
        "enabled": {"key": "Enabled", "type": "bool"},
        "include_apis": {"key": "IncludeAPIs", "type": "bool"},
        "retention_policy": {"key": "RetentionPolicy", "type": "RetentionPolicy"},
    },
    validation={
        "enabled": {"required": True},
    },
    xml_name="Metrics",
)

_apply_back_compat_to_generated(
    RetentionPolicy,
    attribute_map={
        "enabled": {"key": "Enabled", "type": "bool"},
        "days": {"key": "Days", "type": "int"},
        "allow_permanent_delete": {"key": "AllowPermanentDelete", "type": "bool"},
    },
    validation={
        "enabled": {"required": True},
        "days": {"minimum": 1},
    },
    xml_name="RetentionPolicy",
)

_apply_back_compat_to_generated(
    CorsRule,
    attribute_map={
        "allowed_origins": {"key": "AllowedOrigins", "type": "str"},
        "allowed_methods": {"key": "AllowedMethods", "type": "str"},
        "allowed_headers": {"key": "AllowedHeaders", "type": "str"},
        "exposed_headers": {"key": "ExposedHeaders", "type": "str"},
        "max_age_in_seconds": {"key": "MaxAgeInSeconds", "type": "int"},
    },
    validation={
        "allowed_origins": {"required": True},
        "allowed_methods": {"required": True},
        "allowed_headers": {"required": True},
        "exposed_headers": {"required": True},
        "max_age_in_seconds": {"required": True, "minimum": 0},
    },
    xml_name="CorsRule",
)

_apply_back_compat_to_generated(
    StaticWebsite,
    attribute_map={
        "enabled": {"key": "Enabled", "type": "bool"},
        "index_document": {"key": "IndexDocument", "type": "str"},
        "error_document404_path": {"key": "ErrorDocument404Path", "type": "str"},
        "default_index_document_path": {"key": "DefaultIndexDocumentPath", "type": "str"},
    },
    validation={
        "enabled": {"required": True},
    },
    xml_name="StaticWebsite",
)


__all__: List[str] = [
    "Logging",
    "Metrics",
    "RetentionPolicy",
    "CorsRule",
    "StaticWebsite",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
