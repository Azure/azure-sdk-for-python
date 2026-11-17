import pytest

from azure.ai.finetuningsessions.models import CreateSessionRequest, LoRAConfig


def test_lora_config_requires_rank():
    with pytest.raises(ValueError, match="lora_config.rank is required"):
        LoRAConfig()


def test_create_session_request_requires_lora_config():
    with pytest.raises(ValueError, match="lora_config is required"):
        CreateSessionRequest(type="training", base_model="Qwen/Qwen3-32B")


def test_multimodal_lora_placement_serializes():
    config = LoRAConfig(
        rank=32,
        alpha=32.0,
        seed=42,
        freeze_vision_tower=False,
        freeze_multi_modal_projector=True,
    )

    request = CreateSessionRequest(
        type="training",
        base_model="Qwen/Qwen3-32B",
        lora_config=config,
    )
    serialized = request.as_dict()["lora_config"]
    assert serialized["rank"] == 32
    assert serialized["freeze_vision_tower"] is False
    assert serialized["freeze_multi_modal_projector"] is True
