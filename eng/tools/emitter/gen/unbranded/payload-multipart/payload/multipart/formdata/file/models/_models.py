# coding=utf-8
# pylint: disable=useless-super-delegation

from typing import Any, Mapping, overload

from ...._utils.model_base import Model as _Model, rest_field
from ...._utils.utils import FileType


class UploadFileArrayRequest(_Model):
    """UploadFileArrayRequest.

    :ivar files: Required.
    :vartype files: list[~payload.multipart._utils.utils.FileType]
    """

    files: list[FileType] = rest_field(
        visibility=["read", "create", "update", "delete", "query"], is_multipart_file_input=True
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        files: list[FileType],
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class UploadFileRequiredFilenameRequest(_Model):
    """UploadFileRequiredFilenameRequest.

    :ivar file: Required.
    :vartype file: ~payload.multipart._utils.utils.FileType
    """

    file: FileType = rest_field(
        visibility=["read", "create", "update", "delete", "query"], is_multipart_file_input=True
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        file: FileType,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class UploadFileSpecificContentTypeRequest(_Model):
    """UploadFileSpecificContentTypeRequest.

    :ivar file: Required.
    :vartype file: ~payload.multipart._utils.utils.FileType
    """

    file: FileType = rest_field(
        visibility=["read", "create", "update", "delete", "query"], is_multipart_file_input=True
    )
    """Required."""

    @overload
    def __init__(
        self,
        *,
        file: FileType,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
