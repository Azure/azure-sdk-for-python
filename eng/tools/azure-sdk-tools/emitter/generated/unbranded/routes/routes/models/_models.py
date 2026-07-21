# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, overload

from .._utils.model_base import Model as _Model, rest_field


class ExpandParameters(_Model):  # pylint: disable=docstring-keyword-should-match-keyword-only
    """A named model used to verify explode expansion of a model-valued query parameter.

    :ivar field: Required.
    :vartype field: str
    :ivar value: Required.
    :vartype value: str
    """

    field: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    value: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        field: str,
        value: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
