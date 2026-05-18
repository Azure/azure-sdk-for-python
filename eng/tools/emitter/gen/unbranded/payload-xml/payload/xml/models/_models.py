# pylint: disable=too-many-lines
# coding=utf-8
# pylint: disable=useless-super-delegation

import datetime
from typing import Any, Mapping, Optional, TYPE_CHECKING, Union, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import models as _models


class Author(_Model):
    """Author model with a custom XML name.

    :ivar name: Required.
    :vartype name: str
    """

    name: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "name", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "XmlAuthor", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "title", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "XmlBook", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "itemsName": "SimpleModel", "name": "items", "text": False, "unwrapped": False},
        original_tsp_name="items",
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithArrayOfModel", "text": False, "unwrapped": False}

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
        xml={"attribute": True, "name": "id1", "text": False, "unwrapped": False},
    )
    """Required."""
    id2: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": True, "name": "id2", "text": False, "unwrapped": False},
    )
    """Required."""
    enabled: bool = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "enabled", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithAttributes", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "rfc3339", "text": False, "unwrapped": False},
    )
    """DateTime value with rfc3339 encoding. Required."""
    rfc7231: datetime.datetime = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        format="rfc7231",
        xml={"attribute": False, "name": "rfc7231", "text": False, "unwrapped": False},
    )
    """DateTime value with rfc7231 encoding. Required."""

    _xml = {"attribute": False, "name": "ModelWithDatetime", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "metadata", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithDictionary", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "itemsName": "SimpleModel", "name": "items", "text": False, "unwrapped": False},
        original_tsp_name="items",
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithEmptyArray", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "SimpleModelData", "text": False, "unwrapped": False},
    )
    """Required."""
    colors: list[str] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "itemsName": "string", "name": "PossibleColors", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithEncodedNamesSrc", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "status", "text": False, "unwrapped": False},
    )
    """Required. Known values are: \"pending\", \"success\", and \"error\"."""

    _xml = {"attribute": False, "name": "ModelWithEnum", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "id", "text": False, "unwrapped": False},
    )
    """Required."""
    title: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "title", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {
        "attribute": False,
        "name": "ModelWithNamespace",
        "namespace": "http://example.com/schema",
        "prefix": "smp",
        "text": False,
        "unwrapped": False,
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
        xml={"attribute": False, "name": "id", "text": False, "unwrapped": False},
    )
    """Required."""
    title: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={
            "attribute": False,
            "name": "title",
            "namespace": "http://example.com/schema",
            "prefix": "smp",
            "text": False,
            "unwrapped": False,
        },
    )
    """Required."""
    author: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={
            "attribute": False,
            "name": "author",
            "namespace": "http://example.com/ns2",
            "prefix": "ns2",
            "text": False,
            "unwrapped": False,
        },
    )
    """Required."""

    _xml = {
        "attribute": False,
        "name": "ModelWithNamespaceOnProperties",
        "namespace": "http://example.com/schema",
        "prefix": "smp",
        "text": False,
        "unwrapped": False,
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
        xml={"attribute": False, "name": "nested", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithNestedModel", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "item", "text": False, "unwrapped": False},
    )
    """Required."""
    value: Optional[int] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "value", "text": False, "unwrapped": False},
    )

    _xml = {"attribute": False, "name": "ModelWithOptionalField", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "itemsName": "Colors", "name": "Colors", "text": False, "unwrapped": True},
    )
    """Required."""
    counts: list[int] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "itemsName": "int32", "name": "Counts", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithRenamedArrays", "text": False, "unwrapped": False}

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
        xml={"attribute": True, "name": "xml-id", "text": False, "unwrapped": False},
    )
    """Required."""
    title: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "title", "text": False, "unwrapped": False},
    )
    """Required."""
    author: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "author", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithRenamedAttribute", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "InputData", "text": False, "unwrapped": False},
    )
    """Required."""
    output_data: "_models.SimpleModel" = rest_field(
        name="outputData",
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "OutputData", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithRenamedFieldsSrc", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "author", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithRenamedNestedModel", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "renamedTitle", "text": False, "unwrapped": False},
    )
    """Required."""
    author: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "author", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithRenamedProperty", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "itemsName": "ModelItem", "name": "ModelItem", "text": False, "unwrapped": True},
        original_tsp_name="items",
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithRenamedUnwrappedModelArray", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "itemsName": "XmlBook", "name": "AllBooks", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithRenamedWrappedAndItemModelArray", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "itemsName": "SimpleModel", "name": "AllItems", "text": False, "unwrapped": False},
        original_tsp_name="items",
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithRenamedWrappedModelArray", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "itemsName": "string", "name": "colors", "text": False, "unwrapped": False},
    )
    """Required."""
    counts: list[int] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "itemsName": "int32", "name": "counts", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithSimpleArrays", "text": False, "unwrapped": False}

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
        xml={"attribute": True, "name": "language", "text": False, "unwrapped": False},
    )
    """Required."""
    content: str = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "content", "text": True, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithText", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "itemsName": "colors", "name": "colors", "text": False, "unwrapped": True},
    )
    """Required."""
    counts: list[int] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "itemsName": "int32", "name": "counts", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithUnwrappedArray", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "itemsName": "items", "name": "items", "text": False, "unwrapped": True},
        original_tsp_name="items",
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithUnwrappedModelArray", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "itemsName": "ItemName", "name": "ItemsTags", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "ModelWithWrappedPrimitiveCustomItemNames", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "name", "text": False, "unwrapped": False},
    )
    """Required."""
    age: int = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "age", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "SimpleModel", "text": False, "unwrapped": False}

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
        xml={"attribute": False, "name": "message", "text": False, "unwrapped": False},
    )
    """Required."""
    code: int = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        xml={"attribute": False, "name": "code", "text": False, "unwrapped": False},
    )
    """Required."""

    _xml = {"attribute": False, "name": "XmlErrorBody", "text": False, "unwrapped": False}

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
