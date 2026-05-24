# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Literal, Mapping, TYPE_CHECKING, Union, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import models as _models


class Cat(_Model):
    """Cat.

    :ivar name: Required.
    :vartype name: str
    """

    name: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

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


class Dog(_Model):
    """Dog.

    :ivar bark: Required.
    :vartype bark: str
    """

    bark: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        bark: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class EnumsOnlyCases(_Model):
    """EnumsOnlyCases.

    :ivar lr: This should be receive/send the left variant. Required. Is one of the following
     types: Literal["left"], Literal["right"], Literal["up"], Literal["down"]
    :vartype lr: str or str or str or str
    :ivar ud: This should be receive/send the up variant. Required. Is either a Literal["up"] type
     or a Literal["down"] type.
    :vartype ud: str or str
    """

    lr: Literal["left", "right", "up", "down"] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """This should be receive/send the left variant. Required. Is one of the following types:
     Literal[\"left\"], Literal[\"right\"], Literal[\"up\"], Literal[\"down\"]"""
    ud: Literal["up", "down"] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """This should be receive/send the up variant. Required. Is either a Literal[\"up\"] type or a
     Literal[\"down\"] type."""

    @overload
    def __init__(
        self,
        *,
        lr: Literal["left", "right", "up", "down"],
        ud: Literal["up", "down"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class GetResponse(_Model):
    """GetResponse.

    :ivar prop: Required. Is one of the following types: Literal["a"], Literal["b"], Literal["c"]
    :vartype prop: str or str or str
    """

    prop: Literal["a", "b", "c"] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required. Is one of the following types: Literal[\"a\"], Literal[\"b\"], Literal[\"c\"]"""

    @overload
    def __init__(
        self,
        *,
        prop: Literal["a", "b", "c"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class GetResponse1(_Model):
    """GetResponse1.

    :ivar prop: Required. Is one of the following types: Literal["b"], Literal["c"], str
    :vartype prop: str or str or str
    """

    prop: Union[Literal["b"], Literal["c"], str] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    """Required. Is one of the following types: Literal[\"b\"], Literal[\"c\"], str"""

    @overload
    def __init__(
        self,
        *,
        prop: Union[Literal["b"], Literal["c"], str],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class GetResponse2(_Model):
    """GetResponse2.

    :ivar prop: Required. Known values are: "b" and "c".
    :vartype prop: str or ~typetest.union.models.StringExtensibleNamedUnion
    """

    prop: Union[str, "_models.StringExtensibleNamedUnion"] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    """Required. Known values are: \"b\" and \"c\"."""

    @overload
    def __init__(
        self,
        *,
        prop: Union[str, "_models.StringExtensibleNamedUnion"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class GetResponse3(_Model):
    """GetResponse3.

    :ivar prop: Required. Is one of the following types: Literal[1], Literal[2], Literal[3]
    :vartype prop: int or int or int
    """

    prop: Literal[1, 2, 3] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required. Is one of the following types: Literal[1], Literal[2], Literal[3]"""

    @overload
    def __init__(
        self,
        *,
        prop: Literal[1, 2, 3],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class GetResponse4(_Model):
    """GetResponse4.

    :ivar prop: Required. Is one of the following types: float
    :vartype prop: float or float or float
    """

    prop: float = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required. Is one of the following types: float"""

    @overload
    def __init__(
        self,
        *,
        prop: float,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class GetResponse5(_Model):
    """GetResponse5.

    :ivar prop: Required. Is either a Cat type or a Dog type.
    :vartype prop: ~typetest.union.models.Cat or ~typetest.union.models.Dog
    """

    prop: Union["_models.Cat", "_models.Dog"] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required. Is either a Cat type or a Dog type."""

    @overload
    def __init__(
        self,
        *,
        prop: Union["_models.Cat", "_models.Dog"],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class GetResponse6(_Model):
    """GetResponse6.

    :ivar prop: Required.
    :vartype prop: ~typetest.union.models.EnumsOnlyCases
    """

    prop: "_models.EnumsOnlyCases" = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        prop: "_models.EnumsOnlyCases",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class GetResponse7(_Model):
    """GetResponse7.

    :ivar prop: Required.
    :vartype prop: ~typetest.union.models.StringAndArrayCases
    """

    prop: "_models.StringAndArrayCases" = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        prop: "_models.StringAndArrayCases",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class GetResponse8(_Model):
    """GetResponse8.

    :ivar prop: Required.
    :vartype prop: ~typetest.union.models.MixedLiteralsCases
    """

    prop: "_models.MixedLiteralsCases" = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        prop: "_models.MixedLiteralsCases",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class GetResponse9(_Model):
    """GetResponse9.

    :ivar prop: Required.
    :vartype prop: ~typetest.union.models.MixedTypesCases
    """

    prop: "_models.MixedTypesCases" = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        prop: "_models.MixedTypesCases",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class MixedLiteralsCases(_Model):
    """MixedLiteralsCases.

    :ivar string_literal: This should be receive/send the "a" variant. Required. Is one of the
     following types: Literal["a"], Literal[2], float, Literal[True]
    :vartype string_literal: str or int or float or bool
    :ivar int_literal: This should be receive/send the 2 variant. Required. Is one of the following
     types: Literal["a"], Literal[2], float, Literal[True]
    :vartype int_literal: str or int or float or bool
    :ivar float_literal: This should be receive/send the 3.3 variant. Required. Is one of the
     following types: Literal["a"], Literal[2], float, Literal[True]
    :vartype float_literal: str or int or float or bool
    :ivar boolean_literal: This should be receive/send the true variant. Required. Is one of the
     following types: Literal["a"], Literal[2], float, Literal[True]
    :vartype boolean_literal: str or int or float or bool
    """

    string_literal: Literal["a", 2, True] = rest_field(
        name="stringLiteral", visibility=["read", "create", "update", "delete", "query"]
    )
    """This should be receive/send the \"a\" variant. Required. Is one of the following types:
     Literal[\"a\"], Literal[2], float, Literal[True]"""
    int_literal: Literal["a", 2, True] = rest_field(
        name="intLiteral", visibility=["read", "create", "update", "delete", "query"]
    )
    """This should be receive/send the 2 variant. Required. Is one of the following types:
     Literal[\"a\"], Literal[2], float, Literal[True]"""
    float_literal: Literal["a", 2, True] = rest_field(
        name="floatLiteral", visibility=["read", "create", "update", "delete", "query"]
    )
    """This should be receive/send the 3.3 variant. Required. Is one of the following types:
     Literal[\"a\"], Literal[2], float, Literal[True]"""
    boolean_literal: Literal["a", 2, True] = rest_field(
        name="booleanLiteral", visibility=["read", "create", "update", "delete", "query"]
    )
    """This should be receive/send the true variant. Required. Is one of the following types:
     Literal[\"a\"], Literal[2], float, Literal[True]"""

    @overload
    def __init__(
        self,
        *,
        string_literal: Literal["a", 2, True],
        int_literal: Literal["a", 2, True],
        float_literal: Literal["a", 2, True],
        boolean_literal: Literal["a", 2, True],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class MixedTypesCases(_Model):
    """MixedTypesCases.

    :ivar model: This should be receive/send the Cat variant. Required. Is one of the following
     types: Cat, Literal["a"], int, bool
    :vartype model: ~typetest.union.models.Cat or str or int or bool
    :ivar literal: This should be receive/send the "a" variant. Required. Is one of the following
     types: Cat, Literal["a"], int, bool
    :vartype literal: ~typetest.union.models.Cat or str or int or bool
    :ivar int_property: This should be receive/send the int variant. Required. Is one of the
     following types: Cat, Literal["a"], int, bool
    :vartype int_property: ~typetest.union.models.Cat or str or int or bool
    :ivar boolean: This should be receive/send the boolean variant. Required. Is one of the
     following types: Cat, Literal["a"], int, bool
    :vartype boolean: ~typetest.union.models.Cat or str or int or bool
    :ivar array: This should be receive/send 4 element with Cat, "a", int, and boolean. Required.
    :vartype array: list[~typetest.union.models.Cat or str or int or bool]
    """

    model: Union["_models.Cat", Literal["a"], int, bool] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    """This should be receive/send the Cat variant. Required. Is one of the following types: Cat,
     Literal[\"a\"], int, bool"""
    literal: Union["_models.Cat", Literal["a"], int, bool] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    """This should be receive/send the \"a\" variant. Required. Is one of the following types: Cat,
     Literal[\"a\"], int, bool"""
    int_property: Union["_models.Cat", Literal["a"], int, bool] = rest_field(
        name="int", visibility=["read", "create", "update", "delete", "query"]
    )
    """This should be receive/send the int variant. Required. Is one of the following types: Cat,
     Literal[\"a\"], int, bool"""
    boolean: Union["_models.Cat", Literal["a"], int, bool] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    """This should be receive/send the boolean variant. Required. Is one of the following types: Cat,
     Literal[\"a\"], int, bool"""
    array: list[Union["_models.Cat", Literal["a"], int, bool]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    """This should be receive/send 4 element with Cat, \"a\", int, and boolean. Required."""

    @overload
    def __init__(
        self,
        *,
        model: Union["_models.Cat", Literal["a"], int, bool],
        literal: Union["_models.Cat", Literal["a"], int, bool],
        int_property: Union["_models.Cat", Literal["a"], int, bool],
        boolean: Union["_models.Cat", Literal["a"], int, bool],
        array: list[Union["_models.Cat", Literal["a"], int, bool]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class StringAndArrayCases(_Model):
    """StringAndArrayCases.

    :ivar string: This should be receive/send the string variant. Required. Is either a str type or
     a [str] type.
    :vartype string: str or list[str]
    :ivar array: This should be receive/send the array variant. Required. Is either a str type or a
     [str] type.
    :vartype array: str or list[str]
    """

    string: Union[str, list[str]] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """This should be receive/send the string variant. Required. Is either a str type or a [str] type."""
    array: Union[str, list[str]] = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """This should be receive/send the array variant. Required. Is either a str type or a [str] type."""

    @overload
    def __init__(
        self,
        *,
        string: Union[str, list[str]],
        array: Union[str, list[str]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
