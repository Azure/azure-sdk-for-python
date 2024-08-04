# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DataIndex embedding model helpers."""
import re
from typing import Optional

OPEN_AI_PROTOCOL_TEMPLATE = "azure_open_ai://deployment/{}/model/{}"
OPEN_AI_PROTOCOL_REGEX_PATTERN = OPEN_AI_PROTOCOL_TEMPLATE.format(".*", ".*")
OPEN_AI_SHORT_FORM_PROTOCOL_TEMPLATE = "azure_open_ai://deployments?/{}"
OPEN_AI_PROTOCOL_REGEX_PATTERN = OPEN_AI_SHORT_FORM_PROTOCOL_TEMPLATE.format(".*")

HUGGINGFACE_PROTOCOL_TEMPLATE = "hugging_face://model/{}"
HUGGINGFACE_PROTOCOL_REGEX_PATTERN = HUGGINGFACE_PROTOCOL_TEMPLATE.format(".*")


def build_model_protocol(model: Optional[str] = None):
    if not model or re.match(OPEN_AI_PROTOCOL_REGEX_PATTERN, model, re.IGNORECASE):
        return model
    if re.match(OPEN_AI_SHORT_FORM_PROTOCOL_TEMPLATE, model, re.IGNORECASE):
        return model
    if re.match(HUGGINGFACE_PROTOCOL_REGEX_PATTERN, model, re.IGNORECASE):
        return model

    return OPEN_AI_PROTOCOL_TEMPLATE.format(model, model)
