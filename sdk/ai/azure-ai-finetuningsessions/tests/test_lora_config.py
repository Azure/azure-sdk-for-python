from azure.ai.finetuningsessions.models import LoRAConfig


def test_multimodal_lora_placement_serializes():
    config = LoRAConfig(
        rank=32,
        alpha=32.0,
        seed=42,
        freeze_vision_tower=False,
        freeze_multi_modal_projector=True,
    )

    serialized = config.as_dict()
    assert serialized["freeze_vision_tower"] is False
    assert serialized["freeze_multi_modal_projector"] is True
