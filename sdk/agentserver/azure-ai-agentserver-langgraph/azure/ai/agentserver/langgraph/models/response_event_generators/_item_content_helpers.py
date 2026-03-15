# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any

from azure.ai.agentserver.core.models import _projects as project_models


class ItemContentHelper:
    """Base helper for building response item content during streaming."""

    def __init__(self, content_type: str):
        """Initialize the content helper.

        :param content_type: The response item content type handled by this helper.
        :type content_type: str
        """
        self.content_type = content_type
        self.has_aggregated_content = False

    def create_item_content(self) -> project_models.ItemContent:
        """Create the current response item content model.

        :return: The current item content model.
        :rtype: project_models.ItemContent
        """
        return project_models.ItemContent(
            type=self.content_type,
        )

    def aggregate_content(self, _item: Any) -> None:
        """Accumulate additional content into the helper state.

        :param _item: The content fragment to aggregate.
        :type _item: Any
        """
        raise NotImplementedError


class InputTextItemContentHelper(ItemContentHelper):
    """Helper for aggregating input-text content parts."""

    def __init__(self):
        """Initialize the input-text content helper."""
        super().__init__(project_models.ItemContentType.INPUT_TEXT)
        self.text = ""

    def create_item_content(self):
        """Create the aggregated input-text content model.

        :return: The aggregated input-text item content.
        :rtype: project_models.ItemContentInputText
        """
        return project_models.ItemContentInputText(text=self.text)

    def aggregate_content(self, item):
        """Accumulate additional input-text content.

        :param item: The content fragment to aggregate.
        :type item: Any
        """
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
    """Helper for aggregating output-text content parts."""

    def __init__(self):
        """Initialize the output-text content helper."""
        super().__init__(project_models.ItemContentType.OUTPUT_TEXT)
        self.text = ""
        self.annotations = []
        self.logprobs = []

    def create_item_content(self):
        """Create the aggregated output-text content model.

        :return: The aggregated output-text item content.
        :rtype: project_models.ItemContentOutputText
        """
        return project_models.ItemContentOutputText(
            text=self.text,
            annotations=self.annotations,
            logprobs=self.logprobs,
        )

    def aggregate_content(self, item):
        """Accumulate additional output-text content.

        :param item: The content fragment to aggregate.
        :type item: Any
        """
        self.has_aggregated_content = True
        if isinstance(item, str):
            self.text += item
            return
        if not isinstance(item, dict):
            return
        text = item.get("text")
        if isinstance(text, str):
            self.text += text
