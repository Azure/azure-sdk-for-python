# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, TYPE_CHECKING, Union, overload

from .._utils.model_base import Model as _Model, rest_field

if TYPE_CHECKING:
    from .. import models as _models


class CommaDelimitedArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """CommaDelimitedArrayProperty.

    :ivar value: Required.
    :vartype value: list[str]
    """

    value: list[str] = rest_field(visibility=["read", "create", "update", "delete", "query"], format="commaDelimited")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[str],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CommaDelimitedEnumArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """CommaDelimitedEnumArrayProperty.

    :ivar value: Required.
    :vartype value: list[str or ~encode.array.models.Colors]
    """

    value: list[Union[str, "_models.Colors"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="commaDelimited"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[Union[str, "_models.Colors"]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class CommaDelimitedExtensibleEnumArrayProperty(
    _Model
):  # pylint: disable=name-too-long,docstring-keyword-should-match-keyword-only
    """CommaDelimitedExtensibleEnumArrayProperty.

    :ivar value: Required.
    :vartype value: list[str or ~encode.array.models.ColorsExtensibleEnum]
    """

    value: list[Union[str, "_models.ColorsExtensibleEnum"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="commaDelimited"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[Union[str, "_models.ColorsExtensibleEnum"]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class NewlineDelimitedArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """NewlineDelimitedArrayProperty.

    :ivar value: Required.
    :vartype value: list[str]
    """

    value: list[str] = rest_field(visibility=["read", "create", "update", "delete", "query"], format="newlineDelimited")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[str],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class NewlineDelimitedEnumArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """NewlineDelimitedEnumArrayProperty.

    :ivar value: Required.
    :vartype value: list[str or ~encode.array.models.Colors]
    """

    value: list[Union[str, "_models.Colors"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="newlineDelimited"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[Union[str, "_models.Colors"]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class NewlineDelimitedExtensibleEnumArrayProperty(
    _Model
):  # pylint: disable=name-too-long,docstring-keyword-should-match-keyword-only
    """NewlineDelimitedExtensibleEnumArrayProperty.

    :ivar value: Required.
    :vartype value: list[str or ~encode.array.models.ColorsExtensibleEnum]
    """

    value: list[Union[str, "_models.ColorsExtensibleEnum"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="newlineDelimited"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[Union[str, "_models.ColorsExtensibleEnum"]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class PipeDelimitedArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """PipeDelimitedArrayProperty.

    :ivar value: Required.
    :vartype value: list[str]
    """

    value: list[str] = rest_field(visibility=["read", "create", "update", "delete", "query"], format="pipeDelimited")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[str],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class PipeDelimitedEnumArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """PipeDelimitedEnumArrayProperty.

    :ivar value: Required.
    :vartype value: list[str or ~encode.array.models.Colors]
    """

    value: list[Union[str, "_models.Colors"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="pipeDelimited"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[Union[str, "_models.Colors"]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class PipeDelimitedExtensibleEnumArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """PipeDelimitedExtensibleEnumArrayProperty.

    :ivar value: Required.
    :vartype value: list[str or ~encode.array.models.ColorsExtensibleEnum]
    """

    value: list[Union[str, "_models.ColorsExtensibleEnum"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="pipeDelimited"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[Union[str, "_models.ColorsExtensibleEnum"]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SpaceDelimitedArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """SpaceDelimitedArrayProperty.

    :ivar value: Required.
    :vartype value: list[str]
    """

    value: list[str] = rest_field(visibility=["read", "create", "update", "delete", "query"], format="spaceDelimited")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[str],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SpaceDelimitedEnumArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """SpaceDelimitedEnumArrayProperty.

    :ivar value: Required.
    :vartype value: list[str or ~encode.array.models.Colors]
    """

    value: list[Union[str, "_models.Colors"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="spaceDelimited"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[Union[str, "_models.Colors"]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SpaceDelimitedExtensibleEnumArrayProperty(
    _Model
):  # pylint: disable=name-too-long,docstring-keyword-should-match-keyword-only
    """SpaceDelimitedExtensibleEnumArrayProperty.

    :ivar value: Required.
    :vartype value: list[str or ~encode.array.models.ColorsExtensibleEnum]
    """

    value: list[Union[str, "_models.ColorsExtensibleEnum"]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="spaceDelimited"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[Union[str, "_models.ColorsExtensibleEnum"]],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
