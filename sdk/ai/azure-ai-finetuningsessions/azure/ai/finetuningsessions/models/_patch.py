# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Dict, Literal, Mapping, Optional, overload

from .._utils.model_base import Model as _Model, rest_field
from . import _models

MAX_IMAGE_BYTES = 10_000_000
MAX_IMAGES_PER_EXAMPLE = 64
_IMAGE_MAGIC_MATCHERS = {
    "jpeg": lambda data: data.startswith(b"\xff\xd8\xff"),
    "png": lambda data: data.startswith(b"\x89PNG\r\n\x1a\n"),
    "webp": lambda data: (len(data) >= 12 and data.startswith(b"RIFF") and data[8:12] == b"WEBP"),
}


class FromCheckpoint(_Model):
    """Identifies a saved training checkpoint to bootstrap a new session from.

    When passed to :meth:`~azure.ai.finetuningsessions.FineTuningSession.create`,
    the new session's LoRA weights, optimizer state, and scheduler step are all
    initialised from the referenced checkpoint (continual fine-tuning).

    :ivar source_session_id: The ``session_<session_id>`` of the session that saved
        the checkpoint.
    :vartype source_session_id: str
    :ivar checkpoint_id: Name of the checkpoint within the source session.
    :vartype checkpoint_id: str
    """

    source_session_id: str = rest_field()
    """The ``session_<session_id>`` of the session that saved the checkpoint."""

    checkpoint_id: str = rest_field()
    """Name of the checkpoint within the source session."""

    @overload
    def __init__(
        self,
        *,
        source_session_id: str,
        checkpoint_id: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ImageChunk(_Model):
    """Raw image bytes embedded in a model input.

    :ivar data: Encoded image bytes. Required.
    :vartype data: bytes
    :ivar format: Image encoding, such as ``jpeg`` or ``png``. Required.
    :vartype format: str
    :ivar expected_tokens: Number of image placeholder tokens. Required.
    :vartype expected_tokens: int
    """

    type: Literal["image"] = rest_field()
    data: bytes = rest_field()
    format: str = rest_field()
    expected_tokens: int = rest_field()

    @overload
    def __init__(
        self,
        *,
        data: bytes,
        format: str,
        expected_tokens: int,
        type: Literal["image"] = "image",
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("type", "image")
        super().__init__(*args, **kwargs)
        if not isinstance(self.data, bytes):
            raise TypeError("image data must be bytes")
        if len(self.data) > MAX_IMAGE_BYTES:
            raise ValueError(f"image data exceeds the {MAX_IMAGE_BYTES}-byte limit")
        if self.format not in _IMAGE_MAGIC_MATCHERS:
            raise ValueError("image format must be jpeg, png, or webp")
        if not _IMAGE_MAGIC_MATCHERS[self.format](self.data):
            raise ValueError(f"declared image format {self.format!r} does not match the image signature")
        if self.expected_tokens < 1:
            raise ValueError("expected_tokens must be positive")

    @property
    def length(self) -> int:
        return self.expected_tokens


class SampleOperationResult(_models.SampleOperationResult, discriminator="sample"):
    """Sampling result with the tested preview's nested nullable annotations.

    The pinned emitter cannot represent nested nullable tuple arrays. These
    two fields therefore use the supported model override, not generated-file
    rewriting. Wire pairs remain JSON arrays, just as in the Loom preview.
    """

    prompt_logprobs: Optional[list[Optional[float]]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )
    topk_prompt_logprobs: Optional[list[Optional[list[tuple[int, float]]]]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"]
    )

    @overload
    def __init__(
        self,
        *,
        sequences: list[_models.SampledSequence],
        prompt_logprobs: Optional[list[Optional[float]]] = None,
        topk_prompt_logprobs: Optional[list[Optional[list[tuple[int, float]]]]] = None,
        metrics: Optional[dict[str, Any]] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SaveCheckpointRequest(_models.SaveCheckpointRequest):
    """Keep the preview's published ``typing.Dict`` annotation and overload."""

    metrics: Optional[Dict[str, Any]] = rest_field(visibility=["read", "create", "update", "delete", "query"])

    @overload
    def __init__(
        self,
        *,
        path: str,
        step_number: Optional[int] = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ModelInput(_models.ModelInput):
    """Ordered text and image chunks for one model input."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        image_count = sum(
            isinstance(chunk, ImageChunk) or (isinstance(chunk, Mapping) and chunk.get("type") == "image")
            for chunk in self.chunks
        )
        if image_count > MAX_IMAGES_PER_EXAMPLE:
            raise ValueError(f"model input supports at most {MAX_IMAGES_PER_EXAMPLE} images")


__all__: list[str] = [
    "FromCheckpoint",
    "ImageChunk",
    "ModelInput",
    "SampleOperationResult",
    "SaveCheckpointRequest",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
