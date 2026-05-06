# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, overload

from .._utils.model_base import Model as _Model, rest_field


class Cat(_Model):
    """Cat.

    :ivar name: Required.
    :vartype name: str
    :ivar meow: Required.
    :vartype meow: bool
    """

    name: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    meow: bool = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        name: str,
        meow: bool,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Dog(_Model):
    """Dog.

    :ivar name: Required.
    :vartype name: str
    :ivar bark: Required.
    :vartype bark: bool
    """

    name: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""
    bark: bool = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        name: str,
        bark: bool,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
