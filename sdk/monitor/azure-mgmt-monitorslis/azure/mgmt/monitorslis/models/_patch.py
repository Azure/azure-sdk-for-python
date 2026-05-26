# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Iterable, List, Optional, Union

from ._enums import ConditionOperator, SamplingType, ScalarFunction
from ._models import Condition

#: Literal delimiter the SLI resource provider expects between list items for the
#: :attr:`ConditionOperator.IN` / :attr:`ConditionOperator.NOT_IN` operators.
CONDITION_IN_VALUE_SEPARATOR = "^^"

__all__: list[str] = ["CONDITION_IN_VALUE_SEPARATOR"]


def _values_getter(self: Condition) -> List[str]:
    """Return the list of items encoded into ``Condition.value`` for the ``in`` / ``notin`` operators.

    The wire format joins the items with the literal ``^^`` separator. Returns an empty list when
    ``value`` is ``None``.
    """
    raw = self.value
    if raw is None:
        return []
    return raw.split(CONDITION_IN_VALUE_SEPARATOR)


def _values_setter(self: Condition, items: Optional[Iterable[str]]) -> None:
    """Populate ``Condition.value`` by joining ``items`` with the wire ``^^`` separator.

    Passing ``None`` clears ``value``; passing an empty iterable sets ``value`` to an empty string.
    """
    if items is None:
        self.value = None  # type: ignore[assignment]
        return
    self.value = CONDITION_IN_VALUE_SEPARATOR.join(items)


@classmethod  # type: ignore[misc]
def _for_list_operator(
    cls,
    operator: Union[str, ConditionOperator],
    values: Iterable[str],
    *,
    dimension_name: Optional[str] = None,
    scalar_function: Optional[Union[str, ScalarFunction]] = None,
    sampling_type: Optional[Union[str, SamplingType]] = None,
) -> "Condition":
    """Build a :class:`Condition` for a list operator.

    ``operator`` must be :attr:`ConditionOperator.IN` or :attr:`ConditionOperator.NOT_IN`. The
    ``values`` are joined with the literal ``^^`` separator used on the wire. Raises
    :class:`ValueError` if the operator is wrong, ``values`` is empty, or an item contains the
    ``^^`` separator.
    """
    op_value = operator.value if isinstance(operator, ConditionOperator) else operator
    if op_value not in (ConditionOperator.IN.value, ConditionOperator.NOT_IN.value):
        raise ValueError(
            f"operator must be ConditionOperator.IN or ConditionOperator.NOT_IN; got {operator!r}"
        )
    materialized = list(values)
    if not materialized:
        raise ValueError("At least one value is required for list operators.")
    for i, item in enumerate(materialized):
        if item is None or CONDITION_IN_VALUE_SEPARATOR in item:
            raise ValueError(
                f"Value at index {i} contains the reserved {CONDITION_IN_VALUE_SEPARATOR!r} separator."
            )
    return cls(
        operator=operator,
        value=CONDITION_IN_VALUE_SEPARATOR.join(materialized),
        dimension_name=dimension_name,
        scalar_function=scalar_function,
        sampling_type=sampling_type,
    )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    # Attach a list-style accessor on top of the wire ``value`` property and a factory for the
    # ``in`` / ``notin`` operators so callers do not need to manually join values with ``^^``.
    if not isinstance(getattr(Condition, "values", None), property):
        Condition.values = property(_values_getter, _values_setter)  # type: ignore[attr-defined]
    if not hasattr(Condition, "for_list_operator"):
        Condition.for_list_operator = _for_list_operator  # type: ignore[attr-defined]
