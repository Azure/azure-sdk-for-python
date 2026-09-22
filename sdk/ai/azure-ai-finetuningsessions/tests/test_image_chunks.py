import json

import pytest

from azure.ai.finetuningsessions._patch import _SdkJSONEncoder, _estimate_bytes_count
from azure.ai.finetuningsessions.models import (
    Datum,
    ImageChunk,
    LossFnInputs,
    ModelInput,
    ModelInputChunk,
    SampleRequest,
    SamplingParams,
    TensorData,
)
from azure.ai.finetuningsessions.models import _patch as model_patch


def test_image_chunk_serializes_in_model_input() -> None:
    model_input = ModelInput(
        chunks=[
            ModelInputChunk(tokens=[1, 2]),
            ImageChunk(data=b"\xff\xd8\xffjpeg", format="jpeg", expected_tokens=12),
            ModelInputChunk(tokens=[3]),
        ]
    )

    payload = json.loads(json.dumps(model_input, cls=_SdkJSONEncoder))

    assert payload["chunks"][1] == {
        "type": "image",
        "data": "/9j/anBlZw==",
        "format": "jpeg",
        "expected_tokens": 12,
    }

    request = SampleRequest(
        num_samples=1,
        prompt=model_input,
        sampling_params=SamplingParams(max_tokens=8),
    )
    request_payload = json.loads(
        json.dumps(request, cls=_SdkJSONEncoder, exclude_readonly=True)
    )
    assert request_payload["prompt"]["chunks"][1]["type"] == "image"


def test_image_chunk_request_size_uses_encoded_image_bytes() -> None:
    empty = TensorData(data=[])
    datum = Datum(
        model_input=ModelInput(
            chunks=[
                ModelInputChunk(tokens=[1, 2]),
                ImageChunk(
                    data=b"\xff\xd8\xffjpeg", format="jpeg", expected_tokens=12
                ),
            ]
        ),
        loss_fn_inputs=LossFnInputs(
            target_tokens=empty,
            weights=empty,
            advantages=empty,
            logprobs=empty,
        ),
    )

    assert _estimate_bytes_count(datum) == 32


def test_model_input_accepts_64_images_and_rejects_65() -> None:
    images = [
        ImageChunk(data=b"\xff\xd8\xffjpeg", format="jpeg", expected_tokens=1)
        for _ in range(64)
    ]

    assert len(ModelInput(chunks=images).chunks) == 64
    with pytest.raises(ValueError, match="at most 64 images"):
        ModelInput(chunks=images + [images[0]])


def test_image_chunk_rejects_unsafe_metadata_and_size(monkeypatch) -> None:
    with pytest.raises(
        ValueError,
        match="declared image format 'jpeg' does not match the image signature",
    ):
        ImageChunk(data=b"not-jpeg", format="jpeg", expected_tokens=1)
    with pytest.raises(ValueError, match="must be positive"):
        ImageChunk(data=b"\xff\xd8\xffjpeg", format="jpeg", expected_tokens=0)
    assert ImageChunk(
        data=b"\xff\xd8\xffjpeg", format="jpeg", expected_tokens=4097
    ).expected_tokens == 4097

    monkeypatch.setattr(model_patch, "MAX_IMAGE_BYTES", 4)
    with pytest.raises(ValueError, match="exceeds the 4-byte limit"):
        ImageChunk(data=b"\xff\xd8\xff12", format="jpeg", expected_tokens=1)