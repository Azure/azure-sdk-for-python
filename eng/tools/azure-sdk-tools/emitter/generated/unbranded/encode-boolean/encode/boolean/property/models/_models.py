# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, overload

from ..._utils.model_base import Model as _Model, rest_field


class BoolAsStringProperty(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """BoolAsStringProperty.

    :ivar value: Required.
    :vartype value: bool
    """

    value: bool = rest_field(visibility=["read", "create", "update", "delete", "query"], format="str")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        value: bool,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
