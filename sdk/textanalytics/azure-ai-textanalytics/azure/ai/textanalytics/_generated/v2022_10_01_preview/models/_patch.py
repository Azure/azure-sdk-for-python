# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional
from typing_extensions import Literal
from ._models_py3 import (
    AgeResolution as GeneratedAgeResolution,
    AreaResolution as GeneratedAreaResolution,
    CurrencyResolution as GeneratedCurrencyResolution,
    DateTimeResolution as GeneratedDateTimeResolution,
    InformationResolution as GeneratedInformationResolution,
    LengthResolution as GeneratedLengthResolution,
    NumberResolution as GeneratedNumberResolution,
    NumericRangeResolution as GeneratedNumericRangeResolution,
    OrdinalResolution as GeneratedOrdinalResolution,
    SpeedResolution as GeneratedSpeedResolution,
    TemperatureResolution as GeneratedTemperatureResolution,
    TemporalSpanResolution as GeneratedTemporalSpanResolution,
    VolumeResolution as GeneratedVolumeResolution,
    WeightResolution as GeneratedWeightResolution,
)
from ...._dict_mixin import DictMixin


# add dict-like capabilities that all other exposed models have in the TA library
class AgeResolution(GeneratedAgeResolution, DictMixin):
    """Represents the Age entity resolution model.
    """

    resolution_kind: Literal["AgeResolution"] = "AgeResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    value: float
    """The numeric value that the extracted text denotes. Required."""
    unit: str
    """The Age Unit of measurement. Required. Known values are: "Unspecified", "Year",
     "Month", "Week", and "Day". Described in ~azure.ai.textanalytics.AgeUnit."""

    def __init__(
        self,
        *,
        value: float,
        unit: str,
        **kwargs
    ):
        super().__init__(value=value, unit=unit, **kwargs)


class AreaResolution(GeneratedAreaResolution, DictMixin):
    """Represents the area entity resolution model.
    """

    resolution_kind: Literal["AreaResolution"] = "AreaResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    value: float
    """The numeric value that the extracted text denotes. Required."""
    unit: str
    """The area Unit of measurement. Required. Known values are: "Unspecified",
     "SquareKilometer", "SquareHectometer", "SquareDecameter", "SquareDecimeter", "SquareMeter",
     "SquareCentimeter", "SquareMillimeter", "SquareInch", "SquareFoot", "SquareMile", "SquareYard",
     and "Acre". Described in ~azure.ai.textanalytics.AreaUnit."""

    def __init__(
        self,
        *,
        value: float,
        unit: str,
        **kwargs
    ):
        super().__init__(value=value, unit=unit, **kwargs)


class CurrencyResolution(GeneratedCurrencyResolution, DictMixin):
    """Represents the currency entity resolution model.
    """

    resolution_kind: Literal["CurrencyResolution"] = "CurrencyResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    value: float
    """The numeric value that the extracted text denotes. Required."""
    unit: str
    """The unit of the amount captured in the extracted entity. Required."""
    iso4217: Optional[str]
    """The alphabetic code based on another ISO standard, ISO 3166, which lists the
     codes for country names. The first two letters of the ISO 4217 three-letter code are the same
     as the code for the country name, and, where possible, the third letter corresponds to the
     first letter of the currency name."""

    def __init__(
        self,
        *,
        value: float,
        unit: str,
        iso4217: Optional[str] = None,
        **kwargs
    ):
        super().__init__(value=value, unit=unit, iso4217=iso4217, **kwargs)


class DateTimeResolution(GeneratedDateTimeResolution, DictMixin):
    """A resolution for datetime entity instances.
    """

    resolution_kind: Literal["DateTimeResolution"] = "DateTimeResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    timex: str
    """An extended ISO 8601 date/time representation as described in
     (https://github.com/Microsoft/Recognizers-Text/blob/master/Patterns/English/English-DateTime.yaml).
     Required."""
    datetime_subkind: str
    """The DateTime SubKind. Required. Known values are: "Time", "Date",
     "DateTime", "Duration", and "Set". Described in ~azure.ai.textanalytics.DateTimeSubKind."""
    value: str
    """The actual time that the extracted text denote. Required."""
    modifier: Optional[str]
    """An optional modifier of a date/time instance. Known values are: "AfterApprox",
     "Before", "BeforeStart", "Approx", "ReferenceUndefined", "SinceEnd", "AfterMid", "Start",
     "After", "BeforeEnd", "Until", "End", "Less", "Since", "AfterStart", "BeforeApprox", "Mid", and
     "More". Described in ~azure.ai.textanalytics.TemporalModifier."""

    def __init__(
        self,
        *,
        timex: str,
        datetime_subkind: str,
        value: str,
        modifier: Optional[str] = None,
        **kwargs
    ):
        super().__init__(timex=timex, datetime_subkind=datetime_subkind, value=value, modifier=modifier, **kwargs)


