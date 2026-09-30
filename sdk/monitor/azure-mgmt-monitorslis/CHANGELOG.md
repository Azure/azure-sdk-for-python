# Release History

## 1.0.0b2 (2026-05-23)

### Features Added

  - Enum `SamplingType` added member `AVERAGE`
  - Enum `SamplingType` added member `COUNT`

### Breaking Changes

  - Enum value `SamplingType.AVG` was removed.
  - Enum values `SamplingType.MAX`, `SamplingType.MIN`, and `SamplingType.SUM` changed wire values to `"Max"`, `"Min"`, and `"Sum"` (previously `"max"`, `"min"`, and `"sum"`).
  - Enum `ConditionOperator` changed wire values: `==` to `eq`, `!=` to `ne`, `>` to `gt`, `>=` to `gte`, `<` to `lt`, `<=` to `lte`, `@in` to `in`, `!in` to `notin`, `!contains` to `notcontains`, and `!startswith` to `notstartswith`.
  - Enum `WindowUptimeCriteriaComparator` changed wire values: `>` to `gt`, `>=` to `gte`, `<` to `lt`, and `<=` to `lte`.
  - Minimum Python version raised to 3.10 (previously 3.9); Python 3.9 is no longer supported.

## 1.0.0b1 (2026-04-27)

### Other Changes

  - Initial version