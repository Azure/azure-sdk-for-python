# pylint: disable=too-many-lines
# coding=utf-8
# pylint: disable=useless-super-delegation

import datetime
import functools
from typing import Any, Mapping, Optional, TYPE_CHECKING, Union, overload

from .._utils.model_base import (
    Model as _Model,
    _xml_deser_bool,
    _xml_deser_datetime,
    _xml_deser_datetime_rfc7231,
    _xml_deser_enum_or_str,
    _xml_deser_int,
    _xml_deser_str,
    rest_field,
)
from ._enums import Status

if TYPE_CHECKING:
    from .. import models as _models


class Author(_Model):
    """Author model with a custom XML name.

    :ivar name: Required.
    :vartype name: str
    """

    name: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "name", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""

    _xml = {"name": "XmlAuthor", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        name: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Book(_Model):
    """Book model with a custom XML name.

    :ivar title: Required.
    :vartype title: str
    """

    title: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "title", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""

    _xml = {"name": "XmlBook", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        title: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithArrayOfModel(_Model):
    """§4.1 — Contains an array of models.

    :ivar items_property: Required.
    :vartype items_property: ~payload.xml.models.SimpleModel
    """

    items_property: list["_models.SimpleModel"] = rest_field(
        name="items",
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "items", "attribute": False, "unwrapped": False, "text": False, "itemsName": "SimpleModel"},
        original_tsp_name="items",
    )
    """Required."""

    _xml = {"name": "ModelWithArrayOfModel", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        items_property: list["_models.SimpleModel"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithAttributes(_Model):
    """§5.1 — Contains fields that are XML attributes.

    :ivar id1: Required.
    :vartype id1: int
    :ivar id2: Required.
    :vartype id2: str
    :ivar enabled: Required.
    :vartype enabled: bool
    """

    id1: int = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "id1", "attribute": True, "unwrapped": False, "text": False},
        deserializer=_xml_deser_int,
    )
    """Required."""
    id2: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "id2", "attribute": True, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""
    enabled: bool = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "enabled", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_bool,
    )
    """Required."""

    _xml = {"name": "ModelWithAttributes", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        id1: int,
        id2: str,
        enabled: bool,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithDatetime(_Model):
    """Contains datetime properties with different encodings.

    :ivar rfc3339: DateTime value with rfc3339 encoding. Required.
    :vartype rfc3339: ~datetime.datetime
    :ivar rfc7231: DateTime value with rfc7231 encoding. Required.
    :vartype rfc7231: ~datetime.datetime
    """

    rfc3339: datetime.datetime = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        format="rfc3339",
        xml={"name": "rfc3339", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_datetime,
    )
    """DateTime value with rfc3339 encoding. Required."""
    rfc7231: datetime.datetime = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        format="rfc7231",
        xml={"name": "rfc7231", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_datetime_rfc7231,
    )
    """DateTime value with rfc7231 encoding. Required."""

    _xml = {"name": "ModelWithDatetime", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        rfc3339: datetime.datetime,
        rfc7231: datetime.datetime,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithDictionary(_Model):
    """Contains a dictionary of key value pairs.

    :ivar metadata: Required.
    :vartype metadata: dict[str, str]
    """

    metadata: dict[str, str] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "metadata", "attribute": False, "unwrapped": False, "text": False},
    )
    """Required."""

    _xml = {"name": "ModelWithDictionary", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        metadata: dict[str, str],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithEmptyArray(_Model):
    """Contains an array of models that's supposed to be sent/received as an empty XML element.

    :ivar items_property: Required.
    :vartype items_property: ~payload.xml.models.SimpleModel
    """

    items_property: list["_models.SimpleModel"] = rest_field(
        name="items",
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "items", "attribute": False, "unwrapped": False, "text": False, "itemsName": "SimpleModel"},
        original_tsp_name="items",
    )
    """Required."""

    _xml = {"name": "ModelWithEmptyArray", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        items_property: list["_models.SimpleModel"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithEncodedNames(_Model):
    """Uses encodedName instead of Xml.Name which is functionally equivalent.

    :ivar model_data: Required.
    :vartype model_data: ~payload.xml.models.SimpleModel
    :ivar colors: Required.
    :vartype colors: list[str]
    """

    model_data: "_models.SimpleModel" = rest_field(
        name="modelData",
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "SimpleModelData", "attribute": False, "unwrapped": False, "text": False},
    )
    """Required."""
    colors: list[str] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "PossibleColors", "attribute": False, "unwrapped": False, "text": False, "itemsName": "string"},
    )
    """Required."""

    _xml = {"name": "ModelWithEncodedNamesSrc", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        model_data: "_models.SimpleModel",
        colors: list[str],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithEnum(_Model):
    """Contains a single property with an enum value.

    :ivar status: Required. Known values are: "pending", "success", and "error".
    :vartype status: str or ~payload.xml.models.Status
    """

    status: Union[str, "_models.Status"] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "status", "attribute": False, "unwrapped": False, "text": False},
        deserializer=functools.partial(_xml_deser_enum_or_str, Status),
    )
    """Required. Known values are: \"pending\", \"success\", and \"error\"."""

    _xml = {"name": "ModelWithEnum", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        status: Union[str, "_models.Status"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithNamespace(_Model):
    """§6.1, §7.1 — Contains fields with XML namespace on the model.

    :ivar id: Required.
    :vartype id: int
    :ivar title: Required.
    :vartype title: str
    """

    id: int = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "id", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_int,
    )
    """Required."""
    title: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "title", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""

    _xml = {
        "name": "ModelWithNamespace",
        "namespace": "http://example.com/schema",
        "prefix": "smp",
        "attribute": False,
        "unwrapped": False,
        "text": False,
    }

    @overload
    def __init__(
        self,
        *,
        id: int,  # pylint: disable=redefined-builtin
        title: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithNamespaceOnProperties(_Model):
    """§6.2, §7.2 — Contains fields with different XML namespaces on individual properties.

    :ivar id: Required.
    :vartype id: int
    :ivar title: Required.
    :vartype title: str
    :ivar author: Required.
    :vartype author: str
    """

    id: int = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "id", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_int,
    )
    """Required."""
    title: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={
            "name": "title",
            "namespace": "http://example.com/schema",
            "prefix": "smp",
            "attribute": False,
            "unwrapped": False,
            "text": False,
        },
        deserializer=_xml_deser_str,
    )
    """Required."""
    author: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={
            "name": "author",
            "namespace": "http://example.com/ns2",
            "prefix": "ns2",
            "attribute": False,
            "unwrapped": False,
            "text": False,
        },
        deserializer=_xml_deser_str,
    )
    """Required."""

    _xml = {
        "name": "ModelWithNamespaceOnProperties",
        "namespace": "http://example.com/schema",
        "prefix": "smp",
        "attribute": False,
        "unwrapped": False,
        "text": False,
    }

    @overload
    def __init__(
        self,
        *,
        id: int,  # pylint: disable=redefined-builtin
        title: str,
        author: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithNestedModel(_Model):
    """§2.1 — Contains a property that references another model.

    :ivar nested: Required.
    :vartype nested: ~payload.xml.models.SimpleModel
    """

    nested: "_models.SimpleModel" = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "nested", "attribute": False, "unwrapped": False, "text": False},
    )
    """Required."""

    _xml = {"name": "ModelWithNestedModel", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        nested: "_models.SimpleModel",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithOptionalField(_Model):
    """Contains an optional field.

    :ivar item: Required.
    :vartype item: str
    :ivar value:
    :vartype value: int
    """

    item: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "item", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""
    value: Optional[int] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "value", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_int,
    )

    _xml = {"name": "ModelWithOptionalField", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        item: str,
        value: Optional[int] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithRenamedArrays(_Model):
    """§3.3, §3.4 — Contains fields of wrapped and unwrapped arrays of primitive types that have
    different XML representations.

    :ivar colors: Required.
    :vartype colors: list[str]
    :ivar counts: Required.
    :vartype counts: list[int]
    """

    colors: list[str] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "Colors", "attribute": False, "unwrapped": True, "text": False, "itemsName": "Colors"},
    )
    """Required."""
    counts: list[int] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "Counts", "attribute": False, "unwrapped": False, "text": False, "itemsName": "int32"},
    )
    """Required."""

    _xml = {"name": "ModelWithRenamedArrays", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        colors: list[str],
        counts: list[int],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithRenamedAttribute(_Model):
    """§5.2 — Contains a renamed XML attribute.

    :ivar id: Required.
    :vartype id: int
    :ivar title: Required.
    :vartype title: str
    :ivar author: Required.
    :vartype author: str
    """

    id: int = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "xml-id", "attribute": True, "unwrapped": False, "text": False},
        deserializer=_xml_deser_int,
    )
    """Required."""
    title: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "title", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""
    author: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "author", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""

    _xml = {"name": "ModelWithRenamedAttribute", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        id: int,  # pylint: disable=redefined-builtin
        title: str,
        author: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithRenamedFields(_Model):
    """§1.3, §2.3 — Contains fields of the same type that have different XML representation.

    :ivar input_data: Required.
    :vartype input_data: ~payload.xml.models.SimpleModel
    :ivar output_data: Required.
    :vartype output_data: ~payload.xml.models.SimpleModel
    """

    input_data: "_models.SimpleModel" = rest_field(
        name="inputData",
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "InputData", "attribute": False, "unwrapped": False, "text": False},
    )
    """Required."""
    output_data: "_models.SimpleModel" = rest_field(
        name="outputData",
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "OutputData", "attribute": False, "unwrapped": False, "text": False},
    )
    """Required."""

    _xml = {"name": "ModelWithRenamedFieldsSrc", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        input_data: "_models.SimpleModel",
        output_data: "_models.SimpleModel",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithRenamedNestedModel(_Model):
    """§2.2 — Contains a property whose type has.

    :ivar author: Required.
    :vartype author: ~payload.xml.models.Author
    """

    author: "_models.Author" = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "author", "attribute": False, "unwrapped": False, "text": False},
    )
    """Required."""

    _xml = {"name": "ModelWithRenamedNestedModel", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        author: "_models.Author",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithRenamedProperty(_Model):
    """§1.2 — Contains a scalar property with a custom XML name.

    :ivar title: Required.
    :vartype title: str
    :ivar author: Required.
    :vartype author: str
    """

    title: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "renamedTitle", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""
    author: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "author", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""

    _xml = {"name": "ModelWithRenamedProperty", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        title: str,
        author: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithRenamedUnwrappedModelArray(_Model):
    """§4.4 — Contains an unwrapped array of models with a custom item name.

    :ivar items_property: Required.
    :vartype items_property: ~payload.xml.models.SimpleModel
    """

    items_property: list["_models.SimpleModel"] = rest_field(
        name="items",
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "ModelItem", "attribute": False, "unwrapped": True, "text": False, "itemsName": "ModelItem"},
        original_tsp_name="items",
    )
    """Required."""

    _xml = {"name": "ModelWithRenamedUnwrappedModelArray", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        items_property: list["_models.SimpleModel"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithRenamedWrappedAndItemModelArray(_Model):
    """§4.5 — Contains a wrapped array of models with custom wrapper and item names.

    :ivar books: Required.
    :vartype books: ~payload.xml.models.Book
    """

    books: list["_models.Book"] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "AllBooks", "attribute": False, "unwrapped": False, "text": False, "itemsName": "XmlBook"},
    )
    """Required."""

    _xml = {"name": "ModelWithRenamedWrappedAndItemModelArray", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        books: list["_models.Book"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithRenamedWrappedModelArray(_Model):
    """§4.3 — Contains a wrapped array of models with a custom wrapper name.

    :ivar items_property: Required.
    :vartype items_property: ~payload.xml.models.SimpleModel
    """

    items_property: list["_models.SimpleModel"] = rest_field(
        name="items",
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "AllItems", "attribute": False, "unwrapped": False, "text": False, "itemsName": "SimpleModel"},
        original_tsp_name="items",
    )
    """Required."""

    _xml = {"name": "ModelWithRenamedWrappedModelArray", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        items_property: list["_models.SimpleModel"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithSimpleArrays(_Model):
    """§3.1 — Contains fields of arrays of primitive types.

    :ivar colors: Required.
    :vartype colors: list[str]
    :ivar counts: Required.
    :vartype counts: list[int]
    """

    colors: list[str] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "colors", "attribute": False, "unwrapped": False, "text": False, "itemsName": "string"},
    )
    """Required."""
    counts: list[int] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "counts", "attribute": False, "unwrapped": False, "text": False, "itemsName": "int32"},
    )
    """Required."""

    _xml = {"name": "ModelWithSimpleArrays", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        colors: list[str],
        counts: list[int],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithText(_Model):
    """§8.1 — Contains an attribute and text.

    :ivar language: Required.
    :vartype language: str
    :ivar content: Required.
    :vartype content: str
    """

    language: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "language", "attribute": True, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""
    content: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "content", "attribute": False, "unwrapped": False, "text": True},
        deserializer=_xml_deser_str,
    )
    """Required."""

    _xml = {"name": "ModelWithText", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        language: str,
        content: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithUnwrappedArray(_Model):
    """§3.2 — Contains fields of wrapped and unwrapped arrays of primitive types.

    :ivar colors: Required.
    :vartype colors: list[str]
    :ivar counts: Required.
    :vartype counts: list[int]
    """

    colors: list[str] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "colors", "attribute": False, "unwrapped": True, "text": False, "itemsName": "colors"},
    )
    """Required."""
    counts: list[int] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "counts", "attribute": False, "unwrapped": False, "text": False, "itemsName": "int32"},
    )
    """Required."""

    _xml = {"name": "ModelWithUnwrappedArray", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        colors: list[str],
        counts: list[int],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithUnwrappedModelArray(_Model):
    """§4.2 — Contains an unwrapped array of models.

    :ivar items_property: Required.
    :vartype items_property: ~payload.xml.models.SimpleModel
    """

    items_property: list["_models.SimpleModel"] = rest_field(
        name="items",
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "items", "attribute": False, "unwrapped": True, "text": False, "itemsName": "items"},
        original_tsp_name="items",
    )
    """Required."""

    _xml = {"name": "ModelWithUnwrappedModelArray", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        items_property: list["_models.SimpleModel"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithWrappedPrimitiveCustomItemNames(_Model):
    """§3.5 — Contains a wrapped primitive array with custom wrapper and item names.

    :ivar tags: Required.
    :vartype tags: list[str]
    """

    tags: list[str] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "ItemsTags", "attribute": False, "unwrapped": False, "text": False, "itemsName": "ItemName"},
    )
    """Required."""

    _xml = {"name": "ModelWithWrappedPrimitiveCustomItemNames", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        tags: list[str],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SimpleModel(_Model):
    """§1.1 — Contains fields of primitive types.

    :ivar name: Required.
    :vartype name: str
    :ivar age: Required.
    :vartype age: int
    """

    name: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "name", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""
    age: int = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "age", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_int,
    )
    """Required."""

    _xml = {"name": "SimpleModel", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        name: str,
        age: int,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class XmlErrorBody(_Model):
    """The body of an XML error response.

    :ivar message: Required.
    :vartype message: str
    :ivar code: Required.
    :vartype code: int
    """

    message: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "message", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_str,
    )
    """Required."""
    code: int = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"name": "code", "attribute": False, "unwrapped": False, "text": False},
        deserializer=_xml_deser_int,
    )
    """Required."""

    _xml = {"name": "XmlErrorBody", "attribute": False, "unwrapped": False, "text": False}

    @overload
    def __init__(
        self,
        *,
        message: str,
        code: int,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