class InformationResolution(GeneratedInformationResolution, DictMixin):
    """Represents the information (data) entity resolution model.
    """

    resolution_kind: Literal["InformationResolution"] = "InformationResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    value: float
    """The numeric value that the extracted text denotes. Required."""
    unit: str
    """The information (data) Unit of measurement. Required. Known values are:
     "Unspecified", "Bit", "Kilobit", "Megabit", "Gigabit", "Terabit", "Petabit", "Byte",
     "Kilobyte", "Megabyte", "Gigabyte", "Terabyte", and "Petabyte".
     Described in ~azure.ai.textanalytics.InformationUnit."""

    def __init__(
        self,
        *,
        value: float,
        unit: str,
        **kwargs
    ):
        super().__init__(value=value, unit=unit, **kwargs)


class LengthResolution(GeneratedLengthResolution, DictMixin):
    """Represents the length entity resolution model.
    """

    resolution_kind: Literal["LengthResolution"] = "LengthResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    value: float
    """The numeric value that the extracted text denotes. Required."""
    unit: str
    """The length Unit of measurement. Required. Known values are: "Unspecified",
     "Kilometer", "Hectometer", "Decameter", "Meter", "Decimeter", "Centimeter", "Millimeter",
     "Micrometer", "Nanometer", "Picometer", "Mile", "Yard", "Inch", "Foot", "LightYear", and "Pt".
     Described in ~azure.ai.textanalytics.LengthUnit."""

    def __init__(
        self,
        *,
        value: float,
        unit: str,
        **kwargs
    ):
        super().__init__(value=value, unit=unit, **kwargs)


class NumberResolution(GeneratedNumberResolution, DictMixin):
    """A resolution for numeric entity instances.
    """

    resolution_kind: Literal["NumberResolution"] = "NumberResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    value: float
    """The numeric value that the extracted text denotes. Required."""
    number_kind: str
    """The type of the extracted number entity. Required. Known values are:
     "Integer", "Decimal", "Power", "Fraction", "Percent", and "Unspecified".
     Described in ~azure.ai.textanalytics.NumberKind."""

    def __init__(
        self,
        *,
        number_kind: str,
        value: float,
        **kwargs
    ):
        super().__init__(value=value, number_kind=number_kind, **kwargs)


class NumericRangeResolution(GeneratedNumericRangeResolution, DictMixin):
    """Represents the resolution of numeric intervals.
    """

    resolution_kind: Literal["NumericRangeResolution"] = "NumericRangeResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    range_kind: str
    """The kind of range that the resolution object represents. Required. Known
     values are: "Number", "Speed", "Weight", "Length", "Volume", "Area", "Age", "Information",
     "Temperature", and "Currency". Described in ~azure.ai.textanalytics.RangeKind."""
    minimum: float
    """The beginning value of the interval. Required."""
    maximum: float
    """The ending value of the interval. Required."""

    def __init__(
        self,
        *,
        range_kind: str,
        minimum: float,
        maximum: float,
        **kwargs
    ):
        super().__init__(range_kind=range_kind, minimum=minimum, maximum=maximum, **kwargs)


class OrdinalResolution(GeneratedOrdinalResolution, DictMixin):
    """A resolution for ordinal numbers entity instances.
    """

    resolution_kind: Literal["OrdinalResolution"] = "OrdinalResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    offset: str
    """The offset with respect to the reference (e.g., offset = -1 in "show me the
     second to last". Required."""
    relative_to: str
    """The reference point that the ordinal number denotes. Required. Known values
     are: "Current", "End", and "Start". Described in ~azure.ai.textanalytics.RelativeTo."""
    value: str
    """A simple arithmetic expression that the ordinal denotes. Required."""

    def __init__(
        self,
        *,
        offset: str,
        relative_to: str,
        value: str,
        **kwargs
    ):
        super().__init__(offset=offset, relative_to=relative_to, value=value, **kwargs)


class SpeedResolution(GeneratedSpeedResolution, DictMixin):
    """Represents the speed entity resolution model.
    """

    resolution_kind: Literal["SpeedResolution"] = "SpeedResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    value: float
    """The numeric value that the extracted text denotes. Required."""
    unit: str
    """The speed Unit of measurement. Required. Known values are: "Unspecified",
     "MeterPerSecond", "KilometerPerHour", "KilometerPerMinute", "KilometerPerSecond",
     "MilePerHour", "Knot", "FootPerSecond", "FootPerMinute", "YardPerMinute", "YardPerSecond",
     "MeterPerMillisecond", "CentimeterPerMillisecond", and "KilometerPerMillisecond".
     Described in ~azure.ai.textanalytics.SpeedUnit."""

    def __init__(
        self,
        *,
        value: float,
        unit: str,
        **kwargs
    ):
        super().__init__(value=value, unit=unit, **kwargs)


