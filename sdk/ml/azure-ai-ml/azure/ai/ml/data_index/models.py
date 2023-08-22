# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re

OPEN_AI_PROTOCOL_TEMPLATE = "azure_open_ai://deployment/{}/model/{}"
OPEN_AI_PROTOCOL_REGEX_PATTERN = OPEN_AI_PROTOCOL_TEMPLATE.format(".*", ".*")
OPEN_AI_SHORT_FORM_PROTOCOL_TEMPLATE = "azure_open_ai://deployments?/{}"
OPEN_AI_PROTOCOL_REGEX_PATTERN = OPEN_AI_SHORT_FORM_PROTOCOL_TEMPLATE.format(".*")

HUGGINGFACE_PROTOCOL_TEMPLATE = "hugging_face://model/{}"
HUGGINGFACE_PROTOCOL_REGEX_PATTERN = HUGGINGFACE_PROTOCOL_TEMPLATE.format(".*")


def build_model_protocol(s: str = None):
    if not s or re.match(OPEN_AI_PROTOCOL_REGEX_PATTERN, s, re.IGNORECASE):
        return s
    elif re.match(OPEN_AI_SHORT_FORM_PROTOCOL_TEMPLATE, s, re.IGNORECASE):
        return s
    elif re.match(HUGGINGFACE_PROTOCOL_REGEX_PATTERN, s, re.IGNORECASE):
        return s
    else:
        return OPEN_AI_PROTOCOL_TEMPLATE.format(s, s)
