# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.agentserver.core.models import projects as project_models


class ItemContentHelper:
    def __init__(self, content_type: str):
        self.content_type = content_type
        self.has_aggregated_content = False

    def create_item_content(self) -> project_models.ItemContent:
        return project_models.ItemContent(
            type=self.content_type,
        )


class InputTextItemContentHelper(ItemContentHelper):
    def __init__(self):
        super().__init__(project_models.ItemContentType.INPUT_TEXT)
        self.text = ""

    def create_item_content(self):
        return project_models.ItemContentInputText(text=self.text)

    def aggregate_content(self, item):
        self.has_aggregated_content = True
        if isinstance(item, str):
            self.text += item
            return
        if not isinstance(item, dict):
            return
        text = item.get("text")
        if isinstance(text, str):
            self.text += text


class OutputTextItemContentHelper(ItemContentHelper):
    def __init__(self):
        super().__init__(project_models.ItemContentType.OUTPUT_TEXT)
        self.text = ""
        self.annotations = []
        self.logprobs = []

    def create_item_content(self):
        return project_models.ItemContentOutputText(
            text=self.text,
            annotations=self.annotations,
            logprobs=self.logprobs,
        )

    def aggregate_content(self, item):
        self.has_aggregated_content = True
        if isinstance(item, str):
            self.text += item
            return
        if not isinstance(item, dict):
            return
        text = item.get("text")
        if isinstance(text, str):
            self.text += text
