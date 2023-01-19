# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._models_py3 import (
    AgeResolution as GeneratedAgeResolution,
    AreaResolution as GeneratedAreaResolution,
    BooleanResolution as GeneratedBooleanResolution,
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

    :ivar value: The numeric value that the extracted text denotes. Required.
    :vartype value: float
    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar unit: The Age Unit of measurement. Required. Known values are: "Unspecified", "Year",
     "Month", "Week", and "Day". Described in ~azure.ai.textanalytics.AgeUnit.
    :vartype unit: str
    """


class AreaResolution(GeneratedAreaResolution, DictMixin):
    """Represents the area entity resolution model.

    :ivar value: The numeric value that the extracted text denotes. Required.
    :vartype value: float
    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar unit: The area Unit of measurement. Required. Known values are: "Unspecified",
     "SquareKilometer", "SquareHectometer", "SquareDecameter", "SquareDecimeter", "SquareMeter",
     "SquareCentimeter", "SquareMillimeter", "SquareInch", "SquareFoot", "SquareMile", "SquareYard",
     and "Acre". Described in ~azure.ai.textanalytics.AreaUnit.
    :vartype unit: str
    """


class BooleanResolution(GeneratedBooleanResolution, DictMixin):
    """A resolution for boolean expressions.

    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar value: Required.
    :vartype value: bool
    """


class CurrencyResolution(GeneratedCurrencyResolution, DictMixin):
    """Represents the currency entity resolution model.

    :ivar value: The numeric value that the extracted text denotes. Required.
    :vartype value: float
    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar iso4217: The alphabetic code based on another ISO standard, ISO 3166, which lists the
     codes for country names. The first two letters of the ISO 4217 three-letter code are the same
     as the code for the country name, and, where possible, the third letter corresponds to the
     first letter of the currency name.
    :vartype iso4217: str
    :ivar unit: The unit of the amount captured in the extracted entity. Required.
    :vartype unit: str
    """


class DateTimeResolution(GeneratedDateTimeResolution, DictMixin):
    """A resolution for datetime entity instances.

    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar timex: An extended ISO 8601 date/time representation as described in
     (https://github.com/Microsoft/Recognizers-Text/blob/master/Patterns/English/English-DateTime.yaml).
     Required.
    :vartype timex: str
    :ivar date_time_sub_kind: The DateTime SubKind. Required. Known values are: "Time", "Date",
     "DateTime", "Duration", and "Set". Described in ~azure.ai.textanalytics.DateTimeSubKind.
    :vartype date_time_sub_kind: str
    :ivar value: The actual time that the extracted text denote. Required.
    :vartype value: str
    :ivar modifier: An optional modifier of a date/time instance. Known values are: "AfterApprox",
     "Before", "BeforeStart", "Approx", "ReferenceUndefined", "SinceEnd", "AfterMid", "Start",
     "After", "BeforeEnd", "Until", "End", "Less", "Since", "AfterStart", "BeforeApprox", "Mid", and
     "More". Described in ~azure.ai.textanalytics.TemporalModifier.
    :vartype modifier: str
    """


class InformationResolution(GeneratedInformationResolution, DictMixin):
    """Represents the information (data) entity resolution model.

    :ivar value: The numeric value that the extracted text denotes. Required.
    :vartype value: float
    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar unit: The information (data) Unit of measurement. Required. Known values are:
     "Unspecified", "Bit", "Kilobit", "Megabit", "Gigabit", "Terabit", "Petabit", "Byte",
     "Kilobyte", "Megabyte", "Gigabyte", "Terabyte", and "Petabyte".
     Described in ~azure.ai.textanalytics.InformationUnit.
    :vartype unit: str
    """


class LengthResolution(GeneratedLengthResolution, DictMixin):
    """Represents the length entity resolution model.

    :ivar value: The numeric value that the extracted text denotes. Required.
    :vartype value: float
    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar unit: The length Unit of measurement. Required. Known values are: "Unspecified",
     "Kilometer", "Hectometer", "Decameter", "Meter", "Decimeter", "Centimeter", "Millimeter",
     "Micrometer", "Nanometer", "Picometer", "Mile", "Yard", "Inch", "Foot", "LightYear", and "Pt".
     Described in ~azure.ai.textanalytics.LengthUnit.
    :vartype unit: str
    """


class NumberResolution(GeneratedNumberResolution, DictMixin):
    """A resolution for numeric entity instances.

    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar number_kind: The type of the extracted number entity. Required. Known values are:
     "Integer", "Decimal", "Power", "Fraction", "Percent", and "Unspecified".
     Described in ~azure.ai.textanalytics.NumberKind.
    :vartype number_kind: str
    :ivar value: A numeric representation of what the extracted text denotes. Required.
    :vartype value: float
    """


class NumericRangeResolution(GeneratedNumericRangeResolution, DictMixin):
    """represents the resolution of numeric intervals.

    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar range_kind: The kind of range that the resolution object represents. Required. Known
     values are: "Number", "Speed", "Weight", "Length", "Volume", "Area", "Age", "Information",
     "Temperature", and "Currency". Described in ~azure.ai.textanalytics.RangeKind.
    :vartype range_kind: str
    :ivar minimum: The beginning value of  the interval. Required.
    :vartype minimum: float
    :ivar maximum: The ending value of the interval. Required.
    :vartype maximum: float
    """


class OrdinalResolution(GeneratedOrdinalResolution, DictMixin):
    """A resolution for ordinal numbers entity instances.

    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar offset: The offset With respect to the reference (e.g., offset = -1 in "show me the
     second to last". Required.
    :vartype offset: str
    :ivar relative_to: The reference point that the ordinal number denotes. Required. Known values
     are: "Current", "End", and "Start". Described in ~azure.ai.textanalytics.RelativeTo.
    :vartype relative_to: str
    :ivar value: A simple arithmetic expression that the ordinal denotes. Required.
    :vartype value: str
    """


class SpeedResolution(GeneratedSpeedResolution, DictMixin):
    """Represents the speed entity resolution model.

    :ivar value: The numeric value that the extracted text denotes. Required.
    :vartype value: float
    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in  ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar unit: The speed Unit of measurement. Required. Known values are: "Unspecified",
     "MeterPerSecond", "KilometerPerHour", "KilometerPerMinute", "KilometerPerSecond",
     "MilePerHour", "Knot", "FootPerSecond", "FootPerMinute", "YardPerMinute", "YardPerSecond",
     "MeterPerMillisecond", "CentimeterPerMillisecond", and "KilometerPerMillisecond".
     Described in ~azure.ai.textanalytics.SpeedUnit.
    :vartype unit: str
    """


class TemperatureResolution(GeneratedTemperatureResolution, DictMixin):
    """Represents the temperature entity resolution model.

    :ivar value: The numeric value that the extracted text denotes. Required.
    :vartype value: float
    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar unit: The temperature Unit of measurement. Required. Known values are: "Unspecified",
     "Fahrenheit", "Kelvin", "Rankine", and "Celsius". Described in ~azure.ai.textanalytics.TemperatureUnit.
    :vartype unit: str
    """


class TemporalSpanResolution(GeneratedTemporalSpanResolution, DictMixin):
    """represents the resolution of a date and/or time span.

    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar begin: An extended ISO 8601 date/time representation as described in
     (https://github.com/Microsoft/Recognizers-Text/blob/master/Patterns/English/English-DateTime.yaml).
    :vartype begin: str
    :ivar end: An extended ISO 8601 date/time representation as described in
     (https://github.com/Microsoft/Recognizers-Text/blob/master/Patterns/English/English-DateTime.yaml).
    :vartype end: str
    :ivar duration: An optional duration value formatted based on the ISO 8601
     (https://en.wikipedia.org/wiki/ISO_8601#Durations).
    :vartype duration: str
    :ivar modifier: An optional modifier of a date/time instance. Known values are: "AfterApprox",
     "Before", "BeforeStart", "Approx", "ReferenceUndefined", "SinceEnd", "AfterMid", "Start",
     "After", "BeforeEnd", "Until", "End", "Less", "Since", "AfterStart", "BeforeApprox", "Mid", and
     "More". Described in ~azure.ai.textanalytics.TemporalModifier.
    :vartype modifier: str
    :ivar timex: An optional triplet containing the beginning, the end, and the duration all stated
     as ISO 8601 formatted strings.
    :vartype timex: str
    """


class VolumeResolution(GeneratedVolumeResolution, DictMixin):
    """Represents the volume entity resolution model.

    :ivar value: The numeric value that the extracted text denotes. Required.
    :vartype value: float
    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar unit: The Volume Unit of measurement. Required. Known values are: "Unspecified",
     "CubicMeter", "CubicCentimeter", "CubicMillimeter", "Hectoliter", "Decaliter", "Liter",
     "Centiliter", "Milliliter", "CubicYard", "CubicInch", "CubicFoot", "CubicMile", "FluidOunce",
     "Teaspoon", "Tablespoon", "Pint", "Quart", "Cup", "Gill", "Pinch", "FluidDram", "Barrel",
     "Minim", "Cord", "Peck", "Bushel", and "Hogshead". Described in ~azure.ai.textanalytics.VolumeUnit.
    :vartype unit: str
    """


class WeightResolution(GeneratedWeightResolution, DictMixin):
    """Represents the weight entity resolution model.

    :ivar value: The numeric value that the extracted text denotes. Required.
    :vartype value: float
    :ivar resolution_kind: The entity resolution object kind. Required. Known values are:
     "BooleanResolution", "DateTimeResolution", "NumberResolution", "OrdinalResolution",
     "SpeedResolution", "WeightResolution", "LengthResolution", "VolumeResolution",
     "AreaResolution", "AgeResolution", "InformationResolution", "TemperatureResolution",
     "CurrencyResolution", "NumericRangeResolution", and "TemporalSpanResolution".
     Described in ~azure.ai.textanalytics.ResolutionKind.
    :vartype resolution_kind: str
    :ivar unit: The weight Unit of measurement. Required. Known values are: "Unspecified",
     "Kilogram", "Gram", "Milligram", "Gallon", "MetricTon", "Ton", "Pound", "Ounce", "Grain",
     "PennyWeight", "LongTonBritish", "ShortTonUS", "ShortHundredWeightUS", "Stone", and "Dram".
     Described in ~azure.ai.textanalytics.WeightUnit.
    :vartype unit: str
    """


__all__: List[str] = [
    "AgeResolution",
    "AreaResolution",
    "BooleanResolution",
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
