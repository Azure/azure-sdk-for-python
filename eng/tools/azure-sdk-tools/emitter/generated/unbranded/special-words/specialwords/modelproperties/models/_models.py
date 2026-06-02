# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, overload

from ..._utils.model_base import Model as _Model, rest_field

List = list


class DictMethods(_Model):
    """DictMethods.

    :ivar keys_property: Required.
    :vartype keys_property: str
    :ivar items_property: Required.
    :vartype items_property: str
    :ivar values_property: Required.
    :vartype values_property: str
    :ivar popitem_property: Required.
    :vartype popitem_property: str
    :ivar clear_property: Required.
    :vartype clear_property: str
    :ivar update_property: Required.
    :vartype update_property: str
    :ivar setdefault_property: Required.
    :vartype setdefault_property: str
    :ivar pop_property: Required.
    :vartype pop_property: str
    :ivar get_property: Required.
    :vartype get_property: str
    :ivar copy_property: Required.
    :vartype copy_property: str
    """

    keys_property: str = rest_field(
        name="keys", visibility=["read", "create", "update", "delete", "query"], original_tsp_name="keys"
    )
    """Required."""
    items_property: str = rest_field(
        name="items", visibility=["read", "create", "update", "delete", "query"], original_tsp_name="items"
    )
    """Required."""
    values_property: str = rest_field(
        name="values", visibility=["read", "create", "update", "delete", "query"], original_tsp_name="values"
    )
    """Required."""
    popitem_property: str = rest_field(
        name="popitem", visibility=["read", "create", "update", "delete", "query"], original_tsp_name="popitem"
    )
    """Required."""
    clear_property: str = rest_field(
        name="clear", visibility=["read", "create", "update", "delete", "query"], original_tsp_name="clear"
    )
    """Required."""
    update_property: str = rest_field(
        name="update", visibility=["read", "create", "update", "delete", "query"], original_tsp_name="update"
    )
    """Required."""
    setdefault_property: str = rest_field(
        name="setdefault", visibility=["read", "create", "update", "delete", "query"], original_tsp_name="setdefault"
    )
    """Required."""
    pop_property: str = rest_field(
        name="pop", visibility=["read", "create", "update", "delete", "query"], original_tsp_name="pop"
    )
    """Required."""
    get_property: str = rest_field(
        name="get", visibility=["read", "create", "update", "delete", "query"], original_tsp_name="get"
    )
    """Required."""
    copy_property: str = rest_field(
        name="copy", visibility=["read", "create", "update", "delete", "query"], original_tsp_name="copy"
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        keys_property: str,
        items_property: str,
        values_property: str,
        popitem_property: str,
        clear_property: str,
        update_property: str,
        setdefault_property: str,
        pop_property: str,
        get_property: str,
        copy_property: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelWithList(_Model):
    """ModelWithList.

    :ivar list: Required.
    :vartype list: str
    """

    list: str = rest_field(visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        list: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SameAsModel(_Model):
    """SameAsModel.

    :ivar same_as_model: Required.
    :vartype same_as_model: str
    """

    same_as_model: str = rest_field(name="SameAsModel", visibility=["read", "create", "update", "delete", "query"])
    """Required."""

    @overload
    def __init__(
        self,
        *,
        same_as_model: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
