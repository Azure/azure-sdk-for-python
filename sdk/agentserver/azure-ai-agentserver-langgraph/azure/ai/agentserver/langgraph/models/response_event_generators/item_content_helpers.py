# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.agentserver.core.models import projects as project_models


class ItemContentHelper:
    """Base helper for building and accumulating a single :class:`ItemContent` object.

    Subclasses specialise the item content type and implement
    :meth:`aggregate_content` to accumulate streamed chunks.
    """

    def __init__(self, content_type: str) -> None:
        """
        :param content_type: The item content type constant (e.g. ``ItemContentType.OUTPUT_TEXT``).
        :type content_type: str
        """
        self.content_type = content_type
        self.has_aggregated_content = False

    def create_item_content(self) -> project_models.ItemContent:
        """Create a bare :class:`ItemContent` with the helper's content type.

        :return: A new :class:`ItemContent` instance.
        :rtype: project_models.ItemContent
        """
        return project_models.ItemContent(
            type=self.content_type,
        )


class InputTextItemContentHelper(ItemContentHelper):
    """Helper for ``input_text`` content parts."""

    def __init__(self) -> None:
        super().__init__(project_models.ItemContentType.INPUT_TEXT)
        self.text = ""

    def create_item_content(self) -> project_models.ItemContent:
        """Return an :class:`ItemContentInputText` with accumulated text.

        :return: Populated input-text content item.
        :rtype: project_models.ItemContent
        """
        return project_models.ItemContentInputText(text=self.text)

    def aggregate_content(self, item: str | dict) -> None:
        """Accumulate a streamed text chunk.

        :param item: Either a plain string or a dict with a ``"text"`` key.
        :type item: str | dict
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
    """Helper for ``output_text`` content parts."""

    def __init__(self) -> None:
        super().__init__(project_models.ItemContentType.OUTPUT_TEXT)
        self.text = ""
        self.annotations: list = []
        self.logprobs: list = []

    def create_item_content(self) -> project_models.ItemContent:
        """Return an :class:`ItemContentOutputText` with accumulated text, annotations, and logprobs.

        :return: Populated output-text content item.
        :rtype: project_models.ItemContent
        """
        return project_models.ItemContentOutputText(
            text=self.text,
            annotations=self.annotations,
            logprobs=self.logprobs,
        )

    def aggregate_content(self, item: str | dict) -> None:
        """Accumulate a streamed text chunk.

        :param item: Either a plain string or a dict with a ``"text"`` key.
        :type item: str | dict
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
