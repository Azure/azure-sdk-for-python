# coding=utf-8

import datetime
from typing_extensions import Required, TypedDict


class DefaultDurationProperty(TypedDict, total=False):
    """DefaultDurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: Required[datetime.timedelta]
    """Required."""


class Float64MillisecondsDurationProperty(TypedDict, total=False):
    """Float64MillisecondsDurationProperty.

    :ivar value: Required.
    :vartype value: float
    """

    value: Required[float]
    """Required."""


class Float64SecondsDurationProperty(TypedDict, total=False):
    """Float64SecondsDurationProperty.

    :ivar value: Required.
    :vartype value: float
    """

    value: Required[float]
    """Required."""


class FloatMillisecondsDurationArrayProperty(TypedDict, total=False):
    """FloatMillisecondsDurationArrayProperty.

    :ivar value: Required.
    :vartype value: list[float]
    """

    value: Required[list[float]]
    """Required."""


class FloatMillisecondsDurationProperty(TypedDict, total=False):
    """FloatMillisecondsDurationProperty.

    :ivar value: Required.
    :vartype value: float
    """

    value: Required[float]
    """Required."""


class FloatMillisecondsLargerUnitDurationProperty(TypedDict, total=False):  # pylint: disable=name-too-long
    """FloatMillisecondsLargerUnitDurationProperty.

    :ivar value: Required.
    :vartype value: float
    """

    value: Required[float]
    """Required."""


class FloatSecondsDurationArrayProperty(TypedDict, total=False):
    """FloatSecondsDurationArrayProperty.

    :ivar value: Required.
    :vartype value: list[float]
    """

    value: Required[list[float]]
    """Required."""


class FloatSecondsDurationProperty(TypedDict, total=False):
    """FloatSecondsDurationProperty.

    :ivar value: Required.
    :vartype value: float
    """

    value: Required[float]
    """Required."""


class FloatSecondsLargerUnitDurationProperty(TypedDict, total=False):
    """FloatSecondsLargerUnitDurationProperty.

    :ivar value: Required.
    :vartype value: float
    """

    value: Required[float]
    """Required."""


class Int32MillisecondsDurationProperty(TypedDict, total=False):
    """Int32MillisecondsDurationProperty.

    :ivar value: Required.
    :vartype value: int
    """

    value: Required[int]
    """Required."""


class Int32MillisecondsLargerUnitDurationProperty(TypedDict, total=False):  # pylint: disable=name-too-long
    """Int32MillisecondsLargerUnitDurationProperty.

    :ivar value: Required.
    :vartype value: int
    """

    value: Required[int]
    """Required."""


class Int32SecondsDurationProperty(TypedDict, total=False):
    """Int32SecondsDurationProperty.

    :ivar value: Required.
    :vartype value: int
    """

    value: Required[int]
    """Required."""


class Int32SecondsLargerUnitDurationProperty(TypedDict, total=False):
    """Int32SecondsLargerUnitDurationProperty.

    :ivar value: Required.
    :vartype value: int
    """

    value: Required[int]
    """Required."""


class ISO8601DurationProperty(TypedDict, total=False):
    """ISO8601DurationProperty.

    :ivar value: Required.
    :vartype value: ~datetime.timedelta
    """

    value: Required[datetime.timedelta]
    """Required."""
