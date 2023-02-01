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
class AgeResolution(GeneratedAgeResolution, DictMixin): ...
class AreaResolution(GeneratedAreaResolution, DictMixin): ...
class BooleanResolution(GeneratedBooleanResolution, DictMixin): ...
class CurrencyResolution(GeneratedCurrencyResolution, DictMixin): ...
class DateTimeResolution(GeneratedDateTimeResolution, DictMixin): ...
class InformationResolution(GeneratedInformationResolution, DictMixin): ...
class LengthResolution(GeneratedLengthResolution, DictMixin): ...
class NumberResolution(GeneratedNumberResolution, DictMixin): ...
class NumericRangeResolution(GeneratedNumericRangeResolution, DictMixin): ...
class OrdinalResolution(GeneratedOrdinalResolution, DictMixin): ...
class SpeedResolution(GeneratedSpeedResolution, DictMixin): ...
class TemperatureResolution(GeneratedTemperatureResolution, DictMixin): ...
class TemporalSpanResolution(GeneratedTemporalSpanResolution, DictMixin): ...
class VolumeResolution(GeneratedVolumeResolution, DictMixin): ...
class WeightResolution(GeneratedWeightResolution, DictMixin): ...


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
