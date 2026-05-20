# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, Optional, overload

from .._utils.model_base import Model as _Model, rest_field


class TestModel(_Model):
    """TestModel.

    :ivar prop: Required.
    :vartype prop: str
    :ivar changed_prop:
    :vartype changed_prop: str
    """

    prop: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    changed_prop: Optional[str] = rest_field(
        name="changedProp", visibility=["read", "create", "update", "delete", "query"]
    )

    @overload
    def __init__(
        self,
        *,
        prop: str,
        changed_prop: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
