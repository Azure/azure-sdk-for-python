# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, overload

from ..._utils.model_base import Model as _Model, rest_field
from ..._utils.utils import FileType


class AnonymousModelRequest(_Model):
    """AnonymousModelRequest.

    :ivar profile_image: Required.
    :vartype profile_image: ~payload.multipart._utils.utils.FileType
    """

    profile_image: FileType = rest_field(
        name="profileImage", visibility=["read", "create", "update", "delete", "query"], is_multipart_file_input=True
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        profile_image: FileType,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
