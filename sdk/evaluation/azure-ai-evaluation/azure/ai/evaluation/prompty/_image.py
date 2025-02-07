# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import hashlib
import base64
from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import Final, Mapping, Optional, Union

from httpx import AsyncClient

from azure.ai.evaluation.prompty._exceptions import InvalidInputError


DEFAULT_IMAGE_MIME_TYPE: Final[str] = "image/*"
FILE_EXT_TO_MIME: Final[Mapping[str, str]] = {
    ".apng": "image/apng",
    ".avif": "image/avif",
    ".bmp": "image/bmp",
    ".gif": "image/gif",
    ".heic": "image/heic",
    ".heif": "image/heif",
    ".ico": "image/vnd.microsoft.icon",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".webp": "image/webp",
}


class ImageBase(ABC):
    """This class is used to represent an image."""

    def __init__(self, hash: str, mime_type: Optional[str] = None):
        self._mime_type = mime_type.lower() if mime_type else DEFAULT_IMAGE_MIME_TYPE
        self._hash = hash

    @property
    def hash(self) -> str:
        """Gets the hash that uniquely identifies the image.

        :return: The hash that uniquely identifies the image.
        :rtype: str
        """
        return self._hash

    @property
    def mime_type(self) -> str:
        """Gets the mime type of the image.

        :return: The mime type of the image.
        :rtype: str
        """
        return self._mime_type

    def __str__(self) -> str:
        """Returns the string representation of the image.

        :return: The string representation of the image.
        :rtype: str"""
        return f"Image({self.hash})"

    async def as_base64_str(self) -> str:
        """Returns the base64 representation of the image data. This may make network calls to load the image data.

        :return: The base64 representation of the image data.
        :rtype: str"""
        bytes = await self.as_bytes()
        return base64.b64encode(bytes).decode("utf-8")

    @abstractmethod
    async def as_bytes(self) -> bytes:
        """Returns the bytes of the image. This may make network calls to load image data.

        :return: The bytes of the image.
        :rtype: bytes"""
        ...

    @abstractmethod
    def as_url(self) -> str:
        """Returns the URL of the image. This may return a data URL or a URL to the image source.

        :return: The URL of the image.
        :rtype: str"""
        ...


class Base64Image(ImageBase):
    """An image from a base64 data URL string."""

    def __init__(self, base64_data: str, mime_type: str):
        self._bytes = base64.b64decode(base64_data)
        super().__init__(hashlib.sha1(self._bytes).hexdigest(), mime_type)

    @staticmethod
    def from_file(file_path: Union[str, PathLike], mime_type: Optional[str] = None) -> "Base64Image":
        path = Path(file_path).resolve()
        bytes = path.read_bytes()
        base_64_str = base64.b64encode(bytes).decode("utf-8")

        if not mime_type:
            mime_type = FILE_EXT_TO_MIME.get(path.suffix, DEFAULT_IMAGE_MIME_TYPE)

        return Base64Image(base_64_str, mime_type)

    async def as_bytes(self) -> bytes:
        return self._bytes

    def as_url(self) -> str:
        base_64_str = base64.b64encode(self._bytes).decode("utf-8")
        return f"data:{self.mime_type};base64,{base_64_str}"


class FileImage(ImageBase):
    """An image from a file path."""

    def __init__(self, file_path: Union[str, PathLike], mime_type: Optional[str] = None):
        path = Path(file_path).resolve()
        self._bytes = path.read_bytes()

        if not mime_type:
            mime_type = FILE_EXT_TO_MIME.get(path.suffix, DEFAULT_IMAGE_MIME_TYPE)

        super().__init__(hashlib.sha1(self._bytes).hexdigest(), mime_type)

    async def as_bytes(self) -> bytes:
        return self._bytes

    def as_url(self) -> str:
        base_64_str = base64.b64encode(self._bytes).decode("utf-8")
        return f"data:{self.mime_type};base64,{base_64_str}"


class LazyUrlImage(ImageBase):
    """A lazy loading image from a URL."""

    def __init__(self, url: str, mime_type: Optional[str] = None):
        # To avoid making network calls in the constructor, we use the URL itself as the hash,
        # and use a default of image/* for the mime type. Once the image data is loaded, the
        # mime type will be updated.
        self._source_url = url
        self._bytes: Optional[bytes] = None
        super().__init__(hashlib.sha1(url.encode("utf-8")).hexdigest(), mime_type)

    async def as_bytes(self) -> bytes:
        if self._bytes is not None:
            return self._bytes

        try:
            async with AsyncClient() as client:
                response = await client.get(self._source_url)
                if response.status_code != 200:
                    raise InvalidInputError(
                        f"HTTP {response.status_code} while retrieving image from URL: '{self._source_url}'"
                    )
                self._bytes = response.content
                self._mime_type = response.headers.get("Content-Type", DEFAULT_IMAGE_MIME_TYPE)
                return self._bytes
        except Exception as e:
            raise InvalidInputError(f"Failed to retrieve image from URL: '{self._source_url}'. Error: {str(e)}") from e

    def as_url(self) -> str:
        return self._source_url
