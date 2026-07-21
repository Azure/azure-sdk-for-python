# coding=utf-8
# pylint: disable=useless-super-delegation

import datetime
from typing import Any, Mapping, overload

from ..._utils.model_base import Model as _Model, rest_field


class DefaultDurationProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """DefaultDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Float64MillisecondsDurationProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """Float64MillisecondsDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-milliseconds-float"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Float64SecondsDurationProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """Float64SecondsDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-seconds-float"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class FloatMillisecondsDurationArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """FloatMillisecondsDurationArrayProperty.

    :ivar value: Required.
    :vartype value: list[~datetime.timedelta]
    """

    value: list[datetime.timedelta] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-milliseconds-float"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[datetime.timedelta],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class FloatMillisecondsDurationProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """FloatMillisecondsDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-milliseconds-float"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class FloatMillisecondsLargerUnitDurationProperty(
    _Model
):  # pylint: disable=name-too-long,docstring-keyword-should-match-keyword-only
    """FloatMillisecondsLargerUnitDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-milliseconds-float"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class FloatSecondsDurationArrayProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """FloatSecondsDurationArrayProperty.

    :ivar value: Required.
    :vartype value: list[~datetime.timedelta]
    """

    value: list[datetime.timedelta] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-seconds-float"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: list[datetime.timedelta],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class FloatSecondsDurationProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """FloatSecondsDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-seconds-float"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class FloatSecondsLargerUnitDurationProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """FloatSecondsLargerUnitDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-seconds-float"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Int32MillisecondsDurationProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """Int32MillisecondsDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-milliseconds-int"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Int32MillisecondsLargerUnitDurationProperty(
    _Model
):  # pylint: disable=name-too-long,docstring-keyword-should-match-keyword-only
    """Int32MillisecondsLargerUnitDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-milliseconds-int"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Int32SecondsDurationProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """Int32SecondsDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-seconds-int"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Int32SecondsLargerUnitDurationProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """Int32SecondsLargerUnitDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(
        visibility=["read", "create", "update", "delete", "query"], format="duration-seconds-int"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ISO8601DurationProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """ISO8601DurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: datetime.timedelta = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: datetime.timedelta,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
