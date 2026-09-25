# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Dict, Literal, Mapping, Optional, Union, overload

from .. import _unions
from .._utils.model_base import Model as _Model, rest_field
from . import _models
from ._enums import SessionType, TrainingType

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

    # A concrete implementation is required for the two preview overloads.
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-parent-delegation
        super().__init__(*args, **kwargs)


class ImageChunk(_models.ImageChunk, discriminator="image"):
    """Raw image bytes embedded in a model input.

    :ivar data: Encoded image bytes. Required.
    :vartype data: bytes
    :ivar format: Image encoding, such as ``jpeg`` or ``png``. Required.
    :vartype format: str
    :ivar expected_tokens: Number of image placeholder tokens. Required.
    :vartype expected_tokens: int
    """

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
        super().__init__(*args, **kwargs)
        # The generated variant supplies the discriminator for both forms.
        # Preserve validation of an explicitly incorrect original marker.
        values = args[0] if args else kwargs
        if values.get("type", "image") != "image":
            raise ValueError("image type must be 'image'")
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


class LoRAConfig(_models.LoRAConfig):
    """Adapter settings with an explicit rank; no model-independent default is assumed.

    :ivar rank: Required number of LoRA rank dimensions.
    :vartype rank: int
    """

    @overload
    def __init__(
        self,
        *,
        rank: int,
        alpha: Optional[float] = None,
        seed: Optional[int] = None,
        freeze_vision_tower: Optional[bool] = None,
        freeze_multi_modal_projector: Optional[bool] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.rank is None:
            raise ValueError("lora_config.rank is required; pass LoRAConfig(rank=<integer>)")


class CreateSessionRequest(_models.CreateSessionRequest):
    """Session creation with the explicit adapter configuration required by the service.

    :ivar lora_config: Required adapter configuration, including rank.
    :vartype lora_config: ~azure.ai.finetuningsessions.models.LoRAConfig
    """

    lora_config: LoRAConfig = rest_field(visibility=["read", "create", "update", "delete", "query"])

    @overload
    def __init__(
        self,
        *,
        type: Union[str, SessionType],
        base_model: str,
        lora_config: LoRAConfig,
        user_metadata: Optional[dict[str, Any]] = None,
        ejectable: Optional[bool] = None,
        training_type: Optional[Union[str, TrainingType]] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.lora_config is None:
            raise ValueError("lora_config is required; pass LoRAConfig(rank=<integer>)")
        # Model conversion preserves a mapping when construction fails. Validate
        # that fallback rather than sending an invalid nested configuration.
        if isinstance(self.lora_config, Mapping) and self.lora_config.get("rank") is None:
            raise ValueError("lora_config.rank is required; pass LoRAConfig(rank=<integer>)")


class SamplingParams(_models.SamplingParams):
    """Token generation settings, including an optional structured-output format.

    :ivar response_format: Response format passed to compatible sampling providers.
    :vartype response_format: dict[str, typing.Any] or None
    """

    response_format: Optional[Dict[str, Any]] = rest_field(visibility=["read", "create", "update", "delete", "query"])

    @overload
    def __init__(
        self,
        *,
        max_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
        seed: Optional[int] = None,
        stop_criteria: Optional[_unions.StopCriteria] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class SampleOperationResult(_models.SampleOperationResult, discriminator="sample"):
    """Sampling result with the tested preview's nested nullable annotations.

    The pinned emitter cannot represent nested nullable tuple arrays. These
    two fields therefore use the supported model override, not generated-file
    rewriting. Wire pairs remain JSON arrays, just as in the Loom preview.
    """

    # The emitter drops nested nullability. These intentional mutable-field
    # replacements preserve the published type, verified by round-trip tests.
    prompt_logprobs: Optional[list[Optional[float]]] = rest_field(  # type: ignore[assignment]  # pyright: ignore[reportIncompatibleVariableOverride]
        visibility=["read", "create", "update", "delete", "query"]
    )
    topk_prompt_logprobs: Optional[list[Optional[list[tuple[int, float]]]]] = rest_field(  # type: ignore[assignment]  # pyright: ignore[reportIncompatibleVariableOverride]
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


# Preferred descriptive spelling; retain the existing public name and class
# identity for consumers, discriminator dispatch, and isinstance checks.
SamplingOperationResult = SampleOperationResult


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

    @overload
    def __init__(self, *, chunks: list[_models.InputChunk]) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        chunks = []
        for chunk in tuple(self.chunks):
            if not isinstance(chunk, ImageChunk) and isinstance(chunk, Mapping) and chunk.get("type") == "image":
                # Generated deserialization can retain a mapping on failure;
                # do not let that fallback bypass existing image validation.
                chunk = ImageChunk(chunk)
            elif isinstance(chunk, Mapping) and "type" not in chunk and "tokens" in chunk:
                # Keep existing token-only Python mappings usable. Explicit
                # unknown discriminators remain untouched for extensibility.
                chunk = _models.ModelInputChunk(chunk)
            chunks.append(chunk)
        self.chunks = chunks
        image_count = sum(isinstance(chunk, ImageChunk) for chunk in self.chunks)
        if image_count > MAX_IMAGES_PER_EXAMPLE:
            raise ValueError(f"model input supports at most {MAX_IMAGES_PER_EXAMPLE} images")


__all__: list[str] = [
    "FromCheckpoint",
    "ImageChunk",
    "LoRAConfig",
    "CreateSessionRequest",
    "SamplingParams",
    "ModelInput",
    "SampleOperationResult",
    "SamplingOperationResult",
    "SaveCheckpointRequest",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
