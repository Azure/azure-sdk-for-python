# coding=utf-8

import datetime
from typing import Optional, TYPE_CHECKING, Union
from typing_extensions import Required, TypedDict

if TYPE_CHECKING:
    from .models import Status


class Author(TypedDict, total=False):
    """Author model with a custom XML name.

    :ivar name: Required.
    :vartype name: str
    """

    name: Required[str]
    """Required."""


class Book(TypedDict, total=False):
    """Book model with a custom XML name.

    :ivar title: Required.
    :vartype title: str
    """

    title: Required[str]
    """Required."""


class ModelWithArrayOfModel(TypedDict, total=False):
    """§4.1 — Contains an array of models.

    :ivar items_property: Required.
    :vartype items_property: ~payload.xml.models.SimpleModel
    """

    items: Required[list["SimpleModel"]]
    """Required."""


class ModelWithAttributes(TypedDict, total=False):
    """§5.1 — Contains fields that are XML attributes.

    :ivar id1: Required.
    :vartype id1: int
    :ivar id2: Required.
    :vartype id2: str
    :ivar enabled: Required.
    :vartype enabled: bool
    """

    id1: Required[int]
    """Required."""
    id2: Required[str]
    """Required."""
    enabled: Required[bool]
    """Required."""


class ModelWithDatetime(TypedDict, total=False):
    """Contains datetime properties with different encodings.

    :ivar rfc3339: DateTime value with rfc3339 encoding. Required.
    :vartype rfc3339: ~datetime.datetime
    :ivar rfc7231: DateTime value with rfc7231 encoding. Required.
    :vartype rfc7231: ~datetime.datetime
    """

    rfc3339: Required[datetime.datetime]
    """DateTime value with rfc3339 encoding. Required."""
    rfc7231: Required[datetime.datetime]
    """DateTime value with rfc7231 encoding. Required."""


class ModelWithDictionary(TypedDict, total=False):
    """Contains a dictionary of key value pairs.

    :ivar metadata: Required.
    :vartype metadata: dict[str, str]
    """

    metadata: Required[dict[str, str]]
    """Required."""


class ModelWithEmptyArray(TypedDict, total=False):
    """Contains an array of models that's supposed to be sent/received as an empty XML element.

    :ivar items_property: Required.
    :vartype items_property: ~payload.xml.models.SimpleModel
    """

    items: Required[list["SimpleModel"]]
    """Required."""


class ModelWithEncodedNames(TypedDict, total=False):
    """Uses encodedName instead of Xml.Name which is functionally equivalent.

    :ivar model_data: Required.
    :vartype model_data: ~payload.xml.models.SimpleModel
    :ivar colors: Required.
    :vartype colors: list[str]
    """

    modelData: Required["SimpleModel"]
    """Required."""
    colors: Required[list[str]]
    """Required."""


class ModelWithEnum(TypedDict, total=False):
    """Contains a single property with an enum value.

    :ivar status: Required. Known values are: "pending", "success", and "error".
    :vartype status: str or ~payload.xml.models.Status
    """

    status: Required[Union[str, "Status"]]
    """Required. Known values are: \"pending\", \"success\", and \"error\"."""


class ModelWithNamespace(TypedDict, total=False):
    """§6.1, §7.1 — Contains fields with XML namespace on the model.

    :ivar id: Required.
    :vartype id: int
    :ivar title: Required.
    :vartype title: str
    """

    id: Required[int]
    """Required."""
    title: Required[str]
    """Required."""


class ModelWithNamespaceOnProperties(TypedDict, total=False):
    """§6.2, §7.2 — Contains fields with different XML namespaces on individual properties.

    :ivar id: Required.
    :vartype id: int
    :ivar title: Required.
    :vartype title: str
    :ivar author: Required.
    :vartype author: str
    """

    id: Required[int]
    """Required."""
    title: Required[str]
    """Required."""
    author: Required[str]
    """Required."""


class ModelWithNestedModel(TypedDict, total=False):
    """§2.1 — Contains a property that references another model.

    :ivar nested: Required.
    :vartype nested: ~payload.xml.models.SimpleModel
    """

    nested: Required["SimpleModel"]
    """Required."""


class ModelWithOptionalField(TypedDict, total=False):
    """Contains an optional field.

    :ivar item: Required.
    :vartype item: str
    :ivar value:
    :vartype value: int
    """

    item: Required[str]
    """Required."""
    value: Optional[int]


class ModelWithRenamedArrays(TypedDict, total=False):
    """§3.3, §3.4 — Contains fields of wrapped and unwrapped arrays of primitive types that have
    different XML representations.

    :ivar colors: Required.
    :vartype colors: list[str]
    :ivar counts: Required.
    :vartype counts: list[int]
    """

    colors: Required[list[str]]
    """Required."""
    counts: Required[list[int]]
    """Required."""