class TemperatureResolution(GeneratedTemperatureResolution, DictMixin):
    """Represents the temperature entity resolution model.
    """

    resolution_kind: Literal["TemperatureResolution"] = "TemperatureResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    value: float
    """The numeric value that the extracted text denotes. Required."""
    unit: str
    """The temperature Unit of measurement. Required. Known values are: "Unspecified",
     "Fahrenheit", "Kelvin", "Rankine", and "Celsius". Described in ~azure.ai.textanalytics.TemperatureUnit."""

    def __init__(
        self,
        *,
        value: float,
        unit: str,
        **kwargs
    ):
        super().__init__(value=value, unit=unit, **kwargs)


class TemporalSpanResolution(GeneratedTemporalSpanResolution, DictMixin):
    """Represents the resolution of a date and/or time span.
    """

    resolution_kind: Literal["TemporalSpanResolution"] = "TemporalSpanResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    begin: Optional[str]
    """An extended ISO 8601 date/time representation as described in
     (https://github.com/Microsoft/Recognizers-Text/blob/master/Patterns/English/English-DateTime.yaml)."""
    end: Optional[str]
    """An extended ISO 8601 date/time representation as described in
     (https://github.com/Microsoft/Recognizers-Text/blob/master/Patterns/English/English-DateTime.yaml)."""
    duration: Optional[str]
    """An optional duration value formatted based on the ISO 8601
     (https://en.wikipedia.org/wiki/ISO_8601#Durations)."""
    modifier: Optional[str]
    """An optional modifier of a date/time instance. Known values are: "AfterApprox",
     "Before", "BeforeStart", "Approx", "ReferenceUndefined", "SinceEnd", "AfterMid", "Start",
     "After", "BeforeEnd", "Until", "End", "Less", "Since", "AfterStart", "BeforeApprox", "Mid", and
     "More". Described in ~azure.ai.textanalytics.TemporalModifier."""
    timex: Optional[str]
    """An optional triplet containing the beginning, the end, and the duration all stated
     as ISO 8601 formatted strings."""

    def __init__(
        self,
        *,
        begin: Optional[str] = None,
        end: Optional[str] = None,
        duration: Optional[str] = None,
        modifier: Optional[str] = None,
        timex: Optional[str] = None,
        **kwargs
    ):
        super().__init__(begin=begin, end=end, duration=duration, modifier=modifier, timex=timex, **kwargs)


class VolumeResolution(GeneratedVolumeResolution, DictMixin):
    """Represents the volume entity resolution model.
    """

    resolution_kind: Literal["VolumeResolution"] = "VolumeResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    value: float
    """The numeric value that the extracted text denotes. Required."""
    unit: str
    """The Volume Unit of measurement. Required. Known values are: "Unspecified",
     "CubicMeter", "CubicCentimeter", "CubicMillimeter", "Hectoliter", "Decaliter", "Liter",
     "Centiliter", "Milliliter", "CubicYard", "CubicInch", "CubicFoot", "CubicMile", "FluidOunce",
     "Teaspoon", "Tablespoon", "Pint", "Quart", "Cup", "Gill", "Pinch", "FluidDram", "Barrel",
     "Minim", "Cord", "Peck", "Bushel", and "Hogshead". Described in ~azure.ai.textanalytics.VolumeUnit."""

    def __init__(
        self,
        *,
        value: float,
        unit: str,
        **kwargs
    ):
        super().__init__(value=value, unit=unit, **kwargs)


class WeightResolution(GeneratedWeightResolution, DictMixin):
    """Represents the weight entity resolution model.
    """

    resolution_kind: Literal["WeightResolution"] = "WeightResolution"
    """The entity resolution object kind. Required. Known values are:
     "DateTimeResolution" "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind."""
    value: float
    """The numeric value that the extracted text denotes. Required."""
    unit: str
    """The weight Unit of measurement. Required. Known values are: "Unspecified",
     "Kilogram", "Gram", "Milligram", "Gallon", "MetricTon", "Ton", "Pound", "Ounce", "Grain",
     "PennyWeight", "LongTonBritish", "ShortTonUS", "ShortHundredWeightUS", "Stone", and "Dram".
     Described in ~azure.ai.textanalytics.WeightUnit."""

    def __init__(
        self,
        *,
        value: float,
        unit: str,
        **kwargs
    ):
        super().__init__(value=value, unit=unit, **kwargs)


__all__: List[str] = [
    "AgeResolution",
    "AreaResolution",
    "CurrencyResolution",
    "DateTimeResolution",
    "InformationResolution",
    "LengthResolution",
    "NumberResolution",
    "NumericRangeResolution",
    "OrdinalResolution",
    "SpeedResolution",
    "TemperatureResolution",
    "TemporalSpanResolution",
    "VolumeResolution",
    "WeightResolution",
]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