class ModelWithRenamedAttribute(TypedDict, total=False):
    """§5.2 — Contains a renamed XML attribute.

    :ivar id: Required.
    :vartype id: int
    :ivar title: Required.
    :vartype title: str
    :ivar author: Required.
    :vartype author: str
    """

    id: Required[int]
    """Required."""
    title: Required[str]
    """Required."""
    author: Required[str]
    """Required."""


class ModelWithRenamedFields(TypedDict, total=False):
    """§1.3, §2.3 — Contains fields of the same type that have different XML representation.

    :ivar input_data: Required.
    :vartype input_data: ~payload.xml.models.SimpleModel
    :ivar output_data: Required.
    :vartype output_data: ~payload.xml.models.SimpleModel
    """

    inputData: Required["SimpleModel"]
    """Required."""
    outputData: Required["SimpleModel"]
    """Required."""


class ModelWithRenamedNestedModel(TypedDict, total=False):
    """§2.2 — Contains a property whose type has.

    :ivar author: Required.
    :vartype author: ~payload.xml.models.Author
    """

    author: Required["Author"]
    """Required."""


class ModelWithRenamedProperty(TypedDict, total=False):
    """§1.2 — Contains a scalar property with a custom XML name.

    :ivar title: Required.
    :vartype title: str
    :ivar author: Required.
    :vartype author: str
    """

    title: Required[str]
    """Required."""
    author: Required[str]
    """Required."""


class ModelWithRenamedUnwrappedModelArray(TypedDict, total=False):
    """§4.4 — Contains an unwrapped array of models with a custom item name.

    :ivar items_property: Required.
    :vartype items_property: ~payload.xml.models.SimpleModel
    """

    items: Required[list["SimpleModel"]]
    """Required."""


class ModelWithRenamedWrappedAndItemModelArray(TypedDict, total=False):
    """§4.5 — Contains a wrapped array of models with custom wrapper and item names.

    :ivar books: Required.
    :vartype books: ~payload.xml.models.Book
    """

    books: Required[list["Book"]]
    """Required."""


class ModelWithRenamedWrappedModelArray(TypedDict, total=False):
    """§4.3 — Contains a wrapped array of models with a custom wrapper name.

    :ivar items_property: Required.
    :vartype items_property: ~payload.xml.models.SimpleModel
    """

    items: Required[list["SimpleModel"]]
    """Required."""


class ModelWithSimpleArrays(TypedDict, total=False):
    """§3.1 — Contains fields of arrays of primitive types.

    :ivar colors: Required.
    :vartype colors: list[str]
    :ivar counts: Required.
    :vartype counts: list[int]
    """

    colors: Required[list[str]]
    """Required."""
    counts: Required[list[int]]
    """Required."""


class ModelWithText(TypedDict, total=False):
    """§8.1 — Contains an attribute and text.

    :ivar language: Required.
    :vartype language: str
    :ivar content: Required.
    :vartype content: str
    """

    language: Required[str]
    """Required."""
    content: Required[str]
    """Required."""


class ModelWithUnwrappedArray(TypedDict, total=False):
    """§3.2 — Contains fields of wrapped and unwrapped arrays of primitive types.

    :ivar colors: Required.
    :vartype colors: list[str]
    :ivar counts: Required.
    :vartype counts: list[int]
    """

    colors: Required[list[str]]
    """Required."""
    counts: Required[list[int]]
    """Required."""


class ModelWithUnwrappedModelArray(TypedDict, total=False):
    """§4.2 — Contains an unwrapped array of models.

    :ivar items_property: Required.
    :vartype items_property: ~payload.xml.models.SimpleModel
    """

    items: Required[list["SimpleModel"]]
    """Required."""


class ModelWithWrappedPrimitiveCustomItemNames(TypedDict, total=False):
    """§3.5 — Contains a wrapped primitive array with custom wrapper and item names.

    :ivar tags: Required.
    :vartype tags: list[str]
    """

    tags: Required[list[str]]
    """Required."""


class SimpleModel(TypedDict, total=False):
    """§1.1 — Contains fields of primitive types.

    :ivar name: Required.
    :vartype name: str
    :ivar age: Required.
    :vartype age: int
    """

    name: Required[str]
    """Required."""
    age: Required[int]
    """Required."""


class XmlErrorBody(TypedDict, total=False):
    """The body of an XML error response.

    :ivar message: Required.
    :vartype message: str
    :ivar code: Required.
    :vartype code: int
    """

    message: Required[str]
    """Required."""
    code: Required[int]
    """Required."""
